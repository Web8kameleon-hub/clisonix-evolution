import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const message = String(body?.query || body?.message || '').trim()

    if (!message) {
      return NextResponse.json({ success: false, error: 'Query is required' }, { status: 400 })
    }

    const origin = request.nextUrl.origin
    const managerResponse = await fetch(`${origin}/api/ai-manager`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        message,
        clientId: body?.clientId || 'agi-compat-route',
        language: body?.language || 'sq',
      }),
      cache: 'no-store',
    })

    const managerData = await managerResponse.json()

    if (!managerResponse.ok || managerData?.success === false) {
      return NextResponse.json(
        {
          success: false,
          error: managerData?.error || managerData?.message || 'AI manager unavailable',
        },
        { status: managerResponse.status || 502 }
      )
    }

    const content =
      managerData?.result?.response || managerData?.response || managerData?.content || ''

    return NextResponse.json({
      success: true,
      content,
      response: content,
      category: managerData?.category || managerData?.result?.category || 'general',
      handledBy: managerData?.handledBy || managerData?.result?.handledBy || 'AI Manager',
      timestamp: managerData?.timestamp || new Date().toISOString(),
    })
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: error?.message || 'AGI compatibility route failed',
      },
      { status: 500 }
    )
  }
}
