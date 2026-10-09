import { NextResponse } from "next/server";
import { LIVE_CACHE_HEADERS } from "../../_utils/live-cache";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const MAX_STALENESS_MS = 60_000;

function normalizeBaseUrl(value?: string | null): string | null {
  return value?.trim().replace(/\/+$/, "") || null;
}

const INTERNAL_WEB_BASE_CANDIDATES = Array.from(
  new Set(
    [
      normalizeBaseUrl(process.env.WEB_INTERNAL_URL),
      normalizeBaseUrl(process.env.INTERNAL_WEB_BASE_URL),
      process.env.NODE_ENV === "production" ? "http://clisonix-web:3000" : null,
      "http://127.0.0.1:3000",
      process.env.NODE_ENV === "production" ? "http://localhost:3000" : null,
    ].filter((value): value is string => Boolean(value)),
  ),
);

function normalizePercent(value: unknown): number | null {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) return null;
  return Math.min(parsed, 100);
}

async function fetchInternalJson(path: string): Promise<{
  data: Record<string, unknown> | null;
  source: string | null;
  error: string | null;
}> {
  let lastError: string | null = "No upstream base URL available";

  for (const base of INTERNAL_WEB_BASE_CANDIDATES) {
    const target = `${base}${path}`;
    try {
      const response = await fetch(target, {
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Cache-Control": "no-store, no-cache",
          Pragma: "no-cache",
        },
        next: { revalidate: 0 },
      });

      if (!response.ok) {
        lastError = `${target} -> ${response.status}`;
        continue;
      }

      const data = (await response.json()) as Record<string, unknown>;
      return { data, source: target, error: null };
    } catch (error) {
      lastError = `${target} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  return { data: null, source: null, error: lastError };
}

function parseTimestamp(value: unknown): number | null {
  if (typeof value !== "string" || !value.trim()) return null;
  const parsed = Date.parse(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function getPayloadTimestamp(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const source = payload as Record<string, any>;
  const direct = source.timestamp ?? source.generated_at ?? source.updated_at;
  if (typeof direct === "string" && direct.trim()) {
    return direct;
  }

  const metaFetchedAt = source.meta?.fetched_at;
  if (typeof metaFetchedAt === "string" && metaFetchedAt.trim()) {
    return metaFetchedAt;
  }

  return null;
}

function isFreshTimestamp(value: unknown, maxAgeMs: number): boolean {
  const ts = parseTimestamp(value);
  if (ts === null) return false;
  return Date.now() - ts <= maxAgeMs;
}

function isFreshPayload(payload: unknown, maxAgeMs: number): boolean {
  const marker = getPayloadTimestamp(payload);
  if (!marker) {
    // Some live endpoints don't expose timestamps; if fetch succeeded, treat as live.
    return true;
  }
  return isFreshTimestamp(marker, maxAgeMs);
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function getContainers(payload: unknown): Array<Record<string, unknown>> {
  if (!payload || typeof payload !== "object") return [];
  const source = payload as Record<string, unknown>;
  return Array.isArray(source.containers)
    ? (source.containers as Array<Record<string, unknown>>)
    : [];
}

function getContainerName(container: Record<string, unknown>): string {
  const candidates = [
    container.name,
    container.container_name,
    container.service,
    container.image,
    container.id,
    container.container_id,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) {
      return candidate.trim().toLowerCase();
    }
  }

  return "";
}

function isRunningContainer(container: Record<string, unknown>): boolean {
  const raw = `${container?.status ?? container?.state ?? ""}`.toLowerCase();
  return (
    !/(exited|stopped|dead|unhealthy|created)/.test(raw) &&
    /(running|up|healthy)/.test(raw)
  );
}

function isWorkerContainer(container: Record<string, unknown>): boolean {
  const name = getContainerName(container);
  return /(^lab-|\blab\b|-lab$|labor|labour|worker|job|queue|celery|laboratory)/.test(
    name,
  );
}

export async function GET() {
  try {
    const [systemResult, dockerResult, liveResult, sourcesResult] =
      await Promise.all([
        fetchInternalJson("/api/proxy/system-metrics"),
        fetchInternalJson("/api/proxy/docker-containers"),
        fetchInternalJson("/api/mymirror/live-metrics"),
        fetchInternalJson("/api/mymirror/data-sources"),
      ]);

    const system = systemResult.data;
    const docker = dockerResult.data;
    const live = liveResult.data;
    const sources = sourcesResult.data;

    const upstreamErrors = {
      system: systemResult.error,
      docker: dockerResult.error,
      live: liveResult.error,
      sources: sourcesResult.error,
    };

    const upstreamSources = {
      system: systemResult.source,
      docker: dockerResult.source,
      live: liveResult.source,
      sources: sourcesResult.source,
    };

    const availability = {
      system: Boolean(system),
      docker: Boolean(docker),
      live: Boolean(live),
      sources: Boolean(sources),
    };

    const freshness = {
      system: isFreshPayload(system, MAX_STALENESS_MS),
      docker: isFreshPayload(docker, MAX_STALENESS_MS),
      live: isFreshPayload(live, MAX_STALENESS_MS),
      sources: isFreshPayload(sources, MAX_STALENESS_MS),
    };

    const freshnessChecks: boolean[] = [];
    if (availability.system) freshnessChecks.push(freshness.system);
    if (availability.docker) freshnessChecks.push(freshness.docker);
    if (availability.live) freshnessChecks.push(freshness.live);
    if (availability.sources) freshnessChecks.push(freshness.sources);
    const allFresh = freshnessChecks.length > 0 && freshnessChecks.every(Boolean);

    const staleSinceMs = [system, docker, live, sources]
      .map((payload) => parseTimestamp(getPayloadTimestamp(payload)))
      .filter((value): value is number => value !== null)
      .map((ts) => Date.now() - ts)
      .sort((a, b) => b - a)[0] ?? null;

    // No fake/synthetic fallback: if core docker telemetry is missing, fail fast.
    if (!docker) {
      return NextResponse.json(
        {
          error: "Kloud Bridge real data unavailable",
          missing: {
            system: !availability.system,
            docker: !availability.docker,
            live: !availability.live,
            sources: !availability.sources,
          },
          upstream_errors: upstreamErrors,
          upstream_sources: upstreamSources,
          freshness,
          status: "error",
        },
        { status: 503, headers: LIVE_CACHE_HEADERS },
      );
    }

    if (freshnessChecks.length > 0 && !allFresh) {
      return NextResponse.json(
        {
          error: "Kloud Bridge data is stale",
          freshness,
          stale_ms: staleSinceMs,
          upstream_sources: upstreamSources,
          status: "error",
        },
        { status: 503, headers: LIVE_CACHE_HEADERS },
      );
    }

    const systemData = (system ?? {}) as Record<string, any>;
    const dockerData = (docker ?? {}) as Record<string, any>;
    const liveData = (live ?? {}) as Record<string, any>;
    const sourcesData = (sources ?? {}) as Record<string, any>;

    // Friendly transformation for UI
    const bridgeStatus = "connected-monitored";
    const sovereignStatus = liveData?.system ? "ready" : "initializing";
    const totalDataPoints = Number(liveData?.stats?.total_data_points || 0);
    const activeSources = Number(
      liveData?.stats?.active_sources ??
        liveData?.stats?.data_sources_count ??
        sourcesData.active ??
        sourcesData.stats?.active_sources ??
        0,
    );
    const containers = getContainers(dockerData);
    const runningContainers = Number(
      dockerData?.running ??
        liveData?.system?.active_containers ??
        containers.filter(isRunningContainer).length,
    );
    const totalContainers = Number(
      dockerData?.total ?? liveData?.system?.containers ?? containers.length,
    );
    const detectedWorkerContainers =
      containers.filter(isWorkerContainer).length;
    const workerContainers = detectedWorkerContainers;
    const labContainers = 0;
    const allWorkers = workerContainers + labContainers;
    const nonRunningContainers = Math.max(
      0,
      totalContainers - runningContainers,
    );
    const allContainersHealthy =
      totalContainers > 0 && runningContainers >= totalContainers;
    const oceanStatus =
      activeSources > 0 || totalDataPoints > 0 ? "synchronized" : "building";
    const infraReady =
      bridgeStatus === "connected-monitored" &&
      sovereignStatus === "ready" &&
      oceanStatus === "synchronized" &&
      allContainersHealthy;
    const readyStatus = infraReady ? "ready" : "almost";
    const cpuPercent = normalizePercent(
      systemData?.cpu_percent ?? liveData?.system?.cpu ?? null,
    );
    const memoryPercent = normalizePercent(
      systemData?.memory_percent ?? liveData?.system?.memory ?? null,
    );

    const apiCallsToday = Number(liveData?.stats?.api_calls_today ?? 0);
    const activityUpdates =
      totalDataPoints > 0
        ? totalDataPoints
        : apiCallsToday > 0
          ? apiCallsToday
          : null;

    return NextResponse.json(
      {
        status: {
          bridge: bridgeStatus,
          sovereign: sovereignStatus,
          ocean: oceanStatus,
          ready: readyStatus,
        },
        metrics: {
          activity_updates: activityUpdates,
          containers_running: runningContainers,
          containers_total: totalContainers,
          data_sources_active: activeSources,
          worker_containers: workerContainers,
          lab_containers: labContainers,
          total_workers: allWorkers,
          non_running_containers: nonRunningContainers,
          system_cpu: cpuPercent,
          system_memory: memoryPercent,
        },
        human_readable: {
          status: infraReady
            ? "Connected and monitored"
            : "Waiting for real-time healthy telemetry...",
          sync:
            oceanStatus === "synchronized"
              ? "Real-time synchronized"
              : "Awaiting active data sources",
          updates: isFiniteNumber(activityUpdates)
            ? new Intl.NumberFormat("en", { notation: "compact" }).format(
                activityUpdates,
              )
            : "No live activity yet",
          uptime: systemData?.uptime || "Live",
        },
        timestamp: new Date().toISOString(),
        freshness,
        availability,
        upstream_sources: upstreamSources,
      },
      {
        status: 200,
        headers: LIVE_CACHE_HEADERS,
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "Kloud Bridge data unavailable",
        details: error instanceof Error ? error.message : "unknown error",
        status: "error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}

export async function HEAD() {
  return new Response(null, {
    status: 200,
    headers: {
      ...LIVE_CACHE_HEADERS,
      "X-Kloud-Live": "1",
      "X-Kloud-Timestamp": new Date().toISOString(),
    },
  });
}
