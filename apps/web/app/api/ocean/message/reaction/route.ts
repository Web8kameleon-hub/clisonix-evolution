import { NextRequest, NextResponse } from 'next/server';

const resolveOceanUpstream = () => {
  return process.env.OCEAN_CORE_URL || 'http://clisonix-ocean-core:8030';
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Forward auth headers
    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
    if (userId) {
      headers["X-User-ID"] = userId;
      headers["X-User-Id"] = userId;
    }

    const upstream = resolveOceanUpstream();
    const response = await fetch(`${upstream}/api/v1/message/reaction`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[Reaction Route] Error:', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
