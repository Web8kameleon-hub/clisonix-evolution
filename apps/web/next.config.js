/**
 * Clisonix Cloud Industrial Next.js Configuration
 * Production-ready with API rewrites for backend proxy
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadRootEnvFile(relativeFilePath) {
  const envPath = path.resolve(__dirname, "../..", relativeFilePath);
  if (!fs.existsSync(envPath)) {
    return;
  }

  const content = fs.readFileSync(envPath, "utf8");
  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }

    const separatorIndex = line.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }

    const key = line.slice(0, separatorIndex).trim();
    if (!key || process.env[key] !== undefined) {
      continue;
    }

    const value = line.slice(separatorIndex + 1).trim();
    process.env[key] = value;
  }
}

loadRootEnvFile(".env.local");
loadRootEnvFile(".env.monetization.local");

// PRODUCTION: With network_mode: host, services use localhost
// DEVELOPMENT: Also use localhost for local backend
const isDev = process.env.NODE_ENV === "development";
const API_BASE =
  process.env.API_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (isDev ? "http://localhost:8001" : "http://clisonix-api:8000");
const REPORTING_BASE =
  process.env.REPORTING_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_REPORTING_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (isDev ? "http://localhost:8001" : "http://clisonix-api:8000");
const OCEAN_BASE =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_OCEAN_URL ||
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://clisonix-ocean-core:8030");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["framer-motion"],
  staticPageGenerationTimeout: 600,

  // Fix for monorepo lockfile detection
  outputFileTracingRoot: path.resolve(__dirname, "../.."),

  // ==========================================================================
  // IMAGE OPTIMIZATION (85% size reduction with WebP/AVIF)
  // ==========================================================================
  images: {
    // Enable modern formats
    formats: ["image/avif", "image/webp"],

    // Allowed image domains
    remotePatterns: [
      // Local development & Docker
      {
        protocol: "http",
        hostname: "localhost",
      },
      {
        protocol: "http",
        hostname: "127.0.0.1",
      },
      {
        protocol: "http",
        hostname: "clisonix-api",
      },
      {
        protocol: "http",
        hostname: "clisonix-ocean-core",
      },
      {
        protocol: "http",
        hostname: "clisonix-alba",
      },
      // Production domains
      {
        protocol: "https",
        hostname: "clisonix.com",
      },
      {
        protocol: "https",
        hostname: "*.clisonix.com",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "*.githubusercontent.com",
      },
    ],

    // Responsive image sizes
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],

    // Optimization quality (75 is good balance)
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days cache
  },

  // ==========================================================================
  // COMPRESSION & PERFORMANCE
  // ==========================================================================
  compress: true,
  poweredByHeader: false, // Security: hide X-Powered-By

  // Server-only packages (not bundled for client)
  serverExternalPackages: ["stripe"],

  // ==========================================================================
  // SECURITY HEADERS
  // ==========================================================================
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "off" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value:
              "camera=(self), microphone=(self), geolocation=(), payment=(), usb=()",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains; preload",
          },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
          { key: "Cross-Origin-Resource-Policy", value: "same-site" },
          { key: "Origin-Agent-Cluster", value: "?1" },
          { key: "X-Permitted-Cross-Domain-Policies", value: "none" },
        ],
      },
      // Cache favicon aggressively to prevent spam requests
      {
        source: "/favicon.ico",
        headers: [
          { key: "Cache-Control", value: "public, max-age=86400, immutable" },
        ],
      },
      // Cache static assets aggressively
      {
        source: "/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },

  // CRITICAL: Proxy API requests to backend
  async rewrites() {
    return [
      // Crypto Market API
      {
        source: "/api/crypto/:path*",
        destination: `${API_BASE}/api/crypto/:path*`,
      },
      // Weather API
      {
        source: "/api/weather/:path*",
        destination: `${API_BASE}/api/weather/:path*`,
      },
      // Real Data Dashboard API
      {
        source: "/api/realdata/:path*",
        destination: `${API_BASE}/api/realdata/:path*`,
      },
      // AI Routes
      {
        source: "/api/ai/:path*",
        destination: `${API_BASE}/api/ai/:path*`,
      },
      // Monitoring
      {
        source: "/api/monitoring/:path*",
        destination: `${API_BASE}/api/monitoring/:path*`,
      },
      // System Status
      {
        source: "/api/system-status",
        destination: `${API_BASE}/api/system-status`,
      },
      // Health
      {
        source: "/api/health",
        destination: `${API_BASE}/health`,
      },
      // ASI Trinity Status (Phone Monitor)
      {
        source: "/api/asi-status",
        destination: `${API_BASE}/asi/status`,
      },
      // ASI Health
      {
        source: "/api/asi-health",
        destination: `${API_BASE}/asi/health`,
      },
      // ASI Metrics (all ASI routes)
      {
        source: "/asi/:path*",
        destination: `${API_BASE}/asi/:path*`,
      },
      // Backend proxy (for direct backend calls)
      {
        source: "/backend/:path*",
        destination: `${API_BASE}/:path*`,
      },
      // Backend status specifically
      {
        source: "/backend/status",
        destination: `${API_BASE}/health`,
      },
      // Direct /health endpoint proxy
      {
        source: "/health",
        destination: `${API_BASE}/health`,
      },
      // ===== MEDIA SERVING =====
      // Images/videos from uploads
      {
        source: "/uploads/:path*",
        destination: `${API_BASE}/uploads/:path*`,
      },
      {
        source: "/media/:path*",
        destination: `${API_BASE}/media/:path*`,
      },
      {
        source: "/images/:path*",
        destination: `${API_BASE}/images/:path*`,
      },
      {
        source: "/video/:path*",
        destination: `${API_BASE}/video/:path*`,
      },
      {
        source: "/audio/:path*",
        destination: `${API_BASE}/audio/:path*`,
      },
      {
        source: "/files/:path*",
        destination: `${API_BASE}/files/:path*`,
      },
      // ===== REPORTING API (Port 8001) =====
      // Docker containers
      {
        source: "/api/reporting/:path*",
        destination: `${REPORTING_BASE}/api/reporting/:path*`,
      },
      // Direct docker stats
      {
        source: "/api/docker-containers",
        destination: `${REPORTING_BASE}/api/reporting/docker-containers`,
      },
      {
        source: "/api/docker-stats",
        destination: `${REPORTING_BASE}/api/reporting/docker-stats`,
      },
      {
        source: "/api/system-metrics",
        destination: `${REPORTING_BASE}/api/reporting/system-metrics`,
      },
      // ===== ALBI EEG API =====
      {
        source: "/api/albi/:path*",
        destination: `${API_BASE}/api/albi/:path*`,
      },
      // ===== ALBA API =====
      {
        source: "/api/alba/:path*",
        destination: `${API_BASE}/api/alba/:path*`,
      },
      // ===== ASI API (general) =====
      {
        source: "/api/asi/:path*",
        destination: `${API_BASE}/api/asi/:path*`,
      },
      // ===== JONA Neural Synthesis API =====
      {
        source: "/api/jona/:path*",
        destination: `${API_BASE}/api/jona/:path*`,
      },
      // ===== Security Status =====
      {
        source: "/api/security/:path*",
        destination: `${API_BASE}/api/security/:path*`,
      },
      // ===== System Health =====
      {
        source: "/api/system/:path*",
        destination: `${API_BASE}/api/system/:path*`,
      },
      // ===== OCEAN CORE (Port 8030) =====
      // Zürich Deterministic Engine
      {
        source: "/api/zurich/:path*",
        destination: `${OCEAN_BASE}/api/v1/zurich/:path*`,
      },
      {
        source: "/api/zurich",
        destination: `${OCEAN_BASE}/api/v1/zurich`,
      },
      // Trinity Debate Engine
      {
        source: "/api/debate/stream",
        destination: `${OCEAN_BASE}/api/v1/debate/stream`,
      },
      {
        source: "/api/debate/:path*",
        destination: `${OCEAN_BASE}/api/v1/debate/:path*`,
      },
      {
        source: "/api/debate",
        destination: `${OCEAN_BASE}/api/v1/debate`,
      },
      // Ocean Core general
      {
        source: "/api/ocean/health",
        destination: `${OCEAN_BASE}/health`,
      },
      {
        source: "/api/ocean/:path*",
        destination: `${OCEAN_BASE}/api/v1/:path*`,
      },
      {
        source: "/api/ocean",
        destination: `${OCEAN_BASE}/api/v1/health`,
      },
      // ===== OCEAN MEDIA =====
      {
        source: "/media/ocean/:path*",
        destination: `${OCEAN_BASE}/media/:path*`,
      },
      {
        source: "/videos/ocean/:path*",
        destination: `${OCEAN_BASE}/videos/:path*`,
      },
    ];
  },

  // Keep legacy module links stable across rebuilds/deploys.
  async redirects() {
    return [
      {
        source: "/modules/specialized-expert-chat",
        destination: "/modules/specialized-chat",
        permanent: true,
      },
      {
        source: "/modules/albi-eeg-analysis",
        destination: "/modules/albi-eeg-live",
        permanent: true,
      },
      {
        source: "/modules/clisonix-api-collection",
        destination: "/modules/my-data-dashboard",
        permanent: true,
      },
      {
        source: "/modules/behavioral",
        destination: "/modules/openmind",
        permanent: false,
      },
      {
        source: "/modules/marketplace",
        destination: "/developers",
        permanent: false,
      },
      {
        source: "/modules/trinity-debate",
        destination: "/debate",
        permanent: false,
      },
    ];
  },

  webpack: (config) => {
    config.cache = false;
    return config;
  },

  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },

  httpAgentOptions: {
    keepAlive: true,
  },
  allowedDevOrigins: ["localhost:3000", "127.0.0.1:3000", "clisonix.com"],
};

export default nextConfig;
