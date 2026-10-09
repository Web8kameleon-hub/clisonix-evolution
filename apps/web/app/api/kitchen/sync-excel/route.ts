import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Excel endpoint definitions that sync with Protocol Kitchen
const EXCEL_ENDPOINTS = [
  // Core System
  { endpoint: "/api/health", method: "GET", layer: "core", depth: 1 },
  { endpoint: "/api/system-status", method: "GET", layer: "core", depth: 1 },

  // Excel Dashboard
  {
    endpoint: "/api/excel/dashboards",
    method: "GET",
    layer: "excel",
    depth: 2,
  },
  {
    endpoint: "/api/excel/dashboard/{name}",
    method: "GET",
    layer: "excel",
    depth: 2,
  },
  {
    endpoint: "/api/excel/download/{filename}",
    method: "GET",
    layer: "excel",
    depth: 2,
  },

  // Protocol Kitchen
  {
    endpoint: "/api/kitchen/status",
    method: "GET",
    layer: "kitchen",
    depth: 1,
  },
  {
    endpoint: "/api/kitchen/layers",
    method: "GET",
    layer: "kitchen",
    depth: 2,
  },
  {
    endpoint: "/api/kitchen/intake",
    method: "POST",
    layer: "kitchen",
    depth: 3,
  },
  {
    endpoint: "/api/kitchen/metrics",
    method: "GET",
    layer: "kitchen",
    depth: 2,
  },

  // ALBA
  { endpoint: "/api/alba/status", method: "GET", layer: "neural", depth: 2 },
  { endpoint: "/api/alba/collect", method: "POST", layer: "neural", depth: 3 },
  { endpoint: "/api/alba/stream", method: "GET", layer: "neural", depth: 3 },

  // ALBI
  { endpoint: "/api/albi/status", method: "GET", layer: "neural", depth: 2 },
  { endpoint: "/api/albi/analyze", method: "POST", layer: "neural", depth: 3 },
  {
    endpoint: "/api/albi/frequencies",
    method: "GET",
    layer: "neural",
    depth: 2,
  },

  // JONA
  { endpoint: "/api/jona/status", method: "GET", layer: "neural", depth: 2 },
  {
    endpoint: "/api/jona/synthesize",
    method: "POST",
    layer: "neural",
    depth: 3,
  },
  {
    endpoint: "/api/jona/audio-stream",
    method: "GET",
    layer: "neural",
    depth: 3,
  },

  // Billing
  { endpoint: "/api/billing/plans", method: "GET", layer: "billing", depth: 2 },
  {
    endpoint: "/api/billing/subscription",
    method: "GET",
    layer: "billing",
    depth: 2,
  },
  {
    endpoint: "/api/billing/subscribe",
    method: "POST",
    layer: "billing",
    depth: 3,
  },

  // User
  { endpoint: "/api/user/profile", method: "GET", layer: "user", depth: 2 },
  { endpoint: "/api/user/settings", method: "GET", layer: "user", depth: 2 },
  {
    endpoint: "/api/user/data-sources",
    method: "GET",
    layer: "user",
    depth: 2,
  },

  // Analytics
  {
    endpoint: "/api/analytics/summary",
    method: "GET",
    layer: "analytics",
    depth: 2,
  },
  {
    endpoint: "/api/analytics/metrics",
    method: "GET",
    layer: "analytics",
    depth: 2,
  },
  {
    endpoint: "/api/analytics/export",
    method: "POST",
    layer: "analytics",
    depth: 3,
  },

  // Weather
  {
    endpoint: "/api/weather/current",
    method: "GET",
    layer: "integrations",
    depth: 2,
  },
  {
    endpoint: "/api/weather/forecast",
    method: "GET",
    layer: "integrations",
    depth: 2,
  },

  // Crypto
  {
    endpoint: "/api/crypto/prices",
    method: "GET",
    layer: "integrations",
    depth: 2,
  },
  {
    endpoint: "/api/crypto/portfolio",
    method: "GET",
    layer: "integrations",
    depth: 2,
  },

  // Ocean/Curiosity
  { endpoint: "/api/ocean/explore", method: "POST", layer: "ai", depth: 3 },
  { endpoint: "/api/ocean/discoveries", method: "GET", layer: "ai", depth: 2 },
];

export async function GET() {
  try {
    // Check Kitchen status
    const kitchenRes = await fetch(`${API_BASE}/api/kitchen/status`, {
      cache: "no-store",
    });

    const kitchenStatus = kitchenRes.ok ? await kitchenRes.json() : null;

    // Group endpoints by layer
    const byLayer = EXCEL_ENDPOINTS.reduce(
      (acc, ep) => {
        if (!acc[ep.layer]) acc[ep.layer] = [];
        acc[ep.layer].push(ep);
        return acc;
      },
      {} as Record<string, typeof EXCEL_ENDPOINTS>,
    );

    return NextResponse.json({
      success: true,
      kitchen: {
        connected: kitchenRes.ok,
        status: kitchenStatus,
      },
      excel: {
        totalEndpoints: EXCEL_ENDPOINTS.length,
        byLayer: Object.entries(byLayer).map(([layer, endpoints]) => ({
          layer,
          count: endpoints.length,
          endpoints: endpoints.map((e) => `${e.method} ${e.endpoint}`),
        })),
      },
      syncStatus: {
        lastSync: new Date().toISOString(),
        synced: kitchenRes.ok,
        message: kitchenRes.ok
          ? `✅ ${EXCEL_ENDPOINTS.length} endpoints synced with Protocol Kitchen`
          : "⚠️ Kitchen unavailable - using cached endpoints",
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: String(error),
        timestamp: new Date().toISOString(),
      },
      { status: 500 },
    );
  }
}

export async function POST() {
  try {
    // Push endpoints to Kitchen intake
    const response = await fetch(`${API_BASE}/api/kitchen/intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(EXCEL_ENDPOINTS),
    });

    if (!response.ok) {
      throw new Error(`Kitchen intake failed: ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      message: `✅ Synced ${EXCEL_ENDPOINTS.length} Excel endpoints to Protocol Kitchen`,
      result,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: String(error),
        timestamp: new Date().toISOString(),
      },
      { status: 500 },
    );
  }
}
