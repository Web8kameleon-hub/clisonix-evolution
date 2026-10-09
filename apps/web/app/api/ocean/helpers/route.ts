/**
 * API Endpoint: /api/ocean/helpers
 * Real-upstream helper gateway (Ocean-Core only)
 */

import { NextRequest, NextResponse } from 'next/server';
import { validateQuestion } from "../../../lib/oceanHelpers";

const PRIMARY_OCEAN_URL = process.env.OCEAN_CORE_URL;
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_LOCAL_URL = "http://localhost:8030";
const PUBLIC_OCEAN_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;
const isDev = process.env.NODE_ENV !== "production";

type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

function buildUpstreamCandidates(): string[] {
  const ordered = [
    OCEAN_INTERNAL_URL,
    PRIMARY_OCEAN_URL,
    isDev ? OCEAN_LOCAL_URL : undefined,
    PUBLIC_OCEAN_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

function normalizeIncomingMessages(raw: unknown): ChatMessage[] {
  if (!Array.isArray(raw)) return [];

  return raw
    .map((item) => {
      const role =
        item && typeof item === "object" && "role" in item
          ? String((item as { role?: unknown }).role || "")
          : "";
      const content =
        item && typeof item === "object" && "content" in item
          ? String((item as { content?: unknown }).content || "")
          : "";

      if (!content.trim()) return null;

      const normalizedRole: ChatMessage["role"] =
        role === "system" || role === "assistant" || role === "user"
          ? role
          : "user";

      return { role: normalizedRole, content: content.trim() };
    })
    .filter((item): item is ChatMessage => Boolean(item));
}

function makeSsePayload(text: string): Uint8Array {
  return new TextEncoder().encode(
    `data: ${JSON.stringify({ chunk: text })}\n\n`,
  );
}

function makeDoneSsePayload(): Uint8Array {
  return new TextEncoder().encode("data: [DONE]\\n\\n");
}

function sseHeaders(): Headers {
  return new Headers({
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
    "Content-Encoding": "identity",
  });
}

function makeUnavailableSseResponse(reason: string): Response {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(
        makeSsePayload(`Ocean-Core stream unavailable: ${reason}`),
      );
      controller.enqueue(makeDoneSsePayload());
      controller.close();
    },
  });

  return new Response(stream, { headers: sseHeaders(), status: 503 });
}

/**
 * GET /api/ocean/helpers
 * Returns helper registry and health status
 */
async function handleGetRequest() {
  return NextResponse.json({
    status: "ok",
    message: "Ocean Helpers Gateway (real upstream only)",
    version: "2.0.0",
    engine: {
      source: "ocean-core",
      real_services_only: true,
    },
    endpoints: {
      query: "POST /api/ocean/helpers",
      registry: "GET /api/ocean/helpers",
    },
  });
}

/**
 * POST /api/ocean/helpers
 * Body: { question: string, debug?: boolean, stream?: boolean }
 */
async function handlePostRequest(request: NextRequest) {
  try {
    const body = await request.json();
    const { question, stream = false } = body;

    if (!question || typeof question !== 'string') {
      return NextResponse.json(
        {
          error: 'Invalid request',
          message: '"question" field is required and must be a string',
        },
        { status: 400 }
      );
    }

    // Security validation
    const { safe, reason } = validateQuestion(question);
    if (!safe) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          message: reason,
          blocked: true,
        },
        { status: 403 }
      );
    }

    const incomingMessages = normalizeIncomingMessages(body.messages);

    if (stream) {
      return handleStreamingResponse(question, incomingMessages);
    }

    let upstreamResponse: Response | null = null;
    for (const upstream of buildUpstreamCandidates()) {
      try {
        const candidateResponse = await fetch(`${upstream}/api/v1/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: question,
            query: question,
            messages: incomingMessages,
            enable_companion: true,
            enable_feeling_layer: true,
          }),
        });

        if (!candidateResponse.ok) {
          continue;
        }

        upstreamResponse = candidateResponse;
        break;
      } catch {
        // try next upstream
      }
    }

    if (!upstreamResponse) {
      return NextResponse.json(
        {
          error: "Ocean-Core service unavailable",
          message: "No real upstream response available",
        },
        { status: 503 },
      );
    }

    const result = await upstreamResponse.json();

    return NextResponse.json({
      ok: true,
      engine: {
        source: "ocean-core",
        real_services_only: true,
      },
      result: {
        response: result.response,
        confidence: result.confidence,
        sources: result.sources || [],
        query_category: result.query_category || "general",
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('[Ocean Helpers Error]', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * Stream response (SSE format)
 * Compatible with Ocean stream protocol
 */
function handleStreamingResponse(
  question: string,
  incomingMessages: ChatMessage[],
) {
  const connectStream = async (): Promise<Response | null> => {
    for (const upstream of buildUpstreamCandidates()) {
      try {
        const response = await fetch(`${upstream}/api/v1/chat/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify({
            message: question,
            query: question,
            messages: incomingMessages,
            enable_companion: true,
            enable_feeling_layer: true,
          }),
        });

        if (response.ok && response.body) {
          return response;
        }
      } catch {
        // try next upstream
      }
    }
    return null;
  };

  return connectStream().then((upstream) => {
    if (!upstream || !upstream.body) {
      return makeUnavailableSseResponse("No upstream stream available");
    }

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        const reader = upstream.body!.getReader();
        let emittedChunk = false;

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            if (!value) continue;
            emittedChunk = true;
            controller.enqueue(value);
          }
        } catch (streamError) {
          const errorMessage =
            streamError instanceof Error
              ? streamError.message
              : "Unknown stream error";
          if (!emittedChunk) {
            controller.enqueue(
              makeSsePayload(`Ocean-Core stream relay error: ${errorMessage}`),
            );
            controller.enqueue(makeDoneSsePayload());
          }
        } finally {
          controller.close();
          reader.releaseLock();
        }
      },
    });

    return new Response(stream, { headers: sseHeaders() });
  });
}

/**
 * Unified request handler
 */
export async function GET(request: NextRequest) {
  return handleGetRequest();
}

export async function POST(request: NextRequest) {
  return handlePostRequest(request);
}

/**
 * OPTIONS for CORS pre-flight
 */
export async function OPTIONS() {
  return NextResponse.json({ ok: true }, { status: 200 });
}
