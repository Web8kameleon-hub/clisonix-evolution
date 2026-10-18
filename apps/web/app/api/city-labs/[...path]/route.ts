import { NextRequest, NextResponse } from 'next/server'

const INTERNAL_API = (process.env.CITY_LABS_INTERNAL_API || 'http://city-labs-registry:9130').replace(/\/$/, '')
const PREFIX = '/api/city-labs'

function upstreamUrl(request: NextRequest): URL {
  const incoming = request.nextUrl
  const suffix = incoming.pathname.startsWith(PREFIX) ? incoming.pathname.slice(PREFIX.length) : incoming.pathname
  const url = new URL(`${INTERNAL_API}${suffix || '/'}`)
  incoming.searchParams.forEach((value, key) => url.searchParams.append(key, value))
  return url
}

async function proxy(request: NextRequest): Promise<NextResponse> {
  try {
    const headers = new Headers()
    headers.set('accept', request.headers.get('accept') || 'application/json')
    const traceId = request.headers.get('x-trace-id')
    if (traceId) headers.set('x-trace-id', traceId)

    const init: RequestInit = {
      method: request.method,
      headers,
      cache: 'no-store',
    }

    if (!['GET', 'HEAD'].includes(request.method)) {
      const body = await request.text()
      if (body) init.body = body
      const contentType = request.headers.get('content-type')
      if (contentType) headers.set('content-type', contentType)
    }

    const response = await fetch(upstreamUrl(request), init)
    const payload = await response.text()
    return new NextResponse(payload, {
      status: response.status,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json; charset=utf-8',
        'cache-control': 'no-store',
      },
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unavailable',
        detail: error instanceof Error ? error.message : 'City Labs registry unavailable',
      },
      { status: 503, headers: { 'cache-control': 'no-store' } },
    )
  }
}

export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  return proxy(request)
}

export async function POST(request: NextRequest) {
  return proxy(request)
}
