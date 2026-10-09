import { NextRequest, NextResponse } from "next/server";

/**
 * Audio Transcription API Proxy
 * Proxies audio/transcribe requests to Ocean-Core backend (Faster-Whisper)
 * This runs server-side so it can reach the internal Docker network
 */

const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;
const OCEAN_MULTIMODAL_URL =
  process.env.OCEAN_MULTIMODAL_URL ||
  "http://clisonix-ocean-core-multimodal:8033";

function resolveAudioUpstreams(): string[] {
  const upstreams = [OCEAN_MULTIMODAL_URL, OCEAN_INTERNAL_URL, OCEAN_CORE_URL]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(upstreams)];
}

async function readUpstreamPayload(
  response: Response,
): Promise<{ data: Record<string, unknown> | null; text: string }> {
  const text = await response.text();
  const trimmed = text.trim();

  if (!trimmed) {
    return { data: null, text: "" };
  }

  try {
    const parsed = JSON.parse(trimmed) as unknown;
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return { data: parsed as Record<string, unknown>, text: trimmed };
    }
  } catch {}

  return { data: null, text: trimmed };
}

function getUpstreamMessage(
  payload: { data: Record<string, unknown> | null; text: string },
  fallback: string,
): string {
  const message = payload.data?.message;
  if (typeof message === "string" && message.trim()) {
    return message.trim();
  }

  const detail = payload.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail.trim();
  }

  const error = payload.data?.error;
  if (typeof error === "string" && error.trim()) {
    return error.trim();
  }

  return payload.text || fallback;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const hasAudioPayload = Boolean(
      (typeof body?.audio_base64 === "string" && body.audio_base64.trim()) ||
      (typeof body?.audio_url === "string" && body.audio_url.trim()) ||
      (typeof body?.content === "string" && body.content.trim()) ||
      (typeof body?.payload === "string" && body.payload.trim()),
    );

    if (!hasAudioPayload) {
      return NextResponse.json(
        {
          status: "ok",
          module: "audio",
          mode: "readiness",
          message:
            "Audio transcription endpoint is reachable. Provide `audio_base64` or a valid audio payload to run a real transcription.",
          accepted_inputs: ["audio_base64", "audio_url"],
        },
        { status: 200 },
      );
    }

    // Forward auth headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
    if (userId) {
      headers["X-User-ID"] = userId;
      headers["X-User-Id"] = userId;
    }

    const upstreams = resolveAudioUpstreams();
    const candidatePaths = ["/api/v1/audio/transcribe", "/api/v1/audio"];

    let response: Response | null = null;

    for (const upstream of upstreams) {
      for (const path of candidatePaths) {
        const current = await fetch(`${upstream}${path}`, {
          method: "POST",
          headers,
          body: JSON.stringify(body),
        });

        if (current.status !== 404) {
          response = current;
          break;
        }

        response = current;
      }

      if (response && response.status !== 404) {
        break;
      }
    }

    if (!response) {
      throw new Error("Ocean audio upstream is not reachable");
    }

    const payload = await readUpstreamPayload(response);

    if (response.status === 404) {
      return NextResponse.json(
        {
          status: "error",
          message: "Ocean audio module not found.",
        },
        { status: 404 },
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        {
          status: "error",
          message: getUpstreamMessage(
            payload,
            "Ocean audio transcription request failed.",
          ),
        },
        { status: response.status },
      );
    }

    const data =
      payload.data ||
      (payload.text
        ? {
            transcript: payload.text,
          }
        : null);

    if (!data) {
      return NextResponse.json(
        {
          status: "error",
          message: "Ocean audio returned an empty response.",
        },
        { status: 502 },
      );
    }

    const accept = request.headers.get("accept") || "";
    if (accept.includes("application/cbor")) {
      const { default: cbor } = await import("cbor");
      const encoded = cbor.encode(data);
      return new NextResponse(encoded as unknown as BodyInit, {
        status: response.status,
        headers: { "Content-Type": "application/cbor" },
      });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[Audio Proxy] Error:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Audio transcription service unavailable. Please try again.",
      },
      { status: 502 },
    );
  }
}
