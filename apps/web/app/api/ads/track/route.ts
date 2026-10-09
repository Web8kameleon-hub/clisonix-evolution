import { NextResponse } from "next/server";

const isDev = process.env.NODE_ENV === "development";
const ADS_CORE_URL =
  process.env.ADS_CORE_URL ||
  (isDev ? "http://localhost:8096" : "http://clisonix-ads-core:8096");

const KNOWN_ECONOMY_CODES = new Set([
  "CLK",
  "CLC",
  "CTC",
  "CTA",
  "CTD",
  "CTS",
  "CTG",
  "CTR",
  "CTU",
  "CTP",
  "CTF",
]);

function isEconomyCode(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const normalized = value.trim().toUpperCase();
  if (KNOWN_ECONOMY_CODES.has(normalized)) return true;
  return /^CT[A-Z]$/.test(normalized);
}

function normalizeTrackPayload(payload: Record<string, unknown>) {
  const normalizedEvent =
    typeof payload.event === "string" ? payload.event.trim().toLowerCase() : "";

  const fromEventCode = isEconomyCode(payload.event)
    ? String(payload.event).trim().toUpperCase()
    : undefined;
  const fromEconomyCode = isEconomyCode(payload.economy_code)
    ? String(payload.economy_code).trim().toUpperCase()
    : undefined;
  const economyCode = fromEconomyCode || fromEventCode;

  if (!economyCode) {
    return payload;
  }

  const event =
    normalizedEvent === "impression" || economyCode === "CTS"
      ? "impression"
      : "click";

  return {
    ...payload,
    event,
    economy: true,
    economy_code: economyCode,
  };
}

export async function POST(request: Request) {
  try {
    const rawPayload = (await request.json()) as Record<string, unknown>;
    const payload = normalizeTrackPayload(rawPayload);

    const upstream = await fetch(`${ADS_CORE_URL}/api/v1/ads/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch {
    return NextResponse.json({ ok: false, ignored: true }, { status: 200 });
  }
}
