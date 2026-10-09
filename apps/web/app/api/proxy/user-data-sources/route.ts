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
    const response = await fetch(`${API_URL}/api/user/data-sources`, {
      cache: "no-store",
      headers,
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          error: "User data sources upstream returned a non-200 status",
          upstreamStatus: response.status,
        },
        { status: response.status >= 500 ? 503 : response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("User data sources fetch error:", error);
    return NextResponse.json(
      {
        error: "User data sources upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const userId = await resolveUserId(request);
    let body: Record<string, unknown> = {};
    try {
      body = (await request.json()) as Record<string, unknown>;
    } catch {
      body = {};
    }

    const normalizedType =
      typeof body.type === "string" && body.type.trim()
        ? body.type.trim().toLowerCase()
        : "api";

    const normalizedName =
      typeof body.name === "string" && body.name.trim()
        ? body.name.trim()
        : "playground-source";

    const normalizedPayload = {
      name: normalizedName,
      type: normalizedType,
      endpoint:
        typeof body.endpoint === "string" && body.endpoint.trim()
          ? body.endpoint.trim()
          : normalizedType === "api"
            ? "https://example.com"
            : null,
      api_key:
        typeof body.api_key === "string" && body.api_key.trim()
          ? body.api_key.trim()
          : null,
      config:
        body.config &&
        typeof body.config === "object" &&
        !Array.isArray(body.config)
          ? body.config
          : null,
    };

    const response = await fetch(`${API_URL}/api/user/data-sources`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-User-ID": userId,
      },
      body: JSON.stringify(normalizedPayload),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(
        {
          error:
            data?.detail ||
            data?.error ||
            "Failed to create data source upstream",
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
    console.error("User data source create error:", error);
    return NextResponse.json(
      {
        error: "User data source upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}
