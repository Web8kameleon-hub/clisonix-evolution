import { NextRequest, NextResponse } from "next/server";

/**
 * Voice Conversation API Proxy
 * Full pipeline: Audio In → STT → LLM → TTS → Audio Out
 *
 * This enables complete voice-to-voice conversations with the AI
 */

const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;

function resolveOceanUpstream(): string {
  const upstream = (OCEAN_INTERNAL_URL || OCEAN_CORE_URL || "").trim();
  if (!upstream) {
    throw new Error("Ocean voice upstream is not configured");
  }
  return upstream.replace(/\/+$/, "");
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate input
    if (!body.audio_base64 || typeof body.audio_base64 !== "string") {
      return NextResponse.json(
        { status: "error", message: "Audio data is required (base64 encoded)" },
        { status: 400 }
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

    const upstream = resolveOceanUpstream();
    const response = await fetch(`${upstream}/api/v1/voice/conversation`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        audio_base64: body.audio_base64,
        language: body.language || "auto",
        voice: body.voice,
        curiosity_level: body.curiosity_level || "curious",
        user_id: userId,
      }),
    });

    if (response.status === 404) {
      return NextResponse.json(
        { status: "error", message: "Ocean voice module not found." },
        { status: 404 },
      );
    }

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Voice Conversation Proxy] Backend error:", errorText);

      let message = "Voice conversation failed";
      try {
        const parsed = JSON.parse(errorText);
        message = parsed?.detail || parsed?.message || message;
      } catch {
        if (errorText?.trim()) {
          message = errorText;
        }
      }

      return NextResponse.json(
        { status: "error", message },
        { status: response.status },
      );
    }

    // Stream audio response back to client with metadata
    const audioData = await response.arrayBuffer();

    return new NextResponse(audioData, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Length": audioData.byteLength.toString(),
        "X-Transcript": response.headers.get("X-Transcript") || "",
        "X-Response-Text": response.headers.get("X-Response-Text") || "",
        "X-Processing-Time": response.headers.get("X-Processing-Time") || "0s",
        "X-STT-Time": response.headers.get("X-STT-Time") || "0s",
        "X-LLM-Time": response.headers.get("X-LLM-Time") || "0s",
        "X-TTS-Time": response.headers.get("X-TTS-Time") || "0s",
        "X-Voice-Used": response.headers.get("X-Voice-Used") || "unknown",
        "X-Detected-Language": response.headers.get("X-Detected-Language") || "en",
      },
    });
  } catch (error) {
    console.error("[Voice Conversation Proxy] Error:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Voice conversation service unavailable. Please try again.",
      },
      { status: 502 }
    );
  }
}
