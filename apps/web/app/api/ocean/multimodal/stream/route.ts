import { NextRequest, NextResponse } from "next/server";

const OCEAN_MULTIMODAL_URL =
  process.env.OCEAN_MULTIMODAL_URL ||
  "http://clisonix-ocean-core-multimodal:8033";

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };
    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
    if (userId) {
      headers["X-User-ID"] = userId;
    }

    const upstream = await fetch(
      `${OCEAN_MULTIMODAL_URL.replace(/\/+$/, "")}/api/v1/multimodal/stream`,
      {
        method: "POST",
        headers,
        body,
        signal: request.signal,
        cache: "no-store",
      },
    );

    if (!upstream.ok || !upstream.body) {
      const detail = (await upstream.text()).trim();
      return NextResponse.json(
        {
          status: "error",
          message: detail || "Ocean multimodal stream is unavailable",
        },
        { status: upstream.status || 502 },
      );
    }

    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    console.error("[Ocean Multimodal Stream] Error:", error);
    return NextResponse.json(
      { status: "error", message: "Ocean multimodal stream is unavailable" },
      { status: 503 },
    );
  }
}
