import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const query = request.nextUrl.search || ''
    const upstream = await fetch(`http://api:8000/api/alpha/market${query}`, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    if (!upstream.ok) {
      const body = await upstream.text().catch(() => '')
      throw new Error(`Upstream responded with ${upstream.status}: ${body || 'no body'}`)
    }

    const payload = await upstream.json()
    return NextResponse.json({ success: true, data: payload })
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Alpha market upstream unavailable'
    console.error('[alpha/market] upstream error:', message)
    return NextResponse.json(
      {
        success: false,
        error: 'Alpha market unavailable',
        details: message,
        data: null,
      },
      { status: 503 },
    )
  }
}
