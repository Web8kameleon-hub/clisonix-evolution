// Industrial DDoS & Enhanced Network Defense middleware for Express
// - Token bucket per IP
// - Adaptive per-endpoint limiter
// - Moving-average + entropy anomaly detection
// - Blocklist with TTL (in-memory or Redis if REDIS_URL provided)
// - Telemetry to SignalHub (HTTP POST or Redis Pub/Sub)
// - Optional headers hardening
// No mock, production-ready.

import type { Request, Response, NextFunction } from "express";
import crypto from "crypto";
import os from "os";
import fetch from "node-fetch";
import { createClient, RedisClientType } from "redis";

// -----------------------------
// Config
// -----------------------------
const NODE_ID = process.env.INSTANCE_ID || os.hostname();
const ENV = process.env.NODE_ENV || "production";

const REDIS_URL = process.env.REDIS_URL || "";
const SIGNAL_HTTP = process.env.SIGNAL_HTTP || ""; // e.g. http://localhost:8000/signals/ingest
const SIGNAL_REDIS_CHANNEL = process.env.SIGNAL_REDIS_CHANNEL || "signals:security";

const TRUST_PROXY =
  (process.env.TRUST_PROXY || "true").toLowerCase() === "true";
const FIREWALL_WHITELIST_CIDRS = (
  process.env.DDOS_WHITELIST_CIDRS ||
  "127.0.0.1/32,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,::1/128"
)
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);
const FIREWALL_BLACKLIST_CIDRS = (process.env.DDOS_BLACKLIST_CIDRS || "")
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);
const STRICT_PATH_PREFIXES = (
  process.env.DDOS_STRICT_PATHS ||
  "/auth,/login,/api/auth,/defense/handshake,/defense/seal"
)
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);
const STATIC_PATH_PREFIXES = (
  process.env.DDOS_STATIC_PATHS || "/static,/assets"
)
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);

const MAX_RPS_DEFAULT = Number(process.env.DDOS_MAX_RPS || 60); // per IP baseline
const MAX_RPS_STRICT = Number(process.env.DDOS_MAX_RPS_STRICT || 15);
const MAX_RPS_STATIC = Number(process.env.DDOS_MAX_RPS_STATIC || 150);
const BUCKET_REFILL_PER_SEC = Number(process.env.DDOS_BUCKET_REFILL || 60);
const BUCKET_CAPACITY = Number(process.env.DDOS_BUCKET_CAP || 120);
const BLOCK_TTL_SEC = Number(process.env.DDOS_BLOCK_TTL || 1800); // 30min
const GREYLIST_TTL_SEC = Number(process.env.DDOS_GREYLIST_SEC || 900);
const TARPIT_MS = Number(process.env.DDOS_TARPIT_MS || 400);
const ENTROPY_THRESHOLD = Number(process.env.DDOS_ENTROPY || 3.8); // lower entropy -> more uniform -> possible flood
const MOVAVG_WINDOW_SEC = Number(process.env.DDOS_MOVAVG_WINDOW || 30);
const BLOCKED_PATH_PATTERNS = [
  /\.env/i,
  /\.git/i,
  /wp-admin/i,
  /phpmyadmin/i,
  /server-status/i,
  /composer\.(json|lock)/i,
];
const DISALLOWED_METHODS = new Set(["TRACE", "TRACK", "CONNECT"]);

// Adaptive caps per endpoint (override default RPS)
const ENDPOINT_CAP: Record<string, number> = {
  "/api/uploads/eeg/process": 12,
  "/api/uploads/audio/process": 20,
  "/billing/stripe/payment-intent": 8,
  "/billing/paypal/order": 6,
};

// -----------------------------
// Redis (optional)
// -----------------------------
let redis: RedisClientType | null = null;
const hasRedis = Boolean(REDIS_URL);

async function initRedis() {
  if (!hasRedis) return;
  redis = createClient({ url: REDIS_URL });
  redis.on("error", (e) => console.error("[ddos] Redis error:", e));
  await redis.connect();
  console.log("[ddos] Redis connected");
}

void initRedis();

// -----------------------------
// In-memory state (falls back when no Redis)
// -----------------------------
type Bucket = { tokens: number; lastRefill: number };
const buckets = new Map<string, Bucket>();
const blocklist = new Map<string, number>(); // ip -> unblockEpochMs
const greylist = new Map<string, number>(); // ip -> slowdown window
const ipMovAvg = new Map<string, { hits: number[]; last: number }>(); // timestamps (sec)
const ipPaths = new Map<string, Map<string, number>>(); // for entropy calc
const logs: Array<{ ts: number; ip: string; event: string; meta?: any }> = [];

