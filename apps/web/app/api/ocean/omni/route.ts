import { NextRequest, NextResponse } from "next/server";

type OmniAction =
  | "realtime_token"
  | "voice"
  | "audio_transcribe"
  | "vision"
  | "document"
  | "tts"
  | "web_browse"
  | "web_search"
  | "social_status"
  | "social_connect";

const ACTIONS: OmniAction[] = [
  "realtime_token",
  "voice",
  "audio_transcribe",
  "vision",
  "document",
  "tts",
  "web_browse",
  "web_search",
  "social_status",
  "social_connect",
];

function getOrigin(request: NextRequest): string {
  const host = request.headers.get("x-forwarded-host") || request.headers.get("host") || "localhost:3000";
  const proto = request.headers.get("x-forwarded-proto") || "http";
  return `${proto}://${host}`;
}

async function readUpstreamJsonOrText(
  response: Response,
): Promise<{ data: Record<string, unknown> | null; text: string }> {
  const text = (await response.text()).trim();
  if (!text) {
    return { data: null, text: "" };
  }

  try {
    const parsed = JSON.parse(text) as unknown;
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return { data: parsed as Record<string, unknown>, text };
    }
  } catch {
  }

  return { data: null, text };
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

async function forwardJsonResponse(
  upstream: Response,
  fallback: string,
): Promise<NextResponse> {
  const payload = await readUpstreamJsonOrText(upstream);
  if (payload.data) {
    return NextResponse.json(payload.data, { status: upstream.status });
  }

  return NextResponse.json(
    upstream.ok
      ? { text: payload.text }
      : { status: "error", message: getUpstreamMessage(payload, fallback) },
    { status: upstream.status || 502 },
  );
}

export async function GET(request: NextRequest) {
  const origin = getOrigin(request);

  return NextResponse.json({
    status: "ok",
    hub: "ocean-omni",
    description:
      "Unified API for realtime voice/video, multimodal processing (docs/images/scripts/music) and social connections.",
    actions: ACTIONS,
    endpoints: {
      realtime: `${origin}/api/ocean/realtime`,
      voice: `${origin}/api/ocean/voice`,
      audio: `${origin}/api/ocean/audio`,
      vision: `${origin}/api/ocean/vision`,
      document: `${origin}/api/ocean/document`,
      tts: `${origin}/api/ocean/tts`,
      webReader: `${origin}/api/ocean/web-reader`,
      social: `${origin}/api/ocean/social`,
    },
    mediaSupport: {
      camera: true,
      microphone: true,
      screen: true,
      documents: true,
      images: true,
      scripts: true,
      music: true,
    },
    socialPlatforms: ["youtube", "tiktok", "instagram", "x", "linkedin", "facebook"],
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const action = String(body.action || "") as OmniAction;

    if (!ACTIONS.includes(action)) {
      return NextResponse.json(
        {
          status: "error",
          message: "Unknown action",
          supported: ACTIONS,
        },
        { status: 400 },
      );
    }

    const origin = getOrigin(request);
    const forwardHeaders: Record<string, string> = {
      "Content-Type": "application/json",
    };

    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
    if (userId) {
      forwardHeaders["X-User-ID"] = userId;
      forwardHeaders["X-User-Id"] = userId;
    }

    if (action === "social_status") {
      const upstream = await fetch(`${origin}/api/ocean/social`, {
        method: "GET",
        headers: forwardHeaders,
        cache: "no-store",
      });
      return await forwardJsonResponse(upstream, "Ocean social status request failed.");
    }

    if (action === "social_connect") {
      const upstream = await fetch(`${origin}/api/ocean/social`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify({ platform: body.platform }),
      });
      return await forwardJsonResponse(upstream, "Ocean social connect request failed.");
    }

    if (action === "realtime_token") {
      const upstream = await fetch(`${origin}/api/ocean/realtime`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify({
          room: body.room,
          identity: body.identity,
          name: body.name,
        }),
      });
      return await forwardJsonResponse(upstream, "Ocean realtime token request failed.");
    }

    if (action === "voice") {
      const upstream = await fetch(`${origin}/api/ocean/voice`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify({
          audio_base64: body.audio_base64,
          language: body.language,
          voice: body.voice,
          curiosity_level: body.curiosity_level,
        }),
      });

      const arrayBuffer = await upstream.arrayBuffer();
      return new NextResponse(arrayBuffer, {
        status: upstream.status,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "audio/mpeg",
          "X-Transcript": upstream.headers.get("X-Transcript") || "",
          "X-Response-Text": upstream.headers.get("X-Response-Text") || "",
          "X-Voice-Used": upstream.headers.get("X-Voice-Used") || "",
        },
      });
    }

    if (action === "audio_transcribe") {
      const upstream = await fetch(`${origin}/api/ocean/audio`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify(body.payload || body),
      });
      return await forwardJsonResponse(upstream, "Ocean audio transcription request failed.");
    }

    if (action === "vision") {
      const upstream = await fetch(`${origin}/api/ocean/vision`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify(body.payload || body),
      });
      return await forwardJsonResponse(upstream, "Ocean vision request failed.");
    }

    if (action === "document") {
      const upstream = await fetch(`${origin}/api/ocean/document`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify(body.payload || body),
      });
      return await forwardJsonResponse(upstream, "Ocean document request failed.");
    }

    if (action === "tts") {
      const upstream = await fetch(`${origin}/api/ocean/tts`, {
        method: "POST",
        headers: forwardHeaders,
        body: JSON.stringify({
          text: body.text,
          language: body.language,
          voice: body.voice,
          rate: body.rate,
          pitch: body.pitch,
        }),
      });

      const arrayBuffer = await upstream.arrayBuffer();
      return new NextResponse(arrayBuffer, {
        status: upstream.status,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "audio/mpeg",
          "X-Voice-Used": upstream.headers.get("X-Voice-Used") || "",
          "X-Processing-Time": upstream.headers.get("X-Processing-Time") || "",
        },
      });
    }

    if (action === "web_browse") {
      const query = new URLSearchParams({
        action: "browse",
        url: String(body.url || ""),
        max_chars: String(body.max_chars || "10000"),
      });
      const upstream = await fetch(`${origin}/api/ocean/web-reader?${query.toString()}`, {
        method: "GET",
        headers: forwardHeaders,
        cache: "no-store",
      });
      return await forwardJsonResponse(upstream, "Ocean web browse request failed.");
    }

    const query = new URLSearchParams({
      action: "search",
      q: String(body.query || ""),
      num: String(body.num || "5"),
    });
    const upstream = await fetch(`${origin}/api/ocean/web-reader?${query.toString()}`, {
      method: "GET",
      headers: forwardHeaders,
      cache: "no-store",
    });
    return await forwardJsonResponse(upstream, "Ocean web search request failed.");
  } catch (error) {
    console.error("[Ocean Omni] Error:", error);
    return NextResponse.json(
      { status: "error", message: "Ocean Omni request failed" },
      { status: 500 },
    );
  }
}
