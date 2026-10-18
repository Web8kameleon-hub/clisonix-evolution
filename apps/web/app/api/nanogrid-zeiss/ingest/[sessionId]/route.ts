import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
export const maxDuration = 3600

const ALBI_USER_URL = (
  process.env.ALBI_USER_INTERNAL_URL ||
  process.env.ALBI_USER_URL ||
  'http://albi-user:6681'
).replace(/\/+$/, '')

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ sessionId: string }> },
) {
  const { sessionId } = await context.params
  const target = new URL(
    `/session/${encodeURIComponent(sessionId)}/bulk${request.nextUrl.search}`,
    ALBI_USER_URL,
  )
  const headers = new Headers()

  for (const name of ['authorization', 'content-type', 'content-encoding', 'content-length']) {
    const value = request.headers.get(name)
    if (value) headers.set(name, value)
  }
  if (!headers.has('authorization') && process.env.ALBI_USER_API_KEY) {
    headers.set('authorization', `Bearer ${process.env.ALBI_USER_API_KEY}`)
  }
  headers.set('accept', 'application/json')

  try {
    const init: RequestInit & { duplex: 'half' } = {
      method: 'POST',
      headers,
      body: request.body,
      cache: 'no-store',
      duplex: 'half',
    }
    const response = await fetch(target, init)
    const responseHeaders = new Headers()
    responseHeaders.set(
      'content-type',
      response.headers.get('content-type') || 'application/json',
    )

    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders,
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : 'unknown upstream error'
    return NextResponse.json(
      { error: `ALBI dump ingestion unavailable: ${message}` },
      { status: 502 },
    )
  }
}
