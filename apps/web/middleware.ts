/**
 * Clisonix Cloud - Authentication Middleware
 * Protects routes using Auth.js authentication
 */

import { auth } from "@/lib/auth/core";
import {
  createHoneypotHeaders,
  createSecurityHeaders,
  generateNonce,
  getSecurityOptionsFromEnv,
} from "@/lib/security/security-headers";
import {
  BLOCKED_PROBE_PATTERNS,
  DEFENSE_CONFIG,
  DISALLOWED_METHODS,
  matchesPathPrefix,
} from "@/lib/security/defense-config";
import { NextResponse } from "next/server";
import { originMatches } from "@/lib/security/request-origin";

// Everything is public by default (marketing pages, module previews, demos,
// legal pages, PWA assets like /manifest.json and /.well-known/*, etc.).
// Only these routes require a signed-in session. Keeping this list SHORT and
// explicit avoids the historical bug where new public pages were silently
// gated because they were never added to a giant allowlist.
const protectedRoutePatterns = [
  /^\/app(\/.*)?$/,
  /^\/admin(\/.*)?$/,
  /^\/admin-old$/,
  /^\/dashboard(\/.*)?$/,
  /^\/user\/dashboard(\/.*)?$/,
];

function isProtectedRoute(pathname: string) {
  return protectedRoutePatterns.some((pattern) => pattern.test(pathname));
}

function sameOrigin(
  req: Parameters<Parameters<typeof auth>[0]>[0],
  candidate: string | null,
) {
  const forwardedHost =
    req.headers.get("x-forwarded-host")?.split(",")[0]?.trim() || null;
  const forwardedProto =
    req.headers.get("x-forwarded-proto")?.split(",")[0]?.trim() || "https";
  const forwardedOrigin = forwardedHost
    ? `${forwardedProto}://${forwardedHost}`
    : null;

  return originMatches(candidate, [
    req.nextUrl.origin,
    forwardedOrigin,
    process.env.AUTH_URL,
    process.env.NEXTAUTH_URL,
    process.env.NEXT_PUBLIC_APP_URL,
  ]);
}

function applySecurityHeaders(
  req: Parameters<Parameters<typeof auth>[0]>[0],
  response: NextResponse,
  isStrictPath: boolean,
  isStaticPath: boolean,
  nonce: string,
) {
  const headers = createSecurityHeaders({
    ...getSecurityOptionsFromEnv(),
    nonce,
  });

  for (const [key, value] of Object.entries(headers)) {
    response.headers.set(key, value);
  }

  response.headers.set(
    "X-Defense-Profile",
    isStrictPath ? "strict" : isStaticPath ? "static" : "default",
  );

  if (isStrictPath) {
    const honeypotHeaders = createHoneypotHeaders();
    for (const [key, value] of Object.entries(honeypotHeaders)) {
      response.headers.set(key, value);
    }
  }

  return response;
}

function deniedResponse(
  req: Parameters<Parameters<typeof auth>[0]>[0],
  status: number,
  reason: string,
  isStrictPath = false,
  isStaticPath = false,
) {
  const nonce = generateNonce();
  const response = NextResponse.json(
    {
      error: reason,
      status,
      timestamp: new Date().toISOString(),
    },
    { status },
  );

  response.headers.set("X-Defense-Action", "blocked");
  return applySecurityHeaders(req, response, isStrictPath, isStaticPath, nonce);
}

function hasMalformedNextActionId(value: string | null): boolean {
  if (!value) return false;
  const trimmed = value.trim();
  if (!trimmed) return true;
  if (trimmed.length < 8) return true;
  return !/^[A-Za-z0-9_-]+$/.test(trimmed);
}

const LEGACY_COOKIE = "clx_legacy_gate";

export default auth((req) => {
  const pathname = req.nextUrl.pathname;
  const method = req.method.toUpperCase();

  // Legacy dashboard gate — must come before auth redirect
  if (pathname === "/admin-old" || pathname.startsWith("/dashboard")) {
    if (req.cookies.get(LEGACY_COOKIE)?.value !== "granted") {
      return NextResponse.redirect(new URL("/", req.url));
    }
  }
  const isStrictPath = matchesPathPrefix(pathname, DEFENSE_CONFIG.paths.strict);
  const isStaticPath = matchesPathPrefix(pathname, DEFENSE_CONFIG.paths.static);
  const host = req.headers.get("host")?.toLowerCase().split(":")[0] ?? "";

  if (host === "clisonix.com") {
    const redirectUrl = req.nextUrl.clone();
    redirectUrl.protocol = "https";
    redirectUrl.host = "www.clisonix.com";

    const response = NextResponse.redirect(redirectUrl, 308);
    return applySecurityHeaders(
      req,
      response,
      isStrictPath,
      isStaticPath,
      generateNonce(),
    );
  }

  if (DISALLOWED_METHODS.has(method)) {
    return deniedResponse(
      req,
      405,
      "method_not_allowed",
      isStrictPath,
      isStaticPath,
    );
  }

  const nextActionId = req.headers.get("next-action");
  if (method === "POST" && hasMalformedNextActionId(nextActionId)) {
    return deniedResponse(
      req,
      409,
      "stale_client_action_reload_required",
      isStrictPath,
      isStaticPath,
    );
  }

  if (BLOCKED_PROBE_PATTERNS.some((pattern) => pattern.test(pathname))) {
    return deniedResponse(
      req,
      403,
      "probe_blocked",
      isStrictPath,
      isStaticPath,
    );
  }

  if (isStrictPath && !["GET", "HEAD", "OPTIONS"].includes(method)) {
    const origin = req.headers.get("origin");
    const referer = req.headers.get("referer");
    const fetchSite = req.headers.get("sec-fetch-site");

    if (
      fetchSite === "cross-site" ||
      !sameOrigin(req, origin) ||
      !sameOrigin(req, referer)
    ) {
      return deniedResponse(
        req,
        403,
        "cross_site_blocked",
        isStrictPath,
        isStaticPath,
      );
    }
  }

  const nonce = generateNonce();
  const requestHeaders = new Headers(req.headers);
  requestHeaders.set("x-nonce", nonce);

  // Single unified auth policy: only the small protected list above requires
  // a session. Everything else (marketing, module previews, demos, PWA
  // assets) is public — no per-module exceptions to maintain.
  if (
    isProtectedRoute(pathname) &&
    !pathname.startsWith("/api") &&
    !req.auth?.user
  ) {
    const signInUrl = new URL("/sign-in", req.url);
    const response = NextResponse.redirect(signInUrl);
    return applySecurityHeaders(
      req,
      response,
      isStrictPath,
      isStaticPath,
      nonce,
    );
  }

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
  return applySecurityHeaders(req, response, isStrictPath, isStaticPath, nonce);
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
  ],
};
