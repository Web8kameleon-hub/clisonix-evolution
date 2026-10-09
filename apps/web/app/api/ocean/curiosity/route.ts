import { NextResponse } from "next/server";

const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;
const OCEAN_LOCAL_URL = "http://localhost:8030";
const OCEAN_PUBLIC_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;

function isLikelyAlbanian(text: string): boolean {
  const sample = (text || "").trim().toLowerCase();
  if (!sample) return false;
  if (/[çë]/i.test(sample)) return true;
  return /\b(pershendetje|përshëndetje|cfare|çfarë|si je|si jeni|faleminderit|shqip|shpjego|tregom|me trego|ku jemi)\b/i.test(
    sample,
  );
}

function buildOceanCandidates(): string[] {
  const ordered = [
    OCEAN_INTERNAL_URL,
    OCEAN_CORE_URL,
    OCEAN_LOCAL_URL,
    OCEAN_PUBLIC_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

function wantsChunkedStream(
  payload: Record<string, unknown>,
  acceptHeader: string | null,
): boolean {
  if (payload.stream === true) return true;
  if (typeof payload.response_mode === "string") {
    const mode = payload.response_mode.toLowerCase().trim();
    if (mode === "stream" || mode === "chunk" || mode === "chunks") {
      return true;
    }
  }

  return (acceptHeader || "").toLowerCase().includes("text/event-stream");
}

function isHeartbeatProbe(text: string): boolean {
  const normalized = (text || "").trim().toLowerCase();
  return [
    "ping",
    "pong",
    "health",
    "healthcheck",
    "health check",
    "probe",
    "latency probe",
  ].includes(normalized);
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
}

const CHAT_TIMEOUT_MS = 25000;
const STREAM_TIMEOUT_MS = 180000;

async function parseIncomingBody(
  request: Request,
): Promise<Record<string, unknown>> {
  const contentType = (request.headers.get("content-type") || "").toLowerCase();

  if (contentType.includes("application/cbor")) {
    try {
      const { default: cbor } = await import("cbor");
      const raw = await request.arrayBuffer();
      const decoded = cbor.decodeFirstSync(Buffer.from(raw));
      if (decoded && typeof decoded === "object") {
        return decoded as Record<string, unknown>;
      }
      return {};
    } catch (error) {
      throw new Error(
        `CBOR decode failed: ${error instanceof Error ? error.message : "unknown"}`,
      );
    }
  }

  const rawText = await request.text();
  const text = rawText?.trim();

  if (!text) {
    return {};
  }

  const parseCandidates = [
    text,
    text.replace(/\\"/g, '"'),
    text.replace(/^'([\s\S]*)'$/, "$1"),
    text.replace(/^"([\s\S]*)"$/, "$1"),
  ];

  for (const candidate of parseCandidates) {
    try {
      const parsed = JSON.parse(candidate) as unknown;
      if (parsed && typeof parsed === "object") {
        return parsed as Record<string, unknown>;
      }
    } catch {
      // try next candidate
    }
  }

  const messageMatch = text.match(/message\s*[:=]\s*["']([^"']+)["']/i);
  if (messageMatch?.[1]) {
    return { message: messageMatch[1] };
  }

  return { message: text };
}

// ─── HumanThinking fast-path ─────────────────────────────────────────────────
function wantsFastHumanThinkingPlan(question: string): boolean {
  const clean = question.trim();
  if (!clean) return false;
  return (
    /(deepthink|deep think)/i.test(clean) ||
    /\b(give me a plan|clear plan|action plan|roadmap)\b/i.test(clean) ||
    /\b(me jep nje plan|më jep një plan|plan te qarte|plan të qartë|plan veprimi)\b/i.test(
      clean,
    ) ||
    /\b(gib mir einen klaren plan|klaren plan|aktionsplan|fahrplan)\b/i.test(
      clean,
    )
  );
}

function resolveCallbackUrl(payload: Record<string, unknown>): string | null {
  const raw =
    typeof payload.callback_url === "string"
      ? payload.callback_url
      : typeof payload.callbackUrl === "string"
        ? payload.callbackUrl
        : "";
  const clean = raw.trim();
  return clean.length > 0 ? clean : null;
}
// ─────────────────────────────────────────────────────────────────────────────

export async function POST(request: Request) {
  try {
    const body = await parseIncomingBody(request);
    const streamMode = wantsChunkedStream(body, request.headers.get("accept"));
    const rawQuestion =
      typeof body.question === "string"
        ? body.question
        : typeof body.message === "string"
          ? body.message
          : "";
    const question = rawQuestion.trim();

    if (!question) {
      return NextResponse.json(
        { error: "Question is required" },
        { status: 400 },
      );
    }

    if (isHeartbeatProbe(question)) {
      if (streamMode) {
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                `data: ${JSON.stringify({ chunk: "pong", fast_path: true })}\n\n`,
              ),
            );
            controller.enqueue(
              new TextEncoder().encode(
                `data: ${JSON.stringify({ status: "complete", fast_path: true })}\n\n`,
              ),
            );
            controller.enqueue(new TextEncoder().encode("data: [DONE]\n\n"));
            controller.close();
          },
        });

        return new NextResponse(stream, {
          status: 200,
          headers: {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            Connection: "keep-alive",
          },
        });
      }

      return NextResponse.json(
        {
          response: "pong",
          sources: ["heartbeat_probe"],
          confidence: 1,
          query_category: "health",
          fast_path: true,
        },
        { headers: { "Content-Type": "application/json; charset=utf-8" } },
      );
    }

    // ── Callback-only fast-path (no hardcoded content) ───────────────────────
    if (wantsFastHumanThinkingPlan(question)) {
      const requestId =
        typeof body.request_id === "string" && body.request_id.trim().length > 0
          ? body.request_id.trim()
          : `cb_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
      const callbackUrl = resolveCallbackUrl(body);

      if (!callbackUrl) {
        return NextResponse.json(
          {
            error:
              "callback_url is required for async processing; request rejected",
            code: "callback_not_configured",
            request_id: requestId,
            reason: "async_processing_required",
            fast_path: true,
          },
          {
            status: 503,
            headers: { "Content-Type": "application/json; charset=utf-8" },
          },
        );
      }

      if (streamMode) {
        const enc = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(
              enc.encode(
                `data: ${JSON.stringify({ status: "accepted", mode: "callback", request_id: requestId, callback_url: callbackUrl, reason: "async_processing_required" })}\n\n`,
              ),
            );
            controller.enqueue(enc.encode("data: [DONE]\n\n"));
            controller.close();
          },
        });
        return new NextResponse(stream, {
          status: 200,
          headers: {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            Connection: "keep-alive",
          },
        });
      }
      return NextResponse.json(
        {
          status: "accepted",
          mode: "callback",
          request_id: requestId,
          callback_url: callbackUrl,
          reason: "async_processing_required",
          fast_path: true,
        },
        {
          status: 202,
          headers: { "Content-Type": "application/json; charset=utf-8" },
        },
      );
    }
    // ─────────────────────────────────────────────────────────────────────────

    const upstreamPayload: Record<string, unknown> = {
      ...body,
      message: question,
    };

    if (typeof upstreamPayload.question === "string") {
      delete upstreamPayload.question;
    }

    const rawLanguage =
      typeof upstreamPayload.language === "string"
        ? upstreamPayload.language.trim().toLowerCase()
        : "";
    if (!rawLanguage || rawLanguage === "auto" || rawLanguage === "detect") {
      delete upstreamPayload.language;
    }

    const shouldTryAlbanianDictionary =
      rawLanguage === "sq" || isLikelyAlbanian(question);

    let lastError = "No upstream available";

    for (const upstream of buildOceanCandidates()) {
      try {
        if (shouldTryAlbanianDictionary && !streamMode) {
          const dictionaryUrl = `${upstream}/api/v1/albanian/dictionary?query=${encodeURIComponent(question)}`;
          const dictionaryRes = await fetch(dictionaryUrl, {
            method: "GET",
            headers: { Accept: "application/json; charset=utf-8" },
          });

          if (dictionaryRes.ok) {
            const dictionaryData = (await dictionaryRes.json()) as Record<
              string,
              unknown
            >;
            const dictionaryResponse =
              typeof dictionaryData.response === "string"
                ? dictionaryData.response.trim()
                : "";

            if (dictionaryResponse) {
              return NextResponse.json(
                {
                  response: dictionaryResponse,
                  sources: ["albanian_dictionary"],
                  confidence: 0.98,
                  query_category: "dictionary",
                  fast_path: true,
                  upstream,
                },
                {
                  headers: {
                    "Content-Type": "application/json; charset=utf-8",
                  },
                },
              );
            }
          }
        }

        const upstreamPath = streamMode
          ? "/api/v1/chat/stream"
          : "/api/v1/chat";
        const requestPayload = JSON.stringify({
          ...upstreamPayload,
          stream: streamMode,
        });

        let res: Response;
        try {
          res = await fetchWithTimeout(
            `${upstream}${upstreamPath}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json; charset=utf-8",
                Accept: streamMode
                  ? "text/event-stream"
                  : "application/json; charset=utf-8",
              },
              body: requestPayload,
            },
            streamMode ? STREAM_TIMEOUT_MS : CHAT_TIMEOUT_MS,
          );
        } catch (error) {
          if (!streamMode) {
            const fastRes = await fetchWithTimeout(
              `${upstream}/api/v1/chat/fast`,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json; charset=utf-8",
                  Accept: "application/json; charset=utf-8",
                },
                body: requestPayload,
              },
              10000,
            );
            if (fastRes.ok) {
              res = fastRes;
            } else {
              const fastErr = await fastRes.text();
              lastError = `Primary timeout and fast fallback failed (${fastRes.status})${fastErr ? `: ${fastErr}` : ""}`;
              continue;
            }
          } else {
            lastError =
              error instanceof Error
                ? error.message
                : "Unknown stream fetch error";
            continue;
          }
        }

        if (!res.ok) {
          if (!streamMode) {
            const fastRes = await fetchWithTimeout(
              `${upstream}/api/v1/chat/fast`,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json; charset=utf-8",
                  Accept: "application/json; charset=utf-8",
                },
                body: requestPayload,
              },
              10000,
            );
            if (fastRes.ok) {
              res = fastRes;
            } else {
              const errText = await res.text();
              const fastErr = await fastRes.text();
              lastError = `Upstream ${upstream} returned ${res.status}${errText ? `: ${errText}` : ""}; fast fallback ${fastRes.status}${fastErr ? `: ${fastErr}` : ""}`;
              continue;
            }
          } else {
            const errText = await res.text();
            lastError = `Upstream ${upstream} returned ${res.status}${errText ? `: ${errText}` : ""}`;
            continue;
          }
        }

        if (streamMode && res.body) {
          return new NextResponse(res.body, {
            status: res.status,
            headers: {
              "Content-Type": "text/event-stream; charset=utf-8",
              "Cache-Control": "no-cache, no-transform",
              "X-Accel-Buffering": "no",
              Connection: "keep-alive",
            },
          });
        }

        const raw = await res.text();
        let data: Record<string, unknown> = {};
        try {
          data = JSON.parse(raw) as Record<string, unknown>;
        } catch {
          data = { response: raw };
        }

        const responseText = (data.response || data.answer || "")
          .toString()
          .trim();
        if (!responseText) {
          lastError = `Upstream ${upstream} returned empty response`;
          continue;
        }
        return NextResponse.json(
          {
            response: responseText,
            sources: data.sources || [],
            confidence: data.confidence ?? 0.5,
            query_category: data.query_category || "conversational",
            fast_path: true,
            upstream,
          },
          {
            headers: { "Content-Type": "application/json; charset=utf-8" },
          },
        );
      } catch (error) {
        lastError = error instanceof Error ? error.message : "Unknown error";
      }
    }

    return NextResponse.json(
      { error: `Ocean-Core unavailable: ${lastError}`, fast_path: true },
      {
        status: 503,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      },
    );
  } catch (error) {
    console.error("[api/ocean/curiosity] request failed:", error);
    return NextResponse.json(
      {
        error: "Ocean-Core request failed",
        details: error instanceof Error ? error.message : "Unknown error",
        fast_path: true,
      },
      {
        status: 500,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      },
    );
  }
}
