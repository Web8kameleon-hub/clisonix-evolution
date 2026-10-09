export type EconomyCode =
  | "CLK"
  | "CLC"
  | "CTC"
  | "CTA"
  | "CTD"
  | "CTS"
  | "CTG"
  | "CTR"
  | "CTU"
  | "CTP"
  | "CTF";

export interface EconomyTrackPayload {
  economy_code: EconomyCode;
  event?: string;
  slot?: string;
  provider?: string;
  placement_id?: string;
  page?: string;
  route?: string;
  value?: number;
  currency?: string;
  metadata?: Record<string, unknown>;
}

const isDev = process.env.NODE_ENV === "development";
const ADS_CORE_URL =
  process.env.ADS_CORE_URL ||
  (isDev ? "http://localhost:8096" : "http://clisonix-ads-core:8096");

function eventFromCode(code: EconomyCode): string {
  if (code === "CTS") return "impression";
  return "click";
}

function toBody(payload: EconomyTrackPayload) {
  return {
    event: payload.event || eventFromCode(payload.economy_code),
    economy: true,
    economy_code: payload.economy_code,
    slot: payload.slot || "economy",
    provider: payload.provider || "clisonix",
    placement_id: payload.placement_id || payload.economy_code,
    page:
      payload.page ||
      (typeof window !== "undefined" ? window.location.pathname : undefined),
    route: payload.route,
    value: payload.value,
    currency: payload.currency,
    metadata: payload.metadata,
  };
}

export async function trackEconomy(payload: EconomyTrackPayload) {
  try {
    await fetch("/api/ads/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toBody(payload)),
      keepalive: true,
    });
  } catch {
    // no-op
  }
}

export async function trackEconomyServer(payload: EconomyTrackPayload) {
  try {
    await fetch(`${ADS_CORE_URL}/api/v1/ads/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toBody(payload)),
      cache: "no-store",
    });
  } catch {
    // no-op
  }
}
