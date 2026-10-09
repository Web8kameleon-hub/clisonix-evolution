import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";

function pickTenantHeaders(request: NextRequest) {
  const tenantId = request.headers.get("x-tenant-id");
  const headers: HeadersInit = { Accept: "application/json" };
  if (tenantId) {
    headers["x-tenant-id"] = tenantId;
  }
  return headers;
}

export async function GET(request: NextRequest) {
  try {
    const res = await fetch(`${API_URL}/api/mymirror/alert-policy`, {
      cache: "no-store",
      headers: pickTenantHeaders(request),
    });

    const payload = await res.json().catch(() => null);
    if (!res.ok) {
      return NextResponse.json(
        {
          error:
            payload?.detail ||
            payload?.error ||
            "Failed to load alert policy upstream",
          upstreamStatus: res.status,
        },
        { status: res.status >= 500 ? 503 : res.status },
      );
    }

    return NextResponse.json(payload ?? {}, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Alert policy upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}

export async function PUT(request: NextRequest) {
  const body = await request.json().catch(() => null);
  if (!body || typeof body !== "object") {
    return NextResponse.json(
      { error: "Invalid alert policy payload" },
      { status: 400 },
    );
  }

  try {
    const headers: HeadersInit = {
      ...pickTenantHeaders(request),
      "Content-Type": "application/json",
    };

    const res = await fetch(`${API_URL}/api/mymirror/alert-policy`, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
    });

    const payload = await res.json().catch(() => null);
    if (!res.ok) {
      return NextResponse.json(
        {
          error:
            payload?.detail ||
            payload?.error ||
            "Failed to update alert policy upstream",
          upstreamStatus: res.status,
        },
        { status: res.status >= 500 ? 503 : res.status },
      );
    }

    return NextResponse.json(payload ?? {}, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Alert policy upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}
