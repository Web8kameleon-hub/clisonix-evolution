export interface SecurityHeaders {
  [key: string]: string;
}

export interface TrustedDomains {
  scripts?: string[];
  styles?: string[];
  connect?: string[];
  images?: string[];
  fonts?: string[];
  frames?: string[];
  media?: string[];
  workers?: string[];
}

export interface SecurityOptions {
  nonce?: string;
  isDevelopment?: boolean;
  enableHsts?: boolean;
  reportUri?: string;
  trustedDomains?: TrustedDomains;
}

const DEFAULT_TRUSTED_DOMAINS: Required<TrustedDomains> = {
  scripts: [
    "https://vercel.live",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
    "https://pagead2.googlesyndication.com",
  ],
  styles: ["https://fonts.googleapis.com"],
  connect: [
    "https://clisonix.com",
    "https://www.clisonix.com",
    "https://api.clisonix.com",
    "https://*.clisonix.com",
    "wss://*.clisonix.com",
    "https://vercel.live",
  ],
  images: [
    "https://clisonix.com",
    "https://www.clisonix.com",
    "https://images.unsplash.com",
    "https://*.githubusercontent.com",
  ],
  fonts: ["https://fonts.gstatic.com", "data:"],
  frames: [
    "https://googleads.g.doubleclick.net",
    "https://tpc.googlesyndication.com",
  ],
  media: [],
  workers: ["blob:"],
};

function splitEnvList(value?: string): string[] {
  return (value ?? "")
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function uniqueSources(...groups: Array<string[] | undefined>): string[] {
  return [...new Set(groups.flat().filter(Boolean))];
}

function mergeTrustedDomains(domains?: TrustedDomains): Required<TrustedDomains> {
  return {
    scripts: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.scripts,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_SCRIPT_SRC),
      domains?.scripts,
    ),
    styles: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.styles,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_STYLE_SRC),
      domains?.styles,
    ),
    connect: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.connect,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_CONNECT_SRC),
      domains?.connect,
    ),
    images: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.images,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_IMAGE_SRC),
      domains?.images,
    ),
    fonts: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.fonts,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_FONT_SRC),
      domains?.fonts,
    ),
    frames: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.frames,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_FRAME_SRC),
      domains?.frames,
    ),
    media: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.media,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_MEDIA_SRC),
      domains?.media,
    ),
    workers: uniqueSources(
      DEFAULT_TRUSTED_DOMAINS.workers,
      splitEnvList(process.env.NEXT_PUBLIC_CSP_WORKER_SRC),
      domains?.workers,
    ),
  };
}

function encodeBase64Url(bytes: Uint8Array): string {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");
  }

  if (typeof btoa !== "undefined") {
    let binary = "";
    for (const byte of bytes) {
      binary += String.fromCharCode(byte);
    }

    return btoa(binary)
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");
  }

  throw new Error("Base64URL encoding is not available in this runtime.");
}

export function generateNonce(size = 32): string {
  if (globalThis.crypto?.getRandomValues) {
    const bytes = new Uint8Array(size);
    globalThis.crypto.getRandomValues(bytes);
    return encodeBase64Url(bytes);
  }

  throw new Error("Secure random number generation is unavailable for CSP nonce creation.");
}

