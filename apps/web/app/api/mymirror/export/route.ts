import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://clisonix-api:8000' : 'http://127.0.0.1:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const format = body?.format === 'pptx' ? 'pptx' : 'excel'
    const endpoint = format === 'pptx'
      ? `${API_URL}/api/reporting/export-pptx`
      : `${API_URL}/api/reporting/export-excel`

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: '*/*' },
      body: JSON.stringify(body || {}),
    })

    if (!res.ok) {
      return NextResponse.json({ error: 'Export failed' }, { status: 500 })
    }

    const buf = await res.arrayBuffer()
    return new Response(buf, {
      status: 200,
      headers: {
        'Content-Type': format === 'pptx'
          ? 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      },
    })
  } catch {
    return NextResponse.json({ error: 'Export failed' }, { status: 500 })
  }
}
