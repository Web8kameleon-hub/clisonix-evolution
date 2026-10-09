import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}))
  return NextResponse.json({
    ok: true,
    session_id: `hybrid_${Date.now()}`,
    user_id: body.user_id || 'demo_user',
    clinic_id: body.clinic_id || null,
    data_source: body.data_source || 'hybrid',
    status: 'connected',
  })
}
