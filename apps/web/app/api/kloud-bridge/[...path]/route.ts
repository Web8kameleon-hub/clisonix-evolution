import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

const KLOUD_BRIDGE_CANDIDATES = Array.from(
  new Set(
    [
      process.env.KLOUD_BRIDGE_INTERNAL_URL,
      'http://clisonix-kloud-bridge:8889',
      'http://kloud-bridge:8889',
      process.env.KLOUD_BRIDGE_URL,
      'http://localhost:8889',
    ]
      .filter((url): url is string => Boolean(url && url.trim()))
      .map((url) => url.replace(/\/+$/, '')),
  ),
)

let preferredUpstream: string | null = null

function getOrderedCandidates() {
  if (!preferredUpstream) {
    return KLOUD_BRIDGE_CANDIDATES
  }

  return [preferredUpstream, ...KLOUD_BRIDGE_CANDIDATES.filter((base) => base !== preferredUpstream)]
}

function getTimeoutMs(pathname: string, method: string) {
  if (method === 'GET' && /^\/(health|status)$/.test(pathname)) {
    return 1200
  }

  if (method === 'GET') {
    return 2000
  }

  return 3500
}

function sanitizeKloudPayload(pathname: string, rawText: string, contentType: string) {
  if (!contentType.includes('application/json')) {
    return rawText
  }

  try {
    const payload = JSON.parse(rawText)

    if (pathname === '/health') {
      return JSON.stringify({
        status: payload?.status ?? "unknown",
        service: payload?.service ?? "kloud-bridge",
        isolated: Boolean(payload?.isolated),
        live_only: Boolean(payload?.live_only),
        upstream_configured: Boolean(payload?.upstream_configured),
        uptime_seconds: payload?.uptime_seconds ?? null,
      });
    }

    if (pathname === '/status') {
      const configured = Boolean(payload?.upstream?.configured)
      const reachable = Boolean(payload?.upstream?.reachable)
      const summary = payload?.summary ?? null
      const serviceTruth =
        payload?.service_truth ?? summary?.service_truth ?? null
      const hardwareSummary =
        payload?.hardware?.summary ?? summary?.hardware_nodes ?? null
      const upstreamPayload = payload?.upstream ?? {}
      const oceanPayload = payload?.ocean_core ?? {}

      const safeTruth = serviceTruth
        ? {
            state: serviceTruth?.state ?? null,
            connectivity: serviceTruth?.connectivity ?? null,
            sync_status: serviceTruth?.sync_status ?? null,
            proof_of_life: serviceTruth?.proof_of_life ?? null,
            live_flow: serviceTruth?.live_flow ?? null,
            hardware_network_health: serviceTruth?.hardware_network_health ?? null,
            confidence: serviceTruth?.confidence ?? null,
            estimated_recovery: serviceTruth?.estimated_recovery ?? null,
            peer_count:
              typeof serviceTruth?.peer_count === 'number'
                ? serviceTruth.peer_count
                : null,
          }
        : null

      const safeHardwareSummary = hardwareSummary
        ? {
            registered_nodes:
              typeof hardwareSummary?.registered_nodes === 'number'
                ? hardwareSummary.registered_nodes
                : null,
            online_nodes:
              typeof hardwareSummary?.online_nodes === 'number'
                ? hardwareSummary.online_nodes
                : null,
            stale_nodes:
              typeof hardwareSummary?.stale_nodes === 'number'
                ? hardwareSummary.stale_nodes
                : null,
            offline_nodes:
              typeof hardwareSummary?.offline_nodes === 'number'
                ? hardwareSummary.offline_nodes
                : null,
            network_health: hardwareSummary?.network_health ?? null,
            cluster_mode: hardwareSummary?.cluster_mode ?? null,
            proof_of_life: hardwareSummary?.proof_of_life ?? null,
            total_pulses:
              typeof hardwareSummary?.total_pulses === 'number'
                ? hardwareSummary.total_pulses
                : null,
          }
        : null

      const peerCount =
        typeof safeTruth?.peer_count === 'number'
          ? safeTruth.peer_count
          : typeof upstreamPayload?.status?.online_node_count === 'number'
            ? upstreamPayload.status.online_node_count
            : 0

      return JSON.stringify({
        service: payload?.service ?? 'kloud-bridge',
        availability: reachable
          ? 'connected'
          : configured
            ? 'limited'
            : 'setup-required',
        message: reachable
          ? 'Protected live connectivity is active.'
          : configured
            ? 'Protected connectivity is still synchronizing.'
            : 'Protected connectivity is waiting to be enabled.',
        upstream: {
          configured,
          reachable,
          state: reachable ? 'ready' : configured ? 'pending' : 'not-configured',
          peer_count: peerCount,
        },
        ocean_core: {
          configured: Boolean(oceanPayload?.configured),
          reachable: Boolean(oceanPayload?.reachable),
          state: Boolean(oceanPayload?.reachable)
            ? 'linked'
            : Boolean(oceanPayload?.configured)
              ? 'pending'
              : 'not-configured',
        },
        summary: {
          peer_count: peerCount,
          state: safeTruth?.state ?? null,
          connectivity: safeTruth?.connectivity ?? null,
          sync_status: safeTruth?.sync_status ?? null,
          estimated_recovery: safeTruth?.estimated_recovery ?? null,
          hardware_nodes: safeHardwareSummary,
          service_truth: safeTruth,
        },
        service_truth: safeTruth,
        hardware: {
          summary: safeHardwareSummary,
        },
      })
    }

    if (pathname === '/fabric/sync') {
      return JSON.stringify({
        status: payload?.status ?? 'unknown',
        live_only: Boolean(payload?.live_only),
        synchronized: payload?.status === 'synchronized',
      })
    }
  } catch {
    return rawText
  }

  return rawText
}

