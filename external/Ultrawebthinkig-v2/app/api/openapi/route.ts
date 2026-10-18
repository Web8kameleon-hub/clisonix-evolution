import { promises as fs } from 'node:fs'
import path from 'node:path'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const specPath = path.join(process.cwd(), 'openapi', 'internal-openapi.json')
    const raw = await fs.readFile(specPath, 'utf8')
    const spec = JSON.parse(raw)

    return NextResponse.json(spec, {
      headers: {
        'Cache-Control': 'no-store',
      },
    })
  } catch (error: any) {
    return NextResponse.json(
      {
        error: 'OpenAPI spec unavailable',
        message: error?.message || 'Unknown error',
      },
      { status: 500 }
    )
  }
}