function nowSec() { return Math.floor(Date.now() / 1000); }
function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// -----------------------------
// Utilities
// -----------------------------
function entropy(counts: number[]): number {
  const total = counts.reduce((a, b) => a + b, 0) || 1;
  let H = 0;
  for (const c of counts) {
    if (c <= 0) continue;
    const p = c / total;
    H += -p * Math.log2(p);
  }
  return H;
}

function endpointKey(path: string): string {
  // normalize dynamic segments rudimentarily
  return path.replace(/[0-9a-f]{8,}/gi, ":id");
}

function normalizeIp(raw: string | undefined | null): string {
  const value = (raw || "").trim();
  return value.startsWith("::ffff:") ? value.slice(7) : value;
}

function ipv4ToNumber(ip: string): number | null {
  const parts = normalizeIp(ip).split(".");
  if (parts.length !== 4) return null;
  const octets = parts.map((part) => Number(part));
  if (octets.some((part) => !Number.isInteger(part) || part < 0 || part > 255))
    return null;
  return (
    (((octets[0] * 256 + octets[1]) * 256 + octets[2]) * 256 + octets[3]) >>> 0
  );
}

function cidrMatches(ip: string, cidr: string): boolean {
  const normalizedIp = normalizeIp(ip);
  if (cidr === "::1/128") {
    return normalizedIp === "::1" || normalizedIp === "127.0.0.1";
  }

  const [base, bitsRaw] = cidr.split("/");
  const ipNum = ipv4ToNumber(normalizedIp);
  const baseNum = ipv4ToNumber(base);

  if (ipNum === null || baseNum === null) {
    return normalizedIp === normalizeIp(base);
  }

  const bits = Number(bitsRaw || "32");
  const mask = bits === 0 ? 0 : (0xffffffff << (32 - bits)) >>> 0;
  return (ipNum & mask) === (baseNum & mask);
}

function ipInCidrs(ip: string, cidrs: string[]): boolean {
  return cidrs.some((cidr) => cidrMatches(ip, cidr));
}

function getClientIp(req: Request): string {
  const remoteIp = normalizeIp(req.socket.remoteAddress || "unknown");
  const forwarded = (req.headers["x-forwarded-for"] as string | undefined)
    ?.split(",")[0]
    ?.trim();

  if (
    TRUST_PROXY &&
    forwarded &&
    ipInCidrs(remoteIp, FIREWALL_WHITELIST_CIDRS)
  ) {
    return normalizeIp(forwarded);
  }

  return remoteIp;
}

function pathClassFor(path: string): "strict" | "static" | "default" {
  if (
    STRICT_PATH_PREFIXES.some(
      (prefix) => path === prefix || path.startsWith(`${prefix}/`),
    )
  ) {
    return "strict";
  }
  if (
    STATIC_PATH_PREFIXES.some(
      (prefix) => path === prefix || path.startsWith(`${prefix}/`),
    )
  ) {
    return "static";
  }
  return "default";
}

function capForEndpoint(path: string): number {
  const key = endpointKey(path);
  const pathClass = pathClassFor(path);

  if (ENDPOINT_CAP[key] !== undefined) return ENDPOINT_CAP[key];
  if (pathClass === "strict") return MAX_RPS_STRICT;
  if (pathClass === "static") return MAX_RPS_STATIC;
  return MAX_RPS_DEFAULT;
}

function recordLog(ip: string, event: string, meta?: any) {
  const entry = { ts: Date.now(), ip, event, meta };
  logs.push(entry);
  if (logs.length > 5000) logs.shift();
  // fire-and-forget signal
  reportSecuritySignal(event, { ip, ...meta }).catch(() => void 0);
}

async function reportSecuritySignal(event: string, payload: any) {
  // HTTP sink
  if (SIGNAL_HTTP) {
    try {
      await fetch(SIGNAL_HTTP, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          security: {
            event,
            node: NODE_ID,
            env: ENV,
            ts: new Date().toISOString(),
            ...payload,
          },
        }),
        timeout: 1000,
      } as any);
    } catch {}
  }
  // Redis Pub/Sub sink
  if (redis && SIGNAL_REDIS_CHANNEL) {
    try {
      await redis.publish(
        SIGNAL_REDIS_CHANNEL,
        JSON.stringify({
          security: {
            event,
            node: NODE_ID,
            env: ENV,
            ts: new Date().toISOString(),
            ...payload,
          },
        })
      );
    } catch {}
  }
}

