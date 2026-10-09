/**
 * Ocean Curiosity API - Alias for /api/ocean
 * Provides backwards compatibility for /api/ocean_curiosity endpoint
 */

import { NextResponse } from "next/server";

// Redirect to the main ocean API
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const question = searchParams.get("q") || searchParams.get("question") || "";

  // Forward to main ocean API
  const baseUrl = request.url.split("/api/ocean_curiosity")[0];
  const oceanUrl = `${baseUrl}/api/ocean?question=${encodeURIComponent(question)}`;

  try {
    const response = await fetch(oceanUrl);
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({
      success: true,
      message: "Ocean Curiosity API",
      usage: "Use /api/ocean?question=your+question for AI-powered responses",
      redirect: "/api/ocean",
    });
  }
}

export async function POST(request: Request) {
  // Forward POST requests to main ocean API
  const body = await request.json();
  const baseUrl = request.url.split("/api/ocean_curiosity")[0];

  try {
    const response = await fetch(`${baseUrl}/api/ocean`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "Failed to forward to Ocean API",
        redirect: "/api/ocean",
      },
      { status: 500 },
    );
  }
}