export function createSecurityHeaders(options: SecurityOptions = {}): SecurityHeaders {
  const isDevelopment = options.isDevelopment ?? process.env.NODE_ENV !== "production";
  const allowUnsafeEval =
    isDevelopment && process.env.NEXT_PUBLIC_ALLOW_UNSAFE_EVAL === "true";
  const nonce = options.nonce ?? generateNonce();
  const trustedDomains = mergeTrustedDomains(options.trustedDomains);

  const scriptSources = uniqueSources(
    ["'self'", `'nonce-${nonce}'`, "'strict-dynamic'"],
    allowUnsafeEval ? ["'unsafe-eval'"] : [],
    trustedDomains.scripts,
  );

  const styleSources = uniqueSources(
    ["'self'", `'nonce-${nonce}'`],
    isDevelopment ? ["'unsafe-inline'"] : [],
    trustedDomains.styles,
  );

  const connectSources = uniqueSources(
    ["'self'"],
    isDevelopment
      ? [
          "http://localhost:*",
          "http://127.0.0.1:*",
          "ws://localhost:*",
          "ws://127.0.0.1:*",
        ]
      : [],
    trustedDomains.connect,
  );

  const cspDirectives = [
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "manifest-src 'self'",
    `script-src ${scriptSources.join(" ")}`,
    `style-src ${styleSources.join(" ")}`,
    `img-src ${uniqueSources(["'self'", "data:", "blob:"], trustedDomains.images).join(" ")}`,
    `font-src ${uniqueSources(["'self'"], trustedDomains.fonts).join(" ")}`,
    `connect-src ${connectSources.join(" ")}`,
    `frame-src ${trustedDomains.frames.length ? trustedDomains.frames.join(" ") : "'none'"}`,
    `worker-src ${uniqueSources(["'self'", "blob:"], trustedDomains.workers).join(" ")}`,
    `media-src ${uniqueSources(["'self'", "data:", "blob:"], trustedDomains.media).join(" ")}`,
    "script-src-attr 'none'",
    "upgrade-insecure-requests",
    !isDevelopment ? "block-all-mixed-content" : "",
    options.reportUri ? `report-uri ${options.reportUri}` : "",
    options.reportUri ? "report-to csp-endpoint" : "",
  ].filter(Boolean);

  return {
    "Content-Security-Policy": cspDirectives.join("; "),
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": [
      "accelerometer=()",
      "autoplay=()",
      "camera=(self)",
      "display-capture=(self)",
      "encrypted-media=()",
      "fullscreen=(self)",
      "geolocation=()",
      "gyroscope=()",
      "magnetometer=()",
      "microphone=(self)",
      "midi=()",
      "payment=()",
      "picture-in-picture=(self)",
      "publickey-credentials-get=(self)",
      "screen-wake-lock=()",
      "sync-xhr=(self)",
      "usb=()",
      "web-share=()",
      "xr-spatial-tracking=()",
    ].join(", "),
    ...(options.enableHsts === false
      ? {}
      : {
          "Strict-Transport-Security":
            "max-age=31536000; includeSubDomains; preload",
        }),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
    "Origin-Agent-Cluster": "?1",
    "X-DNS-Prefetch-Control": "off",
    "X-Download-Options": "noopen",
    "X-Permitted-Cross-Domain-Policies": "none",
    "X-Mirror-Defense": "Layer-7-Active",
    "X-Security-Level": "Clisonix-Ultra-10/10",
    "X-Content-Nonce": nonce,
    "X-Guardian-Status": "Active",
    "X-Defense-Timestamp": new Date().toISOString(),
    ...(options.reportUri
      ? {
          "Reporting-Endpoints": `csp-endpoint="${options.reportUri}"`,
        }
      : {}),
    "Cache-Control": "no-cache, no-store, must-revalidate, private",
    Pragma: "no-cache",
    Expires: "0",
  };
}

export function createRateLimitHeaders(
  remaining: number,
  resetTime: number,
  limit = 1000,
): SecurityHeaders {
  const retryAfterSeconds = Math.max(0, Math.ceil((resetTime - Date.now()) / 1000));

  return {
    "X-RateLimit-Limit": limit.toString(),
    "X-RateLimit-Remaining": Math.max(0, remaining).toString(),
    "X-RateLimit-Reset": resetTime.toString(),
    "X-RateLimit-Policy": "sliding-window",
    "Retry-After": retryAfterSeconds.toString(),
  };
}

export function createHoneypotHeaders(): SecurityHeaders {
  return {
    "X-Honeypot-Active": "true",
    "X-Honeypot-Endpoint": "/api/v1/trap",
    "X-Trap-Detection": "Armed",
    "X-Security-Scan": "Monitoring",
    "X-Decoy-Response": "true",
  };
}

export function getSecurityOptionsFromEnv(): SecurityOptions {
  return {
    isDevelopment: process.env.NODE_ENV !== "production",
    reportUri:
      process.env.NEXT_PUBLIC_CSP_REPORT_URI ||
      process.env.CSP_REPORT_URI ||
      "/api/csp-report",
    trustedDomains: {
      scripts: splitEnvList(process.env.NEXT_PUBLIC_CSP_SCRIPT_SRC),
      styles: splitEnvList(process.env.NEXT_PUBLIC_CSP_STYLE_SRC),
      connect: splitEnvList(process.env.NEXT_PUBLIC_CSP_CONNECT_SRC),
      images: splitEnvList(process.env.NEXT_PUBLIC_CSP_IMAGE_SRC),
      fonts: splitEnvList(process.env.NEXT_PUBLIC_CSP_FONT_SRC),
      frames: splitEnvList(process.env.NEXT_PUBLIC_CSP_FRAME_SRC),
      media: splitEnvList(process.env.NEXT_PUBLIC_CSP_MEDIA_SRC),
      workers: splitEnvList(process.env.NEXT_PUBLIC_CSP_WORKER_SRC),
    },
  };
}

export default createSecurityHeaders;
