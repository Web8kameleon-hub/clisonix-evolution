import { NextRequest, NextResponse } from "next/server";

// Use localhost for dev, docker hostname for production
const BACKEND_URL =
  process.env.API_INTERNAL_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://localhost:8000");

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  const path = params.path?.join("/") || "";

  try {
    const upstream = await fetch(`${BACKEND_URL}/api/jona/${path}`, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!upstream.ok) {
      return NextResponse.json(
        { success: false, error: "Backend unavailable" },
        { status: upstream.status },
      );
    }

    const data = await upstream.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("[JONA API Proxy] Error:", error);
    return NextResponse.json(
      { success: false, error: "Connection failed", details: String(error) },
      { status: 500 },
    );
  }
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  const path = params.path?.join("/") || "";

  try {
    let body = null;
    try {
      body = await request.json();
    } catch {
      // No body or invalid JSON - that's ok for some endpoints
    }

    const upstream = await fetch(`${BACKEND_URL}/api/jona/${path}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
    });

    if (!upstream.ok) {
      const errorData = await upstream
        .json()
        .catch(() => ({ error: "Unknown error" }));
      return NextResponse.json(
        { success: false, ...errorData },
        { status: upstream.status },
      );
    }

    const data = await upstream.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("[JONA API Proxy] POST Error:", error);
    return NextResponse.json(
      { success: false, error: "Connection failed", details: String(error) },
      { status: 500 },
    );
  }
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  const path = params.path?.join("/") || "";

  try {
    const upstream = await fetch(`${BACKEND_URL}/api/jona/${path}`, {
      method: "DELETE",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!upstream.ok) {
      return NextResponse.json(
        { success: false, error: "Delete failed" },
        { status: upstream.status },
      );
    }

    const data = await upstream.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("[JONA API Proxy] DELETE Error:", error);
    return NextResponse.json(
      { success: false, error: "Connection failed", details: String(error) },
      { status: 500 },
    );
  }
}
