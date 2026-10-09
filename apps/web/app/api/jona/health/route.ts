import { apiDegraded, apiError, apiSuccess } from '@/lib/api/response';
import { buildJonaHealthSnapshot } from '@/lib/jona/health';

const JONA_UPSTREAM = 'http://api:8000/asi/status';

export async function GET() {
  try {
    const upstream = await fetch(JONA_UPSTREAM, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });

    if (!upstream.ok) {
      return apiDegraded(
        {
          service: 'JONA',
          status: 'error',
          checks: {
            upstream: {
              status: 'error',
              target: JONA_UPSTREAM,
              detail: `Upstream returned ${upstream.status}`,
            },
          },
          degraded_reason: 'JONA upstream is unavailable',
        },
        'UPSTREAM_UNAVAILABLE',
        'JONA upstream is unavailable',
        {
          status: 200,
          details: {
            upstream: JONA_UPSTREAM,
            upstreamStatus: upstream.status,
          },
          meta: {
            fallback: true,
            upstream: JONA_UPSTREAM,
          },
        },
      );
    }

    const payload = await upstream.json();
    const jonaData = payload.trinity?.jona;

    if (!jonaData || typeof jonaData !== 'object') {
      return apiDegraded(
        {
          service: 'JONA',
          status: 'error',
          checks: {
            upstream: {
              status: 'healthy',
              target: JONA_UPSTREAM,
              detail: 'Trinity responded but JONA payload was missing',
            },
          },
          degraded_reason: 'JONA payload missing from Trinity response',
        },
        'SERVICE_UNAVAILABLE',
        'JONA payload missing from Trinity response',
        {
          status: 200,
          details: {
            upstream: JONA_UPSTREAM,
          },
          meta: {
            fallback: true,
            upstream: JONA_UPSTREAM,
          },
        },
      );
    }

    const snapshot = buildJonaHealthSnapshot(
      jonaData as Record<string, unknown>,
      JONA_UPSTREAM,
      payload.timestamp,
    );

    return apiSuccess(snapshot, {
      meta: {
        upstream: JONA_UPSTREAM,
      },
    });
  } catch (error) {
    console.error('[JONA health] Error:', error);
    return apiError('INTERNAL_ERROR', 'Failed to resolve JONA health contract', {
      status: 500,
      details: String(error),
    });
  }
}
