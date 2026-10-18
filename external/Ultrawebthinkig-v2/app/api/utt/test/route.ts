import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ 
    message: 'UTT API is working!',
    timestamp: new Date().toISOString(),
    status: 'ok'
  })
}
