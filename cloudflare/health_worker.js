/**
 * CLISONIX CLOUD — Enterprise Zero-Trust Health Worker
 * =====================================================
 * Multi-tenant health monitoring with RBAC, JWT validation, and real-time alerting.
 *
 * Architecture:
 *   - Cloudflare Access JWT validation (Zero-Trust)
 *   - Role-Based Access Control (admin, operator, lab)
 *   - Health probes for 6 critical services (Ocean, Backend, OpenMind, Excel, Ollama, Translation)
 *   - Scheduled cron (every 5 minutes) + on-demand HTTP API
 *   - Slack notifications for service degradation
 *
 * Deployment:
 *   npx wrangler deploy
 *
 * Environment Variables (wrangler.toml → [vars]):
 *   TEAM_DOMAIN  — https://clisonix-com-pages.cloudflareaccess.com
 *   POLICY_AUD   — Application Audience tag from Cloudflare Access
 *
 * Secrets (wrangler secret put <name>):
 *   SLACK_WEBHOOK_URL  — Slack webhook for #critical-alerts
 *   HETZNER_IP         — Production server IP (default: 46.225.14.83)
 *
 * @see wrangler.toml
 */

// ESM import from npm package (installed locally, bundled by Wrangler)
import { jwtVerify, createRemoteJWKSet } from "jose";

// ─── Configuration ─────────────────────────────────────────────────────────────
const CONFIG = {
  jwtHeader: "cf-access-jwt-assertion",
  jwksPath: "/cdn-cgi/access/certs",
  requestIdHeader: "cf-ray",
  defaultTimeout: 8000,
};

// ─── RBAC Policies ─────────────────────────────────────────────────────────────
const RBAC = {
  admin: {
    domains: ["clisonix.com", "ultrawebthinking.com"],
    allowAll: true,
  },
  operator: {
    domains: ["clisonix.com"],
    allowedPaths: ["/health", "/status", "/metrics"],
  },
  lab: {
    domains: ["ultrawebthinking.com"],
    allowedPaths: ["/health", "/lab", "/experiments"],
  },
};

// ─── Service Definitions ───────────────────────────────────────────────────────
const SERVICES = [
  { name: "ocean-core", port: 8030, path: "/health" },
  { name: "backend-api", port: 8000, path: "/health" },
  { name: "openmind", port: 9999, path: "/health" },
  { name: "excel-core", port: 8002, path: "/health" },
  { name: "ollama", port: 11434, path: "/api/tags" },
  { name: "translation", port: 8036, path: "/health" },
];

// ─── Logging Utilities ─────────────────────────────────────────────────────────
function log(ctx, level, message, extra = {}) {
  const base = {
    level,
    message,
    requestId: ctx.requestId,
    timestamp: new Date().toISOString(),
  };
  console.log(JSON.stringify({ ...base, ...extra }));
}

function buildContext(request, env) {
  const url = new URL(request.url);
  const requestId = request.headers.get(CONFIG.requestIdHeader) || crypto.randomUUID();

  return { request, env, url, requestId };
}

function jsonResponse(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      ...headers,
    },
  });
}

function getEmailDomain(email) {
  if (!email || !email.includes("@")) return null;
  return email.split("@")[1].toLowerCase();
}

// ─── Service Health Probes ─────────────────────────────────────────────────────
/** Probe a single service and return real latency + status. */
async function probeService(ip, svc, timeoutMs = CONFIG.defaultTimeout) {
  const url = `http://${ip}:${svc.port}${svc.path}`;
  const start = Date.now();
  let httpCode = 0;
  let body = "";
  let error = null;

  try {
    const resp = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(timeoutMs),
    });
    httpCode = resp.status;
    body = await resp.text().catch(() => "");
  } catch (err) {
    error = err.message || String(err);
  }

  const latencyMs = Date.now() - start;
  const ok = httpCode >= 200 && httpCode < 300;

  return { name: svc.name, url, ok, httpCode, latencyMs, error, body };
}

