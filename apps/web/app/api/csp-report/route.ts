import { NextRequest, NextResponse } from "next/server";

import { appendCspReport } from "@/lib/security/csp-report-store";

export const dynamic = "force-dynamic";

function sanitizeBlockedUri(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim()) return null;

  try {
    const parsed = new URL(value);
    return parsed.origin;
  } catch {
    return value.slice(0, 120);
  }
}

function normalizeReport(payload: unknown) {
  const body =
    typeof payload === "object" && payload !== null
      ? ((payload as Record<string, unknown>)["csp-report"] ??
        (payload as Record<string, unknown>)["body"] ??
        payload)
      : {};

  const report = (
    typeof body === "object" && body !== null ? body : {}
  ) as Record<string, unknown>;

  return {
    documentUri: sanitizeBlockedUri(report["document-uri"]),
    violatedDirective:
      typeof report["violated-directive"] === "string"
        ? report["violated-directive"]
        : null,
    effectiveDirective:
      typeof report["effective-directive"] === "string"
        ? report["effective-directive"]
        : null,
    blockedUri: sanitizeBlockedUri(report["blocked-uri"]),
    sourceFile: sanitizeBlockedUri(report["source-file"]),
    disposition:
      typeof report["disposition"] === "string" ? report["disposition"] : null,
    originalPolicy:
      typeof report["original-policy"] === "string"
        ? report["original-policy"].slice(0, 500)
        : null,
    userAgent: null as string | null,
    receivedAt: new Date().toISOString(),
  };
}

export async function POST(request: NextRequest) {
  let payload: unknown = {};

  try {
    const contentType = request.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      payload = await request.json();
    } else {
      const raw = await request.text();
      payload = raw ? JSON.parse(raw) : {};
    }
  } catch {
    payload = {};
  }

  const report = normalizeReport(payload);
  report.userAgent = request.headers.get("user-agent");

  await appendCspReport(report);

  if (process.env.NODE_ENV !== "production") {
    console.warn("[security][csp-report]", report);
  }

  return new NextResponse(null, {
    status: 204,
    headers: {
      "Cache-Control": "no-store",
    },
  });
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      Allow: "OPTIONS, POST",
      "Cache-Control": "no-store",
    },
  });
}
