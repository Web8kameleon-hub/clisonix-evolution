/**
 * SERVICE INFO API
 * ===============
 * Get detailed info about a specific service
 */

import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.NODE_ENV === 'production'
  ? 'http://clisonix-api:8000'
  : 'http://localhost:8000';

function getServiceInfoFallback(service: string) {
  const oceanBase = process.env.NEXT_PUBLIC_OCEAN_URL || 'http://localhost:8030';

  const fallbackMap: Record<string, Record<string, unknown>> = {
    'ocean-core': {
      service: 'ocean-core',
      url: oceanBase,
      health: `${oceanBase}/health`,
      status: 'available',
      fallback: true,
    },
    'ocean-core-multimodal': {
      service: 'ocean-core-multimodal',
      url: 'http://localhost:8033',
      health: 'http://localhost:8033/health',
      status: 'available',
      fallback: true,
    },
    'ocean-core-strict-chat': {
      service: 'ocean-core-strict-chat',
      url: 'http://localhost:8035',
      health: 'http://localhost:8035/health',
      status: 'available',
      fallback: true,
    },
    'ocean-core-blerina': {
      service: 'ocean-core-blerina',
      url: 'http://localhost:8032',
      health: 'http://localhost:8032/health',
      status: 'available',
      fallback: true,
    },
  };

  return fallbackMap[service] ?? null;
}

export async function POST(request: NextRequest) {
  try {
    const { service } = await request.json();

    if (!service) {
      return NextResponse.json(
        { error: 'service name required' },
        { status: 400 }
      );
    }

    // Query backend for service details
    const response = await fetch(`${API_BASE}/api/v1/service-info`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service }),
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      const fallback = getServiceInfoFallback(service);
      if (fallback) {
        return NextResponse.json(fallback);
      }

      return NextResponse.json(
        { error: `Service not found: ${service}` },
        { status: 404 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('[Service Info] Error:', error);
    return NextResponse.json(
      { error: 'Failed to get service info' },
      { status: 503 }
    );
  }
}
