/**
 * SPECIALIZED CHAT PROXY
 * Routes specialized chat requests through Next.js to Ocean-Core
 * so the browser never needs direct access to the backend.
 */

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const isDev = process.env.NODE_ENV !== "production";
const PRIMARY_OCEAN_URL = process.env.OCEAN_CORE_URL;
const OCEAN_INTERNAL_URL = process.env.OCEAN_INTERNAL_URL;
const PUBLIC_OCEAN_URL =
  process.env.NEXT_PUBLIC_OCEAN_API_URL || "https://api.clisonix.com";
const INTERNAL_OCEAN_URL = "http://clisonix-ocean-core:8030";
const LOCAL_OCEAN_URL = "http://localhost:8030";
const REQUEST_TIMEOUT_MS = Number(
  process.env.OCEAN_SPECIALIZED_TIMEOUT_MS || "8000",
);
const FALLBACK_TIMEOUT_MS = Number(
  process.env.OCEAN_SPECIALIZED_FALLBACK_TIMEOUT_MS || "12000",
);
const NANOGRIDATA_FRAME_HEADER_BYTES = 14;
const NANOGRIDATA_CELL_BYTES = 16;

const DOMAIN_ALIASES: Record<string, string> = {
  neuro: "neuroscience",
  ai: "ai_ml",
  bio: "biotech",
  data: "data_science",
};

type NanogridMetrics = {
  protocol: "nanogridata-v1";
  header_bytes: number;
  cell_bytes: number;
  payload_bytes: number;
  cells: number;
  frame_bytes: number;
  overhead_bytes: number;
  efficiency: number;
};

type BtlMetrics = {
  bits: number;
  pixels: number;
  cell_score: number;
  grid_score: number;
  btl_score: number;
  unit: "BTL";
  formula: "BTL=(w_bits*bits+w_pixels*pixels); grid_score=BTL/cells";
  nanogrid: NanogridMetrics;
};

type MetricsMode = "btl" | "tokens" | "hybrid";

function resolveMetricsMode(
  rawMode: unknown,
  messageText: string,
): MetricsMode {
  if (typeof rawMode === "string") {
    const normalized = rawMode.trim().toLowerCase();
    if (["token", "tokens"].includes(normalized)) return "tokens";
    if (["hybrid", "both", "all"].includes(normalized)) return "hybrid";
    if (
      ["btl", "bits", "pixels", "nanogrid", "nanogridata"].includes(normalized)
    ) {
      return "btl";
    }
  }

  if (/\btokens?\b/i.test(messageText || "")) {
    return "tokens";
  }

  return "tokens";
}

function deriveTokenMetrics(text: string): { tokens: number } {
  const normalized = (text || "").trim();
  if (!normalized) return { tokens: 0 };
  return { tokens: normalized.split(/\s+/).length };
}

function deriveBtlMetrics(text: string): BtlMetrics {
  const normalized = text || "";
  const payloadBytes = Buffer.byteLength(normalized, "utf8");
  const bits = payloadBytes * 8;
  const pixels = normalized.length;
  const wBits = Number.parseFloat(process.env.BTL_W_BITS || "1") || 1;
  const wPixels = Number.parseFloat(process.env.BTL_W_PIXELS || "0.25") || 0.25;
  const cells = Math.max(1, Math.ceil(payloadBytes / NANOGRIDATA_CELL_BYTES));
  const frameBytes =
    NANOGRIDATA_FRAME_HEADER_BYTES + cells * NANOGRIDATA_CELL_BYTES;
  const overheadBytes = Math.max(0, frameBytes - payloadBytes);
  const efficiency =
    frameBytes > 0 ? Number((payloadBytes / frameBytes).toFixed(4)) : 0;
  const cellScore = Number((wBits * bits + wPixels * pixels).toFixed(3));
  const gridScore = Number((cellScore / cells).toFixed(3));

  return {
    bits,
    pixels,
    cell_score: cellScore,
    grid_score: gridScore,
    btl_score: cellScore,
    unit: "BTL",
    formula: "BTL=(w_bits*bits+w_pixels*pixels); grid_score=BTL/cells",
    nanogrid: {
      protocol: "nanogridata-v1",
      header_bytes: NANOGRIDATA_FRAME_HEADER_BYTES,
      cell_bytes: NANOGRIDATA_CELL_BYTES,
      payload_bytes: payloadBytes,
      cells,
      frame_bytes: frameBytes,
      overhead_bytes: overheadBytes,
      efficiency,
    },
  };
}

