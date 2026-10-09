import { NextResponse } from "next/server";

import {
  createSecurityHeaders,
  generateNonce,
  getSecurityOptionsFromEnv,
} from "@/lib/security/security-headers";
import { readRecentCspReports } from "@/lib/security/csp-report-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function hasDirective(policy: string, directive: string) {
  return policy.split(";").some((part) => part.trim().startsWith(directive));
}

export async function GET() {
  const securityOptions = getSecurityOptionsFromEnv();
  const nonce = generateNonce();
  const headers = createSecurityHeaders({
    ...securityOptions,
    nonce,
  });
  const recentReports = await readRecentCspReports(20);

  const csp = headers["Content-Security-Policy"] ?? "";

  return NextResponse.json(
    {
      timestamp: new Date().toISOString(),
      securityHeaders: headers,
      posture: {
        hsts: Boolean(headers["Strict-Transport-Security"]),
        csp: Boolean(csp),
        frameProtection: headers["X-Frame-Options"] === "DENY",
        contentTypeProtection: headers["X-Content-Type-Options"] === "nosniff",
        referrerPolicy: headers["Referrer-Policy"] ?? null,
        reportUri: securityOptions.reportUri ?? null,
      },
      cspDirectives: {
        strictDynamic:
          hasDirective(csp, "script-src") && csp.includes("'strict-dynamic'"),
        upgradeInsecureRequests: hasDirective(csp, "upgrade-insecure-requests"),
        blockAllMixedContent: hasDirective(csp, "block-all-mixed-content"),
        frameAncestors: hasDirective(csp, "frame-ancestors"),
        objectSrcNone:
          hasDirective(csp, "object-src") && csp.includes("object-src 'none'"),
      },
      recentReports,
    },
    {
      headers: {
        "Cache-Control": "no-store",
      },
    },
  );
}
