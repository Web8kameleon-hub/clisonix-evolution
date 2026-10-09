import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const maxDuration = 3600;

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;
const OCEAN_PUBLIC_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;
const OCEAN_LOCAL_URL = "http://localhost:8030";

const OCEAN_CANDIDATES = Array.from(
  new Set(
    [
      OCEAN_INTERNAL_URL,
      OCEAN_CORE_URL,
      "http://ocean-core:8030",
      isDev ? OCEAN_LOCAL_URL : undefined,
      OCEAN_PUBLIC_URL,
    ]
      .filter((url): url is string => Boolean(url && url.trim()))
      .map((url) => url.replace(/\/+$/, "")),
  ),
);

let preferredUpstream: string | null = null

function getOrderedCandidates() {
  if (!preferredUpstream) {
    return OCEAN_CANDIDATES
  }

  return [preferredUpstream, ...OCEAN_CANDIDATES.filter((base) => base !== preferredUpstream)]
}

function shouldRetryStatus(status: number): boolean {
  return status === 404 || status === 405 || status >= 500;
}

export async function GET() {
  return NextResponse.json({ detail: 'Method Not Allowed' }, { status: 405, headers: { Allow: 'POST' } })
}

export async function POST(request: Request) {
  const contentType = request.headers.get('content-type') || 'application/json'
  const accept = request.headers.get('accept') || 'text/event-stream'
  const body = await request.text()

  let lastError = 'No debate stream upstream configured'
  let lastResponse: NextResponse | null = null;

  for (const base of getOrderedCandidates()) {
    try {
      const response = await fetch(`${base}/api/v1/debate/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': contentType,
          Accept: accept,
        },
        body,
        cache: 'no-store',
      })

      if (!response.body) {
        const text = await response.text();
        const proxied = new NextResponse(text, {
          status: response.status,
          headers: {
            "Content-Type":
              response.headers.get("content-type") || "application/json",
            "Cache-Control": "no-store",
          },
        });

        if (response.ok || !shouldRetryStatus(response.status)) {
          preferredUpstream = base;
          return proxied;
        }

        lastResponse = proxied;
        lastError = `Upstream ${base} returned ${response.status}`;
        continue;
      }

      if (response.ok || !shouldRetryStatus(response.status)) {
        preferredUpstream = base;
        return new NextResponse(response.body, {
          status: response.status,
          headers: {
            "Content-Type":
              response.headers.get("content-type") ||
              "text/event-stream; charset=utf-8",
            "Cache-Control":
              "no-cache, no-store, must-revalidate, no-transform",
            Connection: "keep-alive",
            "X-Accel-Buffering": "no",
          },
        });
      }

      const text = await response.text();
      lastResponse = new NextResponse(text, {
        status: response.status,
        headers: {
          "Content-Type":
            response.headers.get("content-type") || "application/json",
          "Cache-Control": "no-store",
        },
      });
      lastError = `Upstream ${base} returned ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : 'Unknown upstream error'
    }
  }

  if (lastResponse) {
    return lastResponse;
  }

  return NextResponse.json(
    {
      ok: false,
      error: 'Debate engine is temporarily unavailable.',
      detail: process.env.NODE_ENV !== 'production' ? lastError : undefined,
    },
    { status: 502 },
  )
}
