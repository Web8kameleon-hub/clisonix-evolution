import { NextRequest, NextResponse } from 'next/server'

const ALBI_USER_CANDIDATES = [
  process.env.ALBI_USER_INTERNAL_URL,
  'http://clisonix-albi-user:6681',
  'http://albi-user:6681',
  process.env.ALBI_USER_URL,
  'http://localhost:6681',
]
  .filter((url): url is string => Boolean(url && url.trim()))
  .map((url) => url.replace(/\/+$/, ''))

async function proxyToAlbiUser(pathname: string, request: NextRequest) {
  const search = request.nextUrl.search || ''
  const path = pathname.startsWith('/') ? pathname : `/${pathname}`

  let lastError = 'No ALBI user upstream configured'

  for (const base of ALBI_USER_CANDIDATES) {
    try {
      const target = `${base}${path}${search}`
      const res = await fetch(target, {
        method: request.method,
        headers: {
          'Content-Type': request.headers.get('content-type') || 'application/json',
          Accept: 'application/json',
        },
        body: request.method === 'GET' ? undefined : await request.text(),
        cache: 'no-store',
      })

      const contentType = res.headers.get('content-type') || 'application/json'
      const text = await res.text()
      return new NextResponse(text, {
        status: res.status,
        headers: { 'Content-Type': contentType },
      })
    } catch (error) {
      lastError = error instanceof Error ? error.message : 'Unknown upstream error'
    }
  }

  return NextResponse.json(
    { success: false, error: `ALBI User API unavailable: ${lastError}` },
    { status: 502 },
  )
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  return proxyToAlbiUser(`/${path.join('/')}`, request)
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  return proxyToAlbiUser(`/${path.join('/')}`, request)
}