async function proxyToKloudBridge(pathname: string, request: NextRequest) {
  const search = request.nextUrl.search || ''
  const path = pathname.startsWith('/') ? pathname : `/${pathname}`
  const body = request.method === 'GET' ? undefined : await request.text()
  const timeoutMs = getTimeoutMs(path, request.method)
  const candidates = getOrderedCandidates()

  let lastError = 'No Kloud Bridge upstream configured'

  for (const base of candidates) {
    try {
      const target = `${base}${path}${search}`
      const res = await fetch(target, {
        method: request.method,
        headers: {
          'Content-Type': request.headers.get('content-type') || 'application/json',
          Accept: request.headers.get('accept') || 'application/json',
        },
        body,
        cache: 'no-store',
        signal: AbortSignal.timeout(timeoutMs),
      })

      preferredUpstream = base
      const contentType = res.headers.get('content-type') || 'application/json'
      const text = await res.text()
      const safeText = sanitizeKloudPayload(path, text, contentType)
      const responseContentType = contentType.includes('application/json') ? 'application/json' : contentType

      return new NextResponse(safeText, {
        status: res.status,
        headers: {
          'Content-Type': responseContentType,
          'Cache-Control': 'no-store',
        },
      })
    } catch (error) {
      lastError = `${base}: ${error instanceof Error ? error.message : 'Unknown upstream error'}`
    }
  }

  console.warn('[kloud-bridge] public proxy unavailable', { path, lastError })

  if (request.method === 'GET' && path === '/health') {
    return NextResponse.json(
      {
        status: 'unknown',
        service: 'kloud-bridge',
        uptime_seconds: null,
      },
      {
        status: 200,
        headers: { 'Cache-Control': 'no-store' },
      },
    )
  }

  if (request.method === 'GET' && path === '/status') {
    return NextResponse.json(
      {
        service: 'kloud-bridge',
        version: null,
        availability: 'setup-required',
        message: 'Live activation is pending or temporarily unavailable.',
        upstream: {
          configured: false,
          reachable: false,
        },
      },
      {
        status: 200,
        headers: { 'Cache-Control': 'no-store' },
      },
    )
  }

  if (request.method === 'POST' && path === '/fabric/sync') {
    return NextResponse.json(
      {
        status: 'waiting',
        live_only: true,
        synchronized: false,
        detail: 'Synchronization will become available when the upstream connection is live.',
      },
      {
        status: 503,
        headers: { 'Cache-Control': 'no-store' },
      },
    )
  }

  return NextResponse.json(
    {
      success: false,
      error: 'Kloud Bridge API temporarily unavailable.',
    },
    {
      status: 502,
      headers: { 'Cache-Control': 'no-store' },
    },
  )
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  return proxyToKloudBridge(`/${path.join('/')}`, request)
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  return proxyToKloudBridge(`/${path.join('/')}`, request)
}
