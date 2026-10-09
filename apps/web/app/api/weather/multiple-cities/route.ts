import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const upstream = await fetch(`http://api:8000/api/weather/multiple-cities`, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    if (!upstream.ok) {
      throw new Error(`Upstream responded with ${upstream.status}`)
    }

    const payload = await upstream.json()
    return NextResponse.json({ success: true, data: payload })
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Weather multi-city upstream unavailable";
    console.error("[weather/multiple-cities] upstream error:", message);
    return NextResponse.json(
      {
        success: false,
        error: "Weather multi-city service unavailable",
        details: message,
        data: null,
      },
      { status: 503 },
    );
  }
}
