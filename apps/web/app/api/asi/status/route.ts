import { NextResponse } from 'next/server'

const isDev = process.env.NODE_ENV === 'development'
const API_BASE = process.env.API_INTERNAL_URL || (isDev ? 'http://localhost:8000' : 'http://clisonix-api:8000')

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/asi/status`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })

    if (!res.ok) {
      return NextResponse.json({ status: 'degraded', trinity: null }, { status: 200 })
    }

    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch {
    return NextResponse.json({ status: 'degraded', trinity: null }, { status: 200 })
  }
}