/** Post a Slack message when a service is down (with AI troubleshooting). */
async function notifySlack(webhookUrl, result, pop, env = null) {
  if (!webhookUrl) return;

  const emoji = result.ok ? "✅" : "🔴";
  const status = result.ok ? "UP" : `DOWN (HTTP ${result.httpCode || "timeout"})`;

  // AI-powered troubleshooting for failed services
  let aiSuggestion = null;
  if (!result.ok && env && env.AI) {
    try {
      const response = await env.AI.run('@cf/openai/gpt-oss-20b', {
        messages: [{
          role: 'system',
          content: 'You are a DevOps expert for Clisonix infrastructure. Provide concise troubleshooting steps (max 3 bullet points) for service failures.'
        }, {
          role: 'user',
          content: `Service: ${result.name}\nURL: ${result.url}\nHTTP Code: ${result.httpCode || 0}\nError: ${result.error || 'timeout'}\n\nWhat are the most likely causes and quick fixes?`
        }],
        max_tokens: 200,
        temperature: 0.3
      });
      aiSuggestion = response.response || null;
    } catch (aiError) {
      console.error('AI analysis failed:', aiError);
    }
  }

  const payload = {
    text: `${emoji} Cloudflare Edge Check — ${result.name} is ${status}`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `${emoji} Edge Health: ${result.name} — ${status}`,
          emoji: true,
        },
      },
      {
        type: "section",
        fields: [
          { type: "mrkdwn", text: `*Service:*\n${result.name}` },
          { type: "mrkdwn", text: `*Status:*\n${status}` },
          { type: "mrkdwn", text: `*Latency:*\n${result.latencyMs}ms` },
          { type: "mrkdwn", text: `*CF PoP:*\n${pop}` },
          { type: "mrkdwn", text: `*URL:*\n${result.url}` },
          {
            type: "mrkdwn",
            text: `*Time:*\n${new Date().toISOString()}`,
          },
        ],
      },
    ],
  };

  if (result.error) {
    payload.blocks.push({
      type: "section",
      text: { type: "mrkdwn", text: `*Error:*\n\`${result.error}\`` },
    });
  }

  // Add AI troubleshooting suggestions
  if (aiSuggestion) {
    payload.blocks.push({
      type: "section",
      text: { 
        type: "mrkdwn", 
        text: `*🤖 AI Troubleshooting:*\n${aiSuggestion}` 
      },
    });
  }

  try {
    await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (_) {
    // Best-effort Slack notification — never throw
  }
}

/** Run all service probes and return structured results. */
async function runChecks(env) {
  const ip = env.HETZNER_IP || "46.225.14.83";
  const probes = await Promise.all(
    SERVICES.map((svc) => probeService(ip, svc))
  );
  return probes;
}

// ─── JWT & RBAC ────────────────────────────────────────────────────────────────
/** Validate Cloudflare Access JWT token from request headers */
async function validateAccessJWT(ctx) {
  const { request, env } = ctx;

  if (!env.TEAM_DOMAIN || !env.POLICY_AUD) {
    log(ctx, "error", "Missing TEAM_DOMAIN or POLICY_AUD in env");
    return {
      ok: false,
      status: 500,
      error: "Server misconfiguration: TEAM_DOMAIN or POLICY_AUD missing",
    };
  }

  const token = request.headers.get(CONFIG.jwtHeader);
  if (!token) {
    log(ctx, "warn", "Missing CF Access JWT header");
    return {
      ok: false,
      status: 403,
      error: "Missing required CF Access JWT",
    };
  }

  try {
    const jwksUrl = new URL(CONFIG.jwksPath, env.TEAM_DOMAIN);
    const JWKS = createRemoteJWKSet(jwksUrl);

    const { payload } = await jwtVerify(token, JWKS, {
      issuer: env.TEAM_DOMAIN,
      audience: env.POLICY_AUD,
    });

    const email = payload.email || payload.sub || null;
    const domain = getEmailDomain(email);

    log(ctx, "info", "JWT verified", { email, domain, aud: payload.aud });

    return { ok: true, payload, email, domain };
  } catch (err) {
    log(ctx, "warn", "JWT verification failed", {
      error: err.message,
      name: err.name,
    });

    return {
      ok: false,
      status: 403,
      error: "Invalid or unauthorized token",
    };
  }
}

/** Resolve user role based on email/domain/JWT claims */
function resolveRole(ctx, auth) {
  const { email, domain, payload } = auth;

  // Check JWT claims for explicit roles
  if (payload.roles && Array.isArray(payload.roles)) {
    if (payload.roles.includes("admin")) return "admin";
    if (payload.roles.includes("operator")) return "operator";
    if (payload.roles.includes("lab")) return "lab";
  }

  // Domain-based heuristic
  if (domain === "clisonix.com") return "admin";
  if (domain === "ultrawebthinking.com") return "lab";

  log(ctx, "info", "No explicit role matched, defaulting to 'operator'", {
    email,
    domain,
  });

  return "operator";
}

