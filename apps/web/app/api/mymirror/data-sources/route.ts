import { NextRequest, NextResponse } from "next/server";
import { LIVE_CACHE_HEADERS } from "../../_utils/live-cache";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const API_URL =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";

export async function GET(request: NextRequest) {
  try {
    const startedAt = Date.now();
    const controller = new AbortController();
    const timeoutHandle = setTimeout(() => controller.abort(), 4500);
    const res = await fetch(`${API_URL}/api/mymirror/data-sources`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    clearTimeout(timeoutHandle);

    if (!res.ok) {
      return NextResponse.json(
        {
          error: "User data sources upstream returned a non-200 status",
          upstreamStatus: res.status,
        },
        { status: res.status >= 500 ? 503 : res.status },
      );
    }

    const data = await res.json().catch(() => ({}));
    const sources = Array.isArray(data.sources) ? data.sources : [];
    const active =
      typeof data.active === "number"
        ? data.active
        : sources.filter(
            (source: Record<string, unknown>) => source?.status === "active",
          ).length;

    return NextResponse.json(
      {
        meta: {
          fetched_at: new Date().toISOString(),
          upstream: `${API_URL}/api/mymirror/data-sources`,
          upstream_latency_ms: Date.now() - startedAt,
        },
        sources,
        count: typeof data.count === "number" ? data.count : sources.length,
        active,
        stats: data.stats ?? null,
      },
      { status: 200, headers: LIVE_CACHE_HEADERS },
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "User data sources upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));

  try {
    const res = await fetch(`${API_URL}/api/mymirror/data-sources`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json().catch(() => ({ ok: true }));
      return NextResponse.json(data, {
        status: 200,
        headers: LIVE_CACHE_HEADERS,
      });
    }

    const error = await res.json().catch(() => null);
    return NextResponse.json(
      {
        error:
          error?.detail ||
          error?.error ||
          "Failed to create data source upstream",
        upstreamStatus: res.status,
      },
      {
        status: res.status >= 500 ? 503 : res.status,
        headers: LIVE_CACHE_HEADERS,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "User data source upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}