function isBlocked(ip: string): boolean {
  const until = blocklist.get(ip);
  if (!until) return false;
  if (Date.now() > until) {
    blocklist.delete(ip);
    return false;
  }
  return true;
}

function isGreylisted(ip: string): boolean {
  const until = greylist.get(ip);
  if (!until) return false;
  if (Date.now() > until) {
    greylist.delete(ip);
    return false;
  }
  return true;
}

function blockIP(ip: string, reason: string, ttlSec = BLOCK_TTL_SEC) {
  blocklist.set(ip, Date.now() + ttlSec * 1000);
  recordLog(ip, "ip_blocked", { reason, ttlSec });
}

function greylistIP(ip: string, reason: string, ttlSec = GREYLIST_TTL_SEC) {
  greylist.set(ip, Date.now() + ttlSec * 1000);
  recordLog(ip, "ip_greylisted", { reason, ttlSec });
}

function clearBlocks() {
  blocklist.clear();
  greylist.clear();
  recordLog("-", "blocklist_cleared");
}

function refillBucket(b: Bucket) {
  const now = Date.now();
  const deltaSec = (now - b.lastRefill) / 1000;
  const refill = Math.floor(deltaSec * BUCKET_REFILL_PER_SEC);
  if (refill > 0) {
    b.tokens = Math.min(BUCKET_CAPACITY, b.tokens + refill);
    b.lastRefill = now;
  }
}

function takeToken(ip: string): boolean {
  let b = buckets.get(ip);
  if (!b) {
    b = { tokens: BUCKET_CAPACITY, lastRefill: Date.now() };
    buckets.set(ip, b);
  }
  refillBucket(b);
  if (b.tokens > 0) {
    b.tokens -= 1;
    return true;
  }
  return false;
}

function updateMovAvg(ip: string) {
  const t = nowSec();
  let m = ipMovAvg.get(ip);
  if (!m) m = { hits: [], last: t };
  m.hits.push(t);
  // keep only last MOVAVG_WINDOW_SEC seconds
  const minT = t - MOVAVG_WINDOW_SEC;
  m.hits = m.hits.filter((x) => x >= minT);
  m.last = t;
  ipMovAvg.set(ip, m);
  return m.hits.length / MOVAVG_WINDOW_SEC; // approx RPS
}

function updatePathDist(ip: string, path: string) {
  const key = endpointKey(path);
  let m = ipPaths.get(ip);
  if (!m) m = new Map<string, number>();
  m.set(key, (m.get(key) || 0) + 1);
  ipPaths.set(ip, m);
  // compute entropy on last window snapshot
  const counts = Array.from(m.values());
  return entropy(counts);
}

