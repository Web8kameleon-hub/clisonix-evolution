import { NextRequest, NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";

const LIVEKIT_API_KEY = process.env.LIVEKIT_API_KEY || "";
const LIVEKIT_API_SECRET = process.env.LIVEKIT_API_SECRET || "";
const LIVEKIT_URL = process.env.NEXT_PUBLIC_LIVEKIT_URL || process.env.LIVEKIT_URL || "";

export async function POST(request: NextRequest) {
  try {
    if (!LIVEKIT_API_KEY || !LIVEKIT_API_SECRET || !LIVEKIT_URL) {
      return NextResponse.json(
        {
          status: "degraded",
          provider: "livekit",
          configured: false,
          token: null,
          url: LIVEKIT_URL || null,
          message:
            "LiveKit configuration is missing. Set LIVEKIT_API_KEY, LIVEKIT_API_SECRET and NEXT_PUBLIC_LIVEKIT_URL/LIVEKIT_URL.",
        },
        { status: 200 },
      );
    }

    const body = await request.json().catch(() => ({}));
    const room = String(body.room || "ocean-live");
    const identityRaw =
      body.identity ||
      body.user_id ||
      request.headers.get("X-User-ID") ||
      request.headers.get("X-User-Id");

    if (!identityRaw || String(identityRaw).trim().length === 0) {
      return NextResponse.json(
        {
          status: "error",
          provider: "livekit",
          message:
            "Missing identity. Provide body.identity or X-User-ID header.",
        },
        { status: 422 },
      );
    }

    const identity = String(identityRaw).trim();
    const participantName = String(body.name || identity);

    const token = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, {
      identity,
      name: participantName,
      ttl: "1h",
    });

    token.addGrant({
      room,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const jwt = await token.toJwt();

    return NextResponse.json({
      status: "ok",
      provider: "livekit",
      room,
      identity,
      name: participantName,
      url: LIVEKIT_URL,
      token: jwt,
      capabilities: {
        audio: true,
        video: true,
        screen: true,
        dataChannel: true,
      },
    });
  } catch (error) {
    console.error("[Ocean Realtime] token error", error);
    return NextResponse.json(
      { status: "error", message: "Realtime token generation failed" },
      { status: 500 },
    );
  }
}