/** Enforce RBAC policies */
function enforceRBAC(ctx, auth, role) {
  const policy = RBAC[role];
  if (!policy) {
    log(ctx, "warn", "No RBAC policy for role", { role });
    return {
      ok: false,
      status: 403,
      error: `No policy defined for role: ${role}`,
    };
  }

  const path = ctx.url.pathname;
  const domain = auth.domain;

  if (policy.domains && !policy.domains.includes(domain)) {
    log(ctx, "warn", "Domain not allowed for role", { role, domain });
    return {
      ok: false,
      status: 403,
      error: "Domain not allowed for this role",
    };
  }

  if (policy.allowAll) {
    log(ctx, "info", "RBAC allowAll", { role, path });
    return { ok: true };
  }

  if (
    policy.allowedPaths &&
    policy.allowedPaths.some((p) => path.startsWith(p))
  ) {
    log(ctx, "info", "RBAC path allowed", { role, path });
    return { ok: true };
  }

  log(ctx, "warn", "RBAC denied", { role, path });
  return {
    ok: false,
    status: 403,
    error: "Access denied by RBAC policy",
  };
}

// ─── Scheduled cron handler ───────────────────────────────────────────────────
async function handleScheduled(event, env, ctx) {
  const pop = event?.scheduledTime
    ? new Date(event.scheduledTime).toISOString()
    : "unknown";

  const results = await runChecks(env);

  // Notify Slack only for DOWN services (with AI troubleshooting)
  const notifyPromises = results
    .filter((r) => !r.ok)
    .map((r) => notifySlack(env.SLACK_WEBHOOK_URL, r, pop, env));

  await Promise.allSettled(notifyPromises);

  // Log summary to Cloudflare Workers Logs
  const summary = results.map(
    (r) =>
      `${r.ok ? "OK" : "FAIL"} ${r.name} HTTP=${r.httpCode} latency=${r.latencyMs}ms`
  );
  console.log("[EdgeHealth]", summary.join(" | "));
}

// ─── HTTP fetch handler (on-demand status page with RBAC) ─────────────────────
async function handleFetch(request, env, ctx) {
  const context = buildContext(request, env);

  try {
    log(context, "info", "Incoming request");

    // Only allow GET requests
    if (request.method !== "GET") {
      return jsonResponse({ error: "Method Not Allowed" }, 405);
    }

    // 1) JWT validation
    const auth = await validateAccessJWT(context);
    if (!auth.ok) {
      return jsonResponse(
        {
          error: auth.error,
          requestId: context.requestId,
        },
        auth.status
      );
    }

    // 2) Role resolution
    const role = resolveRole(context, auth);

    // 3) RBAC enforcement
    const rbac = enforceRBAC(context, auth, role);
    if (!rbac.ok) {
      return jsonResponse(
        {
          error: rbac.error,
          role,
          requestId: context.requestId,
        },
        rbac.status
      );
    }

    // 4) Run health checks
    const results = await runChecks(env);
    const healthy = results.filter((r) => r.ok).length;
    const allOk = healthy === results.length;

    const body = {
      checked_at: new Date().toISOString(),
      server: env.HETZNER_IP || "46.225.14.83",
      authenticated_user: auth.email || "authenticated",
      role,
      summary: {
        healthy,
        total: results.length,
        status: allOk ? "all_healthy" : "degraded",
      },
      services: results.map(({ name, ok, httpCode, latencyMs, error }) => ({
        name,
        ok,
        http_code: httpCode,
        latency_ms: latencyMs,
        ...(error ? { error } : {}),
      })),
    };

    const response = jsonResponse(body, allOk ? 200 : 503);

    // 5) Enterprise headers
    response.headers.set("x-request-id", context.requestId);
    response.headers.set("x-zero-trust-gateway", "clisonix");
    response.headers.set("x-checked-from", "cloudflare-worker");

    return response;
  } catch (err) {
    log(context, "error", "Unhandled exception", { error: err.message });

    return jsonResponse(
      {
        error: "Internal server error",
        requestId: context.requestId,
      },
      500
    );
  }
}

// ─── Worker entry point ───────────────────────────────────────────────────────
export default {
  fetch: handleFetch,
  scheduled: handleScheduled,
};
