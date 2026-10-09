import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://clisonix-api:8000' : 'http://127.0.0.1:8000';

function normalizePercent(value: unknown): number | null {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) return null;
  return Math.min(parsed, 100);
}

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/system-status`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          error: "System metrics upstream returned a non-200 status",
          upstreamStatus: response.status,
        },
        { status: response.status >= 500 ? 503 : response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json({
      cpu_percent: normalizePercent(data.system?.cpu_percent),
      memory_percent: normalizePercent(data.system?.memory_percent),
      disk_percent: normalizePercent(data.system?.disk_percent),
      uptime: data.uptime ?? null,
      hostname: data.system?.hostname ?? null,
    });
  } catch (error) {
    console.error("System metrics fetch error:", error);
    return NextResponse.json(
      {
        error: "System metrics upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}
