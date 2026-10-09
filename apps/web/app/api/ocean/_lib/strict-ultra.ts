type JsonRecord = Record<string, unknown>;

const STRICT_ULTRA_HEADER_VALUE = "strict-ultra-2026";

const STRICT_ULTRA_HEADERS = {
  "X-Clisonix-Profile": STRICT_ULTRA_HEADER_VALUE,
  "X-Clisonix-Routing": "deterministic",
  "X-Clisonix-Mode": "hard-profile",
} as const;

function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function clampNumber(value: unknown, fallback: number, min: number, max: number): number {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, Math.round(n)));
}

function includesIgnoreCase(value: unknown, token: string): boolean {
  return asString(value).toLowerCase().includes(token.toLowerCase());
}

function isStrictUltraRequested(payload: JsonRecord): boolean {
  if (payload.strict_ultra === true) return true;

  const directSignals = [
    payload.processing_mode,
    payload.audio_profile,
    payload.voice_stack,
    payload.vision_stack,
    payload.ultra_profile,
    payload.profile_mode,
  ];

  if (directSignals.some((signal) => includesIgnoreCase(signal, "ultra"))) {
    return true;
  }

  if (
    includesIgnoreCase(payload.grid, "nanogrid") ||
    includesIgnoreCase(payload.vision, "zeiss") ||
    includesIgnoreCase(payload.mode, "limit")
  ) {
    return true;
  }

  return false;
}

export function applyStrictUltraProfile(payload: JsonRecord): {
  enabled: boolean;
  payload: JsonRecord;
  headers: Record<string, string>;
} {
  const enabled = isStrictUltraRequested(payload);
  if (!enabled) {
    return { enabled: false, payload, headers: {} };
  }

  const profileValue = asString(payload.profile).toLowerCase();
  const profile = ["balanced", "clinical", "athlete"].includes(profileValue)
    ? profileValue
    : "clinical";

  const merged: JsonRecord = {
    ...payload,
    strict_ultra: true,
    strict_mode: true,
    deterministic_routing: true,
    processing_mode: "strict_ultra_2026",
    ultra_profile: STRICT_ULTRA_HEADER_VALUE,
    profile_mode: STRICT_ULTRA_HEADER_VALUE,
    mode: "limit",
    grid: "nanogrid_plus",
    vision: "zeiss_ultra",
    vision_stack: "zeiss_ultra",
    audio_profile: "nanogrid_zeiss_voice_ultra",
    voice_stack: "nanogrid_zeiss_ultra",
    document_profile: "nanogrid_zeiss_doc_ultra",
    profile,
    intensity: clampNumber(payload.intensity, 96, 90, 100),
    precision: clampNumber(payload.precision, 99, 95, 100),
    btl_mode: "elastic",
    btl_target_bits: -1,
    btl_target_pixels: -1,
    token_budget: -1,
    long_response: true,
    use_mega_layers: true,
    use_knowledge_seeds: true,
  };

  return {
    enabled: true,
    payload: merged,
    headers: { ...STRICT_ULTRA_HEADERS },
  };
}