function normalizeDomain(domain?: string): string | undefined {
  if (!domain) return undefined;
  const normalized = domain.trim().toLowerCase();
  return DOMAIN_ALIASES[normalized] || normalized;
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number = REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

function buildUpstreamCandidates(): string[] {
  return [
    OCEAN_INTERNAL_URL,
    INTERNAL_OCEAN_URL,
    PRIMARY_OCEAN_URL,
    PUBLIC_OCEAN_URL,
    isDev ? LOCAL_OCEAN_URL : undefined,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));
}

function extractAnswerText(data: Record<string, unknown>): string | null {
  const answer =
    (typeof data.response === "string" && data.response.trim()) ||
    (typeof data.answer === "string" && data.answer.trim()) ||
    (typeof data.fused_answer === "string" && data.fused_answer.trim()) ||
    "";

  return answer || null;
}

function isDatetimeOnlyResponse(data: Record<string, unknown>): boolean {
  const domain = String(data.domain || data.query_category || "").toLowerCase();
  const sourcesRaw = data.sources || data.sources_cited;
  const sources = Array.isArray(sourcesRaw)
    ? sourcesRaw.map((item) => String(item).toLowerCase())
    : [];

  const answer = extractAnswerText(data) || "";
  const normalizedAnswer = answer.toLowerCase();

  const looksLikeDatetimeHeader =
    normalizedAnswer.includes("today is") ||
    normalizedAnswer.includes("time:") ||
    normalizedAnswer.includes("conversational_datetime") ||
    normalizedAnswer.includes("domain: fast_local_reasoning");

  return (
    domain === "fast_local_reasoning" ||
    sources.includes("conversational_datetime") ||
    looksLikeDatetimeHeader
  );
}

