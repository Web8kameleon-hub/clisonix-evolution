import { NextResponse } from 'next/server'

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  return NextResponse.json({
    clinic_id: id,
    readings: [],
    synced: true,
    timestamp: new Date().toISOString(),
  })
}
