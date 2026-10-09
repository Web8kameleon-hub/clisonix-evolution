export type HealthStatus = 'healthy' | 'degraded' | 'error';

export interface JonaHealthCheck {
  status: HealthStatus;
  target?: string;
  value?: number | boolean | null;
  detail?: string | null;
}

export interface JonaHealthSnapshot {
  service: 'JONA';
  status: HealthStatus;
  checks: {
    upstream: JonaHealthCheck;
    operational: JonaHealthCheck;
    health_score: JonaHealthCheck;
    coordination: JonaHealthCheck;
  };
  degraded_reason: string | null;
  data: {
    operational: boolean;
    health_score: number | null;
    coordination_score: number;
    requests_5m: number;
    audio_synthesis: boolean;
    timestamp?: string;
  };
}

function asNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function deriveHealthScore(value: unknown): number | null {
  if (typeof value === 'number' || typeof value === 'string') {
    return asNumber(value);
  }

  if (value && typeof value === 'object') {
    const nested = value as Record<string, unknown>;
    return (
      asNumber(nested.score) ??
      asNumber(nested.overall) ??
      asNumber(nested.health_score) ??
      null
    );
  }

  return null;
}

function deriveOperational(value: unknown): boolean {
  if (typeof value === 'boolean') {
    return value;
  }

  if (typeof value === 'string') {
    return ['true', 'online', 'active', 'operational', 'healthy'].includes(value.toLowerCase());
  }

  if (typeof value === 'number') {
    return value > 0;
  }

  return Boolean(value);
}

export function buildJonaHealthSnapshot(
  jonaData: Record<string, unknown>,
  upstreamTarget: string,
  timestamp?: string,
): JonaHealthSnapshot {
  const operational = deriveOperational(jonaData.operational);
  const rawHealthScore = deriveHealthScore(jonaData.health);
  const healthScore =
    rawHealthScore === null
      ? null
      : rawHealthScore <= 1
        ? Number((rawHealthScore * 100).toFixed(1))
        : rawHealthScore;
  const metrics = (jonaData.metrics ?? {}) as Record<string, unknown>;
  const rawCoordinationScore = asNumber(metrics.coordination_score) ?? 0;
  const coordinationScore =
    rawCoordinationScore <= 1
      ? rawCoordinationScore
      : rawCoordinationScore / 100;
  const coordinationDisplayScore = Number((coordinationScore * 100).toFixed(2));
  const requests5m = asNumber(metrics.requests_5m) ?? 0;
  const audioSynthesis = Boolean(metrics.audio_synthesis);

  let status: HealthStatus = 'healthy';
  let degradedReason: string | null = null;

  if (!operational) {
    status = 'degraded';
    degradedReason = 'JONA reports non-operational state';
  } else if (healthScore !== null && healthScore < 70) {
    status = 'degraded';
    degradedReason = `JONA health score dropped below threshold (${healthScore})`;
  } else if (coordinationScore < 0.5) {
    status = 'degraded';
    degradedReason = `Coordination score below threshold (${coordinationDisplayScore.toFixed(2)})`;
  }

  return {
    service: "JONA",
    status,
    checks: {
      upstream: {
        status: "healthy",
        target: upstreamTarget,
        detail: "Trinity upstream reachable",
      },
      operational: {
        status: operational ? "healthy" : "degraded",
        value: operational,
        detail: operational
          ? "JONA operational flag is healthy"
          : "JONA operational flag is degraded",
      },
      health_score: {
        status:
          healthScore === null || healthScore >= 70 ? "healthy" : "degraded",
        value: healthScore,
        detail:
          healthScore === null ? "No health score reported by upstream" : null,
      },
      coordination: {
        status: coordinationScore >= 0.5 ? "healthy" : "degraded",
        value: coordinationDisplayScore,
        detail:
          coordinationScore >= 0.5
            ? "Coordination score within target range"
            : "Coordination score below target range",
      },
    },
    degraded_reason: degradedReason,
    data: {
      operational,
      health_score: healthScore,
      coordination_score: coordinationDisplayScore,
      requests_5m: requests5m,
      audio_synthesis: audioSynthesis,
      timestamp,
    },
  };
}