async function trySpecializedOrChat(
  upstream: string,
  payload: Record<string, unknown>,
) {
  const message = String(payload.message || payload.query || "").trim();
  const safePayload = {
    ...payload,
    long_response: true,
    // Elastic mode: no artificial cap, budget expressed via BTL semantics.
    btl_mode: "elastic",
    btl_target_bits: -1,
    btl_target_pixels: -1,
  };

  try {
    const specializedRes = await fetchWithTimeout(
      `${upstream}/api/v1/chat/specialized`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(safePayload),
      },
    );

    if (specializedRes.ok) {
      const data = await specializedRes.json();
      return { ok: true as const, data, source: "specialized" as const };
    }
  } catch {
    // fall through to standard chat
  }

  const binaryPreferred =
    payload.response_format === "cbor" ||
    payload.response_format === "cbor2" ||
    payload.response_format === "binary" ||
    payload.binary === true;

  if (binaryPreferred) {
    const { default: cbor } = await import("cbor");
    const binaryRes = await fetchWithTimeout(
      `${upstream}/api/v1/chat/binary`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/cbor",
          Accept: "application/cbor, application/json",
        },
        body: new Uint8Array(
          cbor.encode({
            ...safePayload,
            message,
            query: message,
            response_format: "cbor2",
          }),
        ),
      },
      FALLBACK_TIMEOUT_MS,
    );

    if (binaryRes.ok) {
      const contentType = (binaryRes.headers.get("content-type") || "").toLowerCase();
      if (contentType.includes("application/cbor")) {
        const decoded = cbor.decodeFirstSync(Buffer.from(await binaryRes.arrayBuffer()));
        return { ok: true as const, data: decoded, source: "binary" as const };
      }

      const maybeJson = await binaryRes.text();
      try {
        return {
          ok: true as const,
          data: JSON.parse(maybeJson),
          source: "binary" as const,
        };
      } catch {
        return {
          ok: true as const,
          data: { response: maybeJson },
          source: "binary" as const,
        };
      }
    }
  }

  const fastChatRes = await fetchWithTimeout(
    `${upstream}/api/v1/chat/fast`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...safePayload,
        message,
        query: message,
      }),
    },
    FALLBACK_TIMEOUT_MS,
  );

  if (fastChatRes.ok) {
    const data = await fastChatRes.json();
    return { ok: true as const, data, source: "chat_fast" as const };
  }

  const chatRes = await fetchWithTimeout(
    `${upstream}/api/v1/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...safePayload,
        message,
        query: message,
      }),
    },
    FALLBACK_TIMEOUT_MS,
  );

  if (!chatRes.ok) {
    const errorText = await chatRes.text();
    throw new Error(`Chat error ${chatRes.status}: ${errorText}`);
  }

  const data = await chatRes.json();
  return { ok: true as const, data, source: "chat" as const };
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const message = String(body.message || body.query || "").trim();
    const metricsMode = resolveMetricsMode(body.metrics_mode, message);
    const domain = normalizeDomain(
      typeof body.domain === "string" ? body.domain : undefined,
    );
    const language =
      typeof body.language === "string"
        ? body.language
        : typeof body.preferred_language === "string"
          ? body.preferred_language
          : undefined;

    if (!message) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 },
      );
    }

    const candidates = buildUpstreamCandidates();
    const payload = {
      ...body,
      message,
      query: message,
      domain,
      language,
      preferred_language: language,
      processing_mode: "deep",
      long_response: true,
      metrics_mode: metricsMode,
      specialized: true,
      messages: Array.isArray(body.messages) ? body.messages : undefined,
    } as Record<string, unknown>;

    let lastError = "No upstream candidates configured";

    for (const upstream of candidates) {
      try {
        const result = await trySpecializedOrChat(upstream, payload);
        if (result.ok) {
          const resultData = (result.data || {}) as Record<string, unknown>;
          const answerText = extractAnswerText(resultData);
          if (!answerText) {
            lastError = `Empty answer from ${upstream} (${result.source})`;
            continue;
          }

          if (isDatetimeOnlyResponse(resultData)) {
            lastError = `Datetime-only response from ${upstream} (${result.source})`;
            continue;
          }

          return NextResponse.json({
            ...resultData,
            response: answerText,
            answer:
              typeof resultData.answer === "string"
                ? resultData.answer
                : answerText,
            ...(metricsMode === "tokens" ? deriveTokenMetrics(answerText) : {}),
            ...(metricsMode !== "tokens"
              ? {
                  btl: deriveBtlMetrics(answerText),
                }
              : {}),
            domain: domain || resultData.domain || resultData.query_category,
            upstream,
            route_source: result.source,
            metrics_mode: metricsMode,
          });
        }
      } catch (error) {
        lastError =
          error instanceof Error ? error.message : "Unknown upstream error";
      }
    }

    return NextResponse.json(
      {
        error: "Ocean Core unavailable",
        details: lastError,
        response:
          "⚠️ Specialized chat timed out or Ocean Core is temporarily unavailable. Please try again in a few seconds.",
        domain: domain || "general",
        confidence: 0,
      },
      { status: 502 },
    );
  } catch {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

export async function GET() {
  const candidates = buildUpstreamCandidates();

  for (const upstream of candidates) {
    try {
      const res = await fetchWithTimeout(
        `${upstream}/api/v1/status`,
        {
          method: "GET",
        },
        5000,
      );
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json({ status: "online", upstream, ...data });
      }
    } catch {
      // try next upstream
    }
  }

  return NextResponse.json({ status: "offline" }, { status: 503 });
}