// -----------------------------
// Main middleware
// -----------------------------
export async function ddosGuard(req: Request, res: Response, next: NextFunction) {
  try {
    const ip = getClientIp(req);
    const path = req.path || req.url || "/";
    const method = req.method.toUpperCase();

    if (DISALLOWED_METHODS.has(method)) {
      recordLog(ip, "blocked_method", { method, path });
      res.status(405).json({ error: "method_not_allowed" });
      return;
    }

    if (
      FIREWALL_BLACKLIST_CIDRS.length &&
      ipInCidrs(ip, FIREWALL_BLACKLIST_CIDRS)
    ) {
      recordLog(ip, "blacklist_block", { path, method });
      res.status(403).json({ error: "blocked", reason: "blacklist" });
      return;
    }

    if (BLOCKED_PATH_PATTERNS.some((pattern) => pattern.test(path))) {
      recordLog(ip, "probe_blocked", { path, method });
      blockIP(ip, "probe_detected", BLOCK_TTL_SEC);
      res.status(403).json({ error: "probe_blocked" });
      return;
    }

    // quick block check
    if (isBlocked(ip)) {
      res
        .status(403)
        .json({ error: "blocked", reason: "ddos_en", node: NODE_ID });
      return;
    }

    if (isGreylisted(ip)) {
      await sleep(TARPIT_MS);
    }

    // token bucket per IP
    if (!takeToken(ip)) {
      recordLog(ip, "rate_drop_bucket", { path, method });
      blockIP(ip, "bucket_exhausted", 60);
      res.status(429).json({ error: "too_many_requests" });
      return;
    }

    // adaptive endpoint cap (rough approx via moving average)
    const rps = updateMovAvg(ip);
    const cap = capForEndpoint(path);
    if (rps > cap) {
      recordLog(ip, "rate_exceeded_endpoint_cap", {
        cap,
        rps: Number(rps.toFixed(2)),
        path,
        method,
      });
      greylistIP(ip, "endpoint_cap_exceeded", GREYLIST_TTL_SEC);
      await sleep(TARPIT_MS);
      res.status(429).json({ error: "endpoint_rate_limited" });
      return;
    }

    // entropy check (very low entropy -> uniform flood)
    const H = updatePathDist(ip, path);
    if (H < ENTROPY_THRESHOLD && rps > Math.max(10, cap * 0.6)) {
      recordLog(ip, "low_entropy_suspected_flood", {
        entropy: Number(H.toFixed(3)),
        rps: Number(rps.toFixed(2)),
      });
      greylistIP(ip, "low_entropy_pattern", GREYLIST_TTL_SEC);
      await sleep(TARPIT_MS);
      if (pathClassFor(path) === "strict") {
        blockIP(ip, "strict_endpoint_anomaly", BLOCK_TTL_SEC);
      }
      res.status(403).json({ error: "anomaly_blocked" });
      return;
    }

    // harden response headers
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Referrer-Policy", "no-referrer");
    res.setHeader("X-DNS-Prefetch-Control", "off");
    res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
    res.setHeader("Cross-Origin-Resource-Policy", "same-site");
    res.setHeader("X-Permitted-Cross-Domain-Policies", "none");
    res.setHeader("X-Defense-Node", NODE_ID);
    res.setHeader("X-Defense-Profile", pathClassFor(path));

    next();
  } catch (err) {
    console.error("[ddos] guard error", err);
    res.status(500).json({ error: "ddos_guard_error" });
  }
}

// -----------------------------
// Router (status & admin endpoints)
// -----------------------------
import { Router } from "express";
export const ddosRouter = Router();

ddosRouter.get("/security/status", (_req, res) => {
  // snapshot
  res.json({
    status: "active",
    node: NODE_ID,
    env: ENV,
    blocklist_size: blocklist.size,
    greylist_size: greylist.size,
    buckets_size: buckets.size,
    movavg_ips: ipMovAvg.size,
    window_sec: MOVAVG_WINDOW_SEC,
    entropy_threshold: ENTROPY_THRESHOLD,
    trust_proxy: TRUST_PROXY,
    strict_paths: STRICT_PATH_PREFIXES,
    static_paths: STATIC_PATH_PREFIXES,
    ts: new Date().toISOString(),
  });
});

ddosRouter.get("/security/logs", (_req, res) => {
  res.json({ count: logs.length, items: logs.slice(-500) });
});

ddosRouter.post("/security/block", async (req, res) => {
  try {
    const { ip, ttlSec, reason } = req.body || {};
    if (!ip) return res.status(400).json({ error: "ip_required" });
    blockIP(ip, reason || "manual_block", Number(ttlSec) || BLOCK_TTL_SEC);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: "block_error" });
  }
});

ddosRouter.post("/security/clear", (_req, res) => {
  clearBlocks();
  res.json({ ok: true });
});

ddosRouter.get("/ddos/metrics", (_req, res) => {
  // lightweight metrics
  const mem = process.memoryUsage();
  res.json({
    node: NODE_ID,
    env: ENV,
    memory_mb: {
      rss: Math.round(mem.rss / 1_048_576),
      heapUsed: Math.round(mem.heapUsed / 1_048_576),
      heapTotal: Math.round(mem.heapTotal / 1_048_576),
    },
    buckets: buckets.size,
    blocklist: blocklist.size,
    greylist: greylist.size,
    movavg_ips: ipMovAvg.size,
    ts: new Date().toISOString(),
  });
});

// -----------------------------
// Attach helper to app easily
// -----------------------------
import type { Express } from "express";
export function mountDdosSecurity(app: Express) {
  // Place early in middleware chain
  app.use(ddosGuard);

  // Mount admin/status routes
  app.use(ddosRouter);

  console.log("[ddos] Enhanced Network Defense mounted");
}

// -----------------------------
// Health self-test (optional)
// -----------------------------
export async function ddosSelfTest(): Promise<{ ok: boolean; id: string }> {
  const id = crypto.randomUUID();
  try {
    // Light check on Redis (if present)
    if (redis) {
      await redis.ping();
    }
    return { ok: true, id };
  } catch {
    return { ok: false, id };
  }
}
