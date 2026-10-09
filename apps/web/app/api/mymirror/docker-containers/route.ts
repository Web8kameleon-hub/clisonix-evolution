import { NextResponse } from "next/server";
import { LIVE_CACHE_HEADERS } from "../../_utils/live-cache";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const REPORTING_PATH = "/api/reporting/docker-containers";
const DEFAULT_API_BASE =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";
const DEFAULT_REPORTING_BASE =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-reporting:8001"
    : "http://127.0.0.1:8001";

function normalizeBaseUrl(value?: string | null) {
  return value?.trim().replace(/\/+$/, "") || null;
}

function toNumber(value: unknown, defaultValue = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : defaultValue;
}

const API_CANDIDATES = Array.from(
  new Set(
    [
      normalizeBaseUrl(process.env.REPORTING_INTERNAL_URL),
      normalizeBaseUrl(process.env.API_INTERNAL_URL),
      DEFAULT_REPORTING_BASE,
      DEFAULT_API_BASE,
      process.env.NODE_ENV === "production" ? "http://localhost:8001" : null,
      process.env.NODE_ENV === "production" ? "http://localhost:8000" : null,
    ].filter((value): value is string => Boolean(value)),
  ),
);

type RawContainer = Record<string, unknown>;

function normalizeContainer(container: RawContainer, index: number) {
  const rawStatus = `${
    container?.status ??
    container?.state ??
    container?.Status ??
    container?.State ??
    ""
  }`;
  const lowered = rawStatus.toLowerCase();
  const isRunning =
    !/(exited|stopped|dead|unhealthy)/.test(lowered) &&
    /(running|up|healthy)/.test(lowered);

  return {
    id: String(
      container?.id ??
        container?.container_id ??
        container?.Id ??
        `${container?.name ?? container?.container_name ?? "container"}-${index}`,
    ),
    name: String(
      container?.name ??
        container?.container_name ??
        container?.Names ??
        `container-${index + 1}`,
    ),
    image: String(container?.image ?? container?.Image ?? "unknown"),
    status: isRunning ? "running" : rawStatus || "unknown",
    cpu: toNumber(container?.cpu ?? container?.cpu_percent ?? 0),
    memory: toNumber(
      container?.memory ??
        container?.memory_percent ??
        container?.mem_percent ??
        0,
    ),
    ports: String(container?.ports ?? container?.Ports ?? "-"),
    healthy:
      typeof container?.healthy === "boolean" ? container.healthy : isRunning,
    uptime: container?.uptime ?? null,
  };
}

async function fetchDockerContainers() {
  let lastError = "No docker container source responded";

  for (const base of API_CANDIDATES) {
    const target = `${base}${REPORTING_PATH}`;

    try {
      const res = await fetch(target, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        next: { revalidate: 0 },
      });

      if (!res.ok) {
        lastError = `${target} -> ${res.status}`;
        continue;
      }

      const data = await res.json();
      if (Array.isArray(data?.containers)) {
        return { ...data, source: target };
      }

      lastError = `${target} -> invalid payload`;
    } catch (error) {
      lastError = `${target} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  throw new Error(lastError);
}

export async function GET() {
  try {
    const data = await fetchDockerContainers();
    const containers = Array.isArray(data?.containers)
      ? data.containers.map((container: RawContainer, index: number) =>
          normalizeContainer(container, index),
        )
      : [];

    const running =
      typeof data?.running === "number"
        ? data.running
        : containers.filter((container) => container.status === "running")
            .length;
    const total =
      typeof data?.total === "number"
        ? data.total
        : typeof data?.count === "number"
          ? data.count
          : containers.length;

    return NextResponse.json(
      {
        timestamp: data?.timestamp ?? new Date().toISOString(),
        total,
        running,
        containers,
        source: data?.source ?? "mymirror-docker-proxy",
      },
      { status: 200, headers: LIVE_CACHE_HEADERS },
    );
  } catch (error) {
    console.error("MyMirror docker containers fetch error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503, headers: LIVE_CACHE_HEADERS },
    );
  }
}
