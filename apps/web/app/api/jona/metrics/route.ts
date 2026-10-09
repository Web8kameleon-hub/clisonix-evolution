import { apiError, apiSuccess } from "@/lib/api/response";
import { buildJonaHealthSnapshot } from "@/lib/jona/health";

const JONA_UPSTREAM = "http://api:8000/asi/status";

export async function GET() {
  try {
    // Get REAL data from backend Trinity service
    const upstream = await fetch(JONA_UPSTREAM, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!upstream.ok) {
      return apiError("UPSTREAM_UNAVAILABLE", "JONA backend is unavailable", {
        status: 503,
        details: {
          upstream: JONA_UPSTREAM,
          upstreamStatus: upstream.status,
        },
      });
    }

    const data = await upstream.json();
    const jonaData = data.trinity?.jona;

    if (!jonaData) {
      return apiError(
        "SERVICE_UNAVAILABLE",
        "JONA service is not available in Trinity payload",
        {
          status: 503,
          details: {
            upstream: JONA_UPSTREAM,
          },
        },
      );
    }

    const snapshot = buildJonaHealthSnapshot(
      jonaData as Record<string, unknown>,
      JONA_UPSTREAM,
      data.timestamp,
    );

    return apiSuccess(
      {
        service: "JONA",
        role: "Data Coordinator",
        status: snapshot.status,
        checks: snapshot.checks,
        degraded_reason: snapshot.degraded_reason,
        data: {
          operational: jonaData.operational,
          health: jonaData.health,
          metrics: {
            requests_5m: jonaData.metrics?.requests_5m || 0,
            infinite_potential: jonaData.metrics?.infinite_potential || 0,
            audio_synthesis: jonaData.metrics?.audio_synthesis || false,
            coordination_score: jonaData.metrics?.coordination_score || 0,
          },
          timestamp: data.timestamp,
        },
      },
      {
        meta: {
          upstream: JONA_UPSTREAM,
        },
      },
    );
  } catch (error) {
    console.error("[JONA metrics] Error:", error);
    return apiError("INTERNAL_ERROR", "Failed to resolve JONA metrics", {
      status: 500,
      details: String(error),
    });
  }
}
