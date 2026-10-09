import { NextResponse } from 'next/server';

/**
 * Root API endpoint - Returns API info and available endpoints
 */
export async function GET() {
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "";
  const documentationUrl = appUrl
    ? `${appUrl.replace(/\/$/, "")}/developers`
    : "/developers";
  const supportEmail = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "";

  return NextResponse.json({
    name: "Clisonix Cloud API",
    version: "1.0.0",
    status: "operational",
    timestamp: new Date().toISOString(),
    documentation: documentationUrl,
    endpoints: {
      health: {
        "GET /api/asi/health": "ASI Trinity health status",
        "GET /api/asi/trinity": "Full ASI Trinity metrics",
        "GET /api/reporting/health": "Reporting service health",
        "GET /api/reporting/dashboard": "Dashboard metrics",
      },
      modules: {
        "GET /api/ocean": "Curiosity Ocean AI chat",
        "GET /api/pulse": "Pulse real-time data",
        "GET /api/vision": "Vision AI processing",
        "GET /api/grid": "Grid computing status",
      },
    },
    support: supportEmail || null,
  });
}
