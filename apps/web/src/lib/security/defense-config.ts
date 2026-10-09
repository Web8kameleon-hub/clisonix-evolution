export interface DefenseConfig {
  trustProxy: boolean;
  firewall: {
    whitelistCidrs: string[];
    blacklistCidrs: string[];
    temporaryBanSeconds: number;
  };
  ratelimit: {
    default: { capacity: number; refillPerSec: number };
    strict: { capacity: number; refillPerSec: number };
    static: { capacity: number; refillPerSec: number };
  };
  paths: {
    strict: string[];
    static: string[];
  };
  pow: {
    difficultyBits: number;
    cookieName: string;
    ttlSeconds: number;
  };
  anomaly: {
    ewmaAlpha: number;
    spikeFactor: number;
    greylistSeconds: number;
    tarpitMs: number;
  };
  mesh: {
    nodeId: string;
    peers: Array<{ id: string }>;
  };
}

function parseCsv(value: string | undefined, fallback: string[]): string[] {
  return (value ?? fallback.join(","))
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) return fallback;
  return value.toLowerCase() === "true";
}

export const DEFENSE_CONFIG: DefenseConfig = {
  trustProxy: parseBoolean(process.env.TRUST_PROXY, true),
  firewall: {
    whitelistCidrs: parseCsv(process.env.SECURITY_WHITELIST_CIDRS, [
      "127.0.0.1/32",
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
      "::1/128",
    ]),
    blacklistCidrs: parseCsv(process.env.SECURITY_BLACKLIST_CIDRS, []),
    temporaryBanSeconds: Number(process.env.SECURITY_TEMP_BAN_SECONDS || 1800),
  },
  ratelimit: {
    default: {
      capacity: Number(process.env.SECURITY_RL_DEFAULT_CAPACITY || 120),
      refillPerSec: Number(process.env.SECURITY_RL_DEFAULT_REFILL || 60),
    },
    strict: {
      capacity: Number(process.env.SECURITY_RL_STRICT_CAPACITY || 30),
      refillPerSec: Number(process.env.SECURITY_RL_STRICT_REFILL || 15),
    },
    static: {
      capacity: Number(process.env.SECURITY_RL_STATIC_CAPACITY || 300),
      refillPerSec: Number(process.env.SECURITY_RL_STATIC_REFILL || 150),
    },
  },
  paths: {
    strict: parseCsv(process.env.SECURITY_STRICT_PATHS, [
      "/auth",
      "/login",
      "/api/auth",
      "/defense/handshake",
      "/defense/seal",
    ]),
    static: parseCsv(process.env.SECURITY_STATIC_PATHS, ["/static", "/assets", "/_next/static"]),
  },
  pow: {
    difficultyBits: Number(process.env.SECURITY_POW_DIFFICULTY || 18),
    cookieName: process.env.SECURITY_POW_COOKIE || "pow_ok",
    ttlSeconds: Number(process.env.SECURITY_POW_TTL || 900),
  },
  anomaly: {
    ewmaAlpha: Number(process.env.SECURITY_ANOMALY_EWMA || 0.2),
    spikeFactor: Number(process.env.SECURITY_ANOMALY_SPIKE_FACTOR || 4.0),
    greylistSeconds: Number(process.env.SECURITY_GREYLIST_SECONDS || 900),
    tarpitMs: Number(process.env.SECURITY_TARPIT_MS || 400),
  },
  mesh: {
    nodeId: process.env.SECURITY_MESH_NODE_ID || "web8-node-tirana-01",
    peers: parseCsv(process.env.SECURITY_MESH_PEERS, [
      "web8-node-berlin-01",
      "web8-node-dusseldorf-01",
    ]).map((id) => ({ id })),
  },
};

export function matchesPathPrefix(pathname: string, prefixes: string[]): boolean {
  return prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export const DISALLOWED_METHODS = new Set(["TRACE", "TRACK", "CONNECT"]);

export const BLOCKED_PROBE_PATTERNS = [
  /\.env/i,
  /\.git/i,
  /wp-admin/i,
  /phpmyadmin/i,
  /server-status/i,
  /composer\.(json|lock)/i,
  /id_rsa/i,
  /\.sql/i,
];
