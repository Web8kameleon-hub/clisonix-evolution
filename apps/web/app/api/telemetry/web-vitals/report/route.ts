import { NextResponse } from "next/server";
import { getWebVitalsSummary } from "@/lib/telemetry/webVitalsStore";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const summary = getWebVitalsSummary();

  if (!summary.hasData) {
    return new NextResponse(null, { status: 204 });
  }

  return NextResponse.json(summary, { status: 200 });
}
