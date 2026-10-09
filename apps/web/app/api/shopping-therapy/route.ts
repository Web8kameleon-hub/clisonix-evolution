import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const SHOP_BASE =
  process.env.SHOPPING_THERAPY_BASE_URL || 'http://clisonix-shopping-therapy:7300';

// ─── POST: search | stream | register | read ──────────────────────────────────

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const path = new URL(req.url).searchParams.get('path') || 'search';

  const allowed = ['search', 'stream', 'register', 'read', 'ocean-chat'];
  const endpoint = allowed.includes(path) ? path : 'search';

  try {
    const upstream = await fetch(`${SHOP_BASE}/api/v1/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (endpoint === 'stream' || endpoint === 'ocean-chat') {
      if (!upstream.body) {
        return NextResponse.json(
          { error: 'No stream body from Shopping Therapy' },
          { status: 502 },
        );
      }
      return new NextResponse(upstream.body, {
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'X-Accel-Buffering': 'no',
        },
      });
    }

    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { error: `Shopping Therapy unreachable: ${message}` },
      { status: 503 },
    );
  }
}

// ─── GET: health | status | catalogue ────────────────────────────────────────

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const path = url.searchParams.get('path') || 'status';
  const category = url.searchParams.get('category') || '';

  const allowed = ['health', 'status', 'catalogue', ''];
  const endpoint = allowed.includes(path) ? path : 'status';

  const upstreamUrl =
    endpoint === 'catalogue'
      ? `${SHOP_BASE}/api/v1/catalogue${category ? `?category=${encodeURIComponent(category)}` : ''}`
      : `${SHOP_BASE}/${endpoint}`;

  try {
    const upstream = await fetch(upstreamUrl, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { error: `Shopping Therapy unreachable: ${message}` },
      { status: 503 },
    );
  }
}
