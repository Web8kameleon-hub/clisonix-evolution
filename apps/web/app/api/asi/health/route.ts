import { NextResponse } from 'next/server'

const isDev = process.env.NODE_ENV === 'development'
const API_BASE = process.env.API_INTERNAL_URL || (isDev ? 'http://localhost:8000' : 'http://clisonix-api:8000')

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' })
    if (!res.ok) {
      return NextResponse.json({ ok: false, status: 'degraded' }, { status: 200 })
    }
    const data = await res.json().catch(() => ({}))
    return NextResponse.json({ ok: true, ...data }, { status: 200 })
  } catch {
    return NextResponse.json({ ok: false, status: 'degraded' }, { status: 200 })
  }
}
