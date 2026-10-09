import { NextResponse } from "next/server";
import {
  recordWebVital,
  type WebVitalName,
  type WebVitalsPayload,
} from "@/lib/telemetry/webVitalsStore";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const VALID_METRICS = new Set<WebVitalName>([
  "CLS",
  "FCP",
  "INP",
  "LCP",
  "TTFB",
]);

function tryForwardAsync(payload: WebVitalsPayload): void {
  const forwardUrl = process.env.WEB_VITALS_FORWARD_URL;
  if (!forwardUrl) {
    return;
  }

  queueMicrotask(() => {
    fetch(forwardUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    }).catch((error) => {
      const reason = error instanceof Error ? error.message : String(error);
      console.warn("[WebVitalsForward] failed:", reason);
    });
  });
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isValidPayload(value: unknown): value is WebVitalsPayload {
  if (!value || typeof value !== "object") {
    return false;
  }

  const payload = value as Partial<WebVitalsPayload>;

  if (!isNonEmptyString(payload.id)) return false;
  if (!isNonEmptyString(payload.name) || !VALID_METRICS.has(payload.name as WebVitalName)) return false;
  if (!isFiniteNumber(payload.value) || payload.value < 0) return false;
  if (!isNonEmptyString(payload.pathname)) return false;
  if (!isNonEmptyString(payload.href)) return false;
  if (!isNonEmptyString(payload.userAgent)) return false;
  if (!isNonEmptyString(payload.timestamp)) return false;

  if (payload.delta !== undefined && (!isFiniteNumber(payload.delta) || payload.delta < 0)) return false;

  if (
    payload.rating !== undefined &&
    payload.rating !== "good" &&
    payload.rating !== "needs-improvement" &&
    payload.rating !== "poor"
  ) {
    return false;
  }

  return true;
}

export async function POST(request: Request) {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body" },
      { status: 400 },
    );
  }

  if (!isValidPayload(payload)) {
    return NextResponse.json(
      { ok: false, error: "Invalid web vitals payload" },
      { status: 422 },
    );
  }

  recordWebVital(payload);
  tryForwardAsync(payload);

  console.info("[WebVitals]", {
    metric: payload.name,
    value: payload.value,
    rating: payload.rating ?? "unknown",
    pathname: payload.pathname,
    timestamp: payload.timestamp,
    navigationType: payload.navigationType ?? "unknown",
  });

  return NextResponse.json({ ok: true }, { status: 202 });
}
