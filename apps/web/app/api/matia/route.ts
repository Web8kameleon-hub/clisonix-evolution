import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const MATIA_BASE = process.env.MATIA_BASE_URL || 'http://clisonix-matia:7200';

// ─── Stream endpoint ──────────────────────────────────────────────────────────

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const path = new URL(req.url).searchParams.get('path') || 'stream';

  // Allowed paths: analyse | stream | screen
  const allowed = ['analyse', 'stream', 'screen'];
  const endpoint = allowed.includes(path) ? path : 'stream';

  try {
    const upstream = await fetch(`${MATIA_BASE}/api/v1/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (endpoint === 'stream') {
      // Relay SSE stream
      if (!upstream.body) {
        return NextResponse.json({ error: 'No stream body from Matia' }, { status: 502 });
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

    // JSON response (analyse | screen)
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });

  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Matia unreachable: ${message}` }, { status: 503 });
  }
}

// ─── Status / health pass-through ────────────────────────────────────────────

export async function GET(req: NextRequest) {
  const path = new URL(req.url).searchParams.get('path') || 'status';
  const allowed = ['health', 'status', ''];
  const endpoint = allowed.includes(path) ? (path || '') : 'status';

  try {
    const upstream = await fetch(`${MATIA_BASE}/${endpoint}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Matia unreachable: ${message}` }, { status: 503 });
  }
}
