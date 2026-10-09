import { auth } from "@/lib/auth/core";
import {
  createSecurityHeaders,
  generateNonce,
  getSecurityOptionsFromEnv,
} from "@/lib/security/security-headers";
import { NextResponse } from "next/server";

const publicRoutePatterns = [
  /^\/$/,
  /^\/sign-in(\/.*)?$/,
  /^\/sign-up(\/.*)?$/,
  /^\/blog(\/.*)?$/,
  /^\/faq(\/.*)?$/,
  /^\/docs(\/.*)?$/,
  /^\/news(\/.*)?$/,
  /^\/terms(\/.*)?$/,
  /^\/privacy(\/.*)?$/,
  /^\/ads\.txt$/,
  /^\/robots\.txt$/,
  /^\/sitemap\.xml$/,
  /^\/sitemap-0\.xml$/,
  /^\/modules$/,
  /^\/modules\/(curiosity-ocean|web-reader|archive|social-intelligence|specialized-chat|aviation-weather|eeg-analysis|neural-synthesis|nanogrid-zeiss|kloud-bridge|weather-dashboard)(\/.*)?$/,
  /^\/(zurich|debate|landing|about-us|pricing|why-clisonix|platform|security|company|developers|status|health)(\/.*)?$/,
];

function isPublicRoute(pathname: string) {
  return publicRoutePatterns.some((pattern) => pattern.test(pathname));
}

function applySecurityHeaders(
  req: Parameters<Parameters<typeof auth>[0]>[0],
  response: NextResponse,
  nonce: string,
) {
  const headers = createSecurityHeaders({
    ...getSecurityOptionsFromEnv(),
    nonce,
  });

  for (const [key, value] of Object.entries(headers)) {
    response.headers.set(key, value);
  }

  return response;
}

export default auth((req) => {
  const pathname = req.nextUrl.pathname;
  const host = req.headers.get("host")?.toLowerCase().split(":")[0] ?? "";

  if (host === "clisonix.com") {
    const redirectUrl = req.nextUrl.clone();
    redirectUrl.protocol = "https";
    redirectUrl.host = "www.clisonix.com";

    const response = NextResponse.redirect(redirectUrl, 308);
    return applySecurityHeaders(req, response, generateNonce());
  }

  const nonce = generateNonce();
  const requestHeaders = new Headers(req.headers);
  requestHeaders.set("x-nonce", nonce);

  if (pathname.startsWith("/api/auth") || isPublicRoute(pathname)) {
    const response = NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
    return applySecurityHeaders(req, response, nonce);
  }

  if (!req.auth?.user && !pathname.startsWith("/api")) {
    const signInUrl = new URL("/sign-in", req.url);
    const response = NextResponse.redirect(signInUrl);
    return applySecurityHeaders(req, response, nonce);
  }

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
  return applySecurityHeaders(req, response, nonce);
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
  ],
};
