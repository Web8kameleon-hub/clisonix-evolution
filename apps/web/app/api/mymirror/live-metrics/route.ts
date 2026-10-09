import { NextResponse } from "next/server";
import { LIVE_CACHE_HEADERS } from "../../_utils/live-cache";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const DEFAULT_API_BASE =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";
function normalizeBaseUrl(value?: string | null) {
  return value?.trim().replace(/\/+$/, "") || null;
}

function toNullableNumber(value: unknown) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

const API_CANDIDATES = Array.from(
  new Set(
    [
      normalizeBaseUrl(process.env.API_INTERNAL_URL),
      DEFAULT_API_BASE,
      process.env.NODE_ENV === "production" ? "http://localhost:8000" : null,
    ].filter((value): value is string => Boolean(value)),
  ),
);

async function fetchJsonFromCandidates(path: string, candidates: string[]) {
  let lastError = `No source responded for ${path}`;

  for (const base of candidates) {
    const target = `${base}${path}`;
    const startedAt = Date.now();
    try {
      const controller = new AbortController();
      const timeoutHandle = setTimeout(() => controller.abort(), 4500);
      const res = await fetch(target, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        next: { revalidate: 0 },
        signal: controller.signal,
      });
      clearTimeout(timeoutHandle);

      if (!res.ok) {
        lastError = `${target} -> ${res.status}`;
        continue;
      }

      const payload = await res.json();
      return {
        payload,
        upstream: target,
        latencyMs: Date.now() - startedAt,
      };
    } catch (error) {
      lastError = `${target} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  throw new Error(lastError);
}

export async function GET() {
  try {
    const liveFetch = await fetchJsonFromCandidates(
      "/api/mymirror/live-metrics",
      API_CANDIDATES,
    );
    const liveData = liveFetch?.payload ?? {};
    const system = liveData?.system || {};
    const stats = liveData?.stats || {};

    return NextResponse.json(
      {
        meta: {
          fetched_at: new Date().toISOString(),
          upstream: liveFetch.upstream,
          upstream_latency_ms: toNullableNumber(liveFetch.latencyMs),
        },
        system: {
          cpu: toNullableNumber(system.cpu_percent ?? system.cpu),
          memory: toNullableNumber(system.memory_percent ?? system.memory),
          disk: toNullableNumber(system.disk_percent ?? system.disk),
          containers: toNullableNumber(system.containers),
          active_containers: toNullableNumber(system.active_containers),
        },
        stats: {
          tenant_id: liveData?.stats?.tenant_id ?? null,
          data_sources_count: toNullableNumber(stats.data_sources_count),
          active_sources: toNullableNumber(stats.active_sources),
          total_data_points: toNullableNumber(stats.total_data_points),
          tracked_metrics: toNullableNumber(stats.tracked_metrics),
          storage_used_gb: toNullableNumber(stats.storage_used_gb),
          api_calls_today: toNullableNumber(stats.api_calls_today),
          internal_apis: toNullableNumber(stats.internal_apis),
          external_apis: toNullableNumber(stats.external_apis),
          laboratories: toNullableNumber(stats.laboratories),
          cores: toNullableNumber(stats.cores),
          engines: toNullableNumber(stats.engines),
          reliability_score: toNullableNumber(stats.reliability_score),
          source_health_ratio: toNullableNumber(stats.source_health_ratio),
          source_quality_score: toNullableNumber(stats.source_quality_score),
        },
        trend: liveData?.trend ?? null,
        alerts: Array.isArray(liveData?.alerts) ? liveData.alerts : [],
        alert_policy: liveData?.alert_policy ?? null,
        persistence: liveData?.persistence ?? null,
      },
      { headers: LIVE_CACHE_HEADERS },
    );
  } catch (error) {
    console.error("MyMirror live metrics fetch error:", error);
    return NextResponse.json(
      {
        error: "System metrics upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}
