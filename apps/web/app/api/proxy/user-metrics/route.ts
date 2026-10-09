import { NextRequest, NextResponse } from "next/server";
import { getUserHeaders, resolveUserId } from "../../_utils/user-identity";
import { LIVE_CACHE_HEADERS } from "../../_utils/live-cache";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const API_URL =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";

export async function GET(request: NextRequest) {
  try {
    const headers = await getUserHeaders(request);
    const response = await fetch(`${API_URL}/api/user/metrics`, {
      cache: "no-store",
      headers,
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          error: "User metrics upstream returned a non-200 status",
          upstreamStatus: response.status,
        },
        { status: response.status >= 500 ? 503 : response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("User metrics fetch error:", error);
    return NextResponse.json(
      {
        error: "User metrics upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const userId = await resolveUserId(request);
    const body = await request.json();

    const response = await fetch(`${API_URL}/api/user/metrics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-User-ID": userId,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(
        {
          error:
            data?.detail || data?.error || "Failed to create metric upstream",
          upstreamStatus: response.status,
        },
        { status: response.status >= 500 ? 503 : response.status },
      );
    }

    return NextResponse.json(data, {
      status: response.status,
      headers: LIVE_CACHE_HEADERS,
    });
  } catch (error) {
    console.error("User metric create error:", error);
    return NextResponse.json(
      {
        error: "User metrics upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}
