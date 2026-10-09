import { NextResponse } from "next/server";
import { fetchJsonFromCandidates } from "../../_lib/upstream";

export const dynamic = "force-dynamic";

type SignalState = "live" | "degraded" | "down";

interface SignalProbe {
  id: string;
  title: string;
  state: SignalState;
  latency_ms: number | null;
  source: string | null;
  detail: string | null;
}

function getWebInternalBase() {
  return (
    process.env.WEB_INTERNAL_URL?.trim().replace(/\/+$/, "") ||
    "http://127.0.0.1:3000"
  );
}

async function fetchWebJson(path: string, timeoutMs = 5000) {
  const source = `${getWebInternalBase()}${path}`;
  const started = Date.now();

  const response = await fetch(source, {
    cache: "no-store",
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(timeoutMs),
  });

  if (!response.ok) {
    throw new Error(`${source} -> ${response.status}`);
  }

  const data = (await response.json()) as Record<string, unknown>;
  return { data, source, latency: Date.now() - started };
}

async function probeUltraSignal(timeoutMs = 5000) {
  const base =
    process.env.ULTRA_INTERNAL_URL?.trim().replace(/\/+$/, "") ||
    process.env.NEXT_PUBLIC_ULTRA_URL?.trim().replace(/\/+$/, "") ||
    "https://ultra.clisonix.com";

  const candidates = ["/health", "/api/health", "/api/status"];
  let lastError = "Ultra endpoint unavailable";

  for (const path of candidates) {
    const source = `${base}${path}`;
    const started = Date.now();

    try {
      const response = await fetch(source, {
        cache: "no-store",
        signal: AbortSignal.timeout(timeoutMs),
      });

      if (!response.ok) {
        lastError = `${source} -> ${response.status}`;
        continue;
      }

      return {
        ok: true,
        source,
        latency: Date.now() - started,
        detail: "Connected",
      };
    } catch (error) {
      lastError = `${source} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  return {
    ok: false,
    source: `${base}/*`,
    latency: null,
    detail: lastError,
  };
}

function asSignalProbe(
  id: string,
  title: string,
  settled:
    | PromiseSettledResult<{ source: string; latency: number }>
    | PromiseSettledResult<{ source: string; data: Record<string, unknown>; latency: number }>,
): SignalProbe {
  if (settled.status === "fulfilled") {
    return {
      id,
      title,
      state: "live",
      latency_ms: settled.value.latency,
      source: settled.value.source,
      detail: "Connected",
    };
  }

  return {
    id,
    title,
    state: "degraded",
    latency_ms: null,
    source: null,
    detail: settled.reason instanceof Error ? settled.reason.message : String(settled.reason),
  };
}

export async function GET() {
  const [
    systemSettled,
    asiSettled,
    oceanStatusSettled,
    oceanSelfLearningSettled,
    kloudProxySettled,
    kloudBridgeSettled,
    dockerSettled,
    ultraSettled,
  ] = await Promise.allSettled([
    (async () => {
      const started = Date.now();
      const result = await fetchJsonFromCandidates<Record<string, unknown>>({
        group: "api",
        path: "/api/system-status",
      });
      return { ...result, latency: Date.now() - started };
    })(),
    (async () => {
      const started = Date.now();
      const result = await fetchJsonFromCandidates<Record<string, unknown>>({
        group: "api",
        path: "/api/asi/status",
      });
      return { ...result, latency: Date.now() - started };
    })(),
    fetchWebJson("/api/ocean/status"),
    fetchWebJson("/api/ocean/self-learning-status"),
    fetchWebJson("/api/proxy/kloud-bridge"),
    fetchWebJson("/api/kloud-bridge/status"),
    (async () => {
      const started = Date.now();
      const result = await fetchJsonFromCandidates<Record<string, unknown>>({
        group: "reporting",
        path: "/api/reporting/docker-containers",
      });
      return { ...result, latency: Date.now() - started };
    })(),
    probeUltraSignal(),
  ]);

  const probes: SignalProbe[] = [
    asSignalProbe("system", "Clisonix System", systemSettled),
    asSignalProbe("asi", "ASI Trinity", asiSettled),
    asSignalProbe("ocean", "Ocean Status", oceanStatusSettled),
    asSignalProbe("ocean-self-learning", "Ocean Self Learning", oceanSelfLearningSettled),
    asSignalProbe("kloud", "Kloud Proxy", kloudProxySettled),
    asSignalProbe("kloud-bridge", "Kloud Bridge Core", kloudBridgeSettled),
    asSignalProbe("docker", "Container Telemetry", dockerSettled),
  ];

  if (ultraSettled.status === "fulfilled") {
    probes.push({
      id: "ultra",
      title: "Ultra Clisonix",
      state: ultraSettled.value.ok ? "live" : "degraded",
      latency_ms: ultraSettled.value.latency,
      source: ultraSettled.value.source,
      detail: ultraSettled.value.detail,
    });
  } else {
    probes.push({
      id: "ultra",
      title: "Ultra Clisonix",
      state: "degraded",
      latency_ms: null,
      source: null,
      detail:
        ultraSettled.reason instanceof Error
          ? ultraSettled.reason.message
          : String(ultraSettled.reason),
    });
  }

  const liveCount = probes.filter((probe) => probe.state === "live").length;
  const overall: SignalState =
    liveCount === probes.length
      ? "live"
      : liveCount > 0
        ? "degraded"
        : "down";

  return NextResponse.json({
    status: overall,
    summary: {
      live: liveCount,
      total: probes.length,
      degraded: probes.length - liveCount,
    },
    probes,
    timestamp: new Date().toISOString(),
  });
}
