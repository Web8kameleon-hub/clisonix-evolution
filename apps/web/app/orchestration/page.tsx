"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type ServiceState = "online" | "degraded" | "offline" | "unknown";

type Service = {
  id: string;
  name: string;
  category: string;
  capabilities: string[];
  source: "catalog" | "compose" | "registry";
  state: ServiceState;
  latencyMs?: number;
  checkedAt?: string;
  topology: {
    canonicalId: string;
    dependsOn: string[];
  };
};

type TopologyEdge = {
  id: string;
  source: string;
  target: string;
  type: "dependency";
};

type TopologyResponse = {
  success: boolean;
  data?: {
    services: Service[];
    edges: TopologyEdge[];
  };
  error?: {
    message: string;
  };
  meta?: {
    timestamp?: string;
    source?: string;
    degraded?: boolean;
  };
};

type Cluster = {
  id: string;
  name: string;
  services: Service[];
  state: ServiceState;
  x: number;
  y: number;
};

const STATE_COLORS: Record<ServiceState, string> = {
  online: "#34d399",
  degraded: "#fbbf24",
  offline: "#fb7185",
  unknown: "#94a3b8",
};

function clusterState(services: Service[]): ServiceState {
  if (services.some((service) => service.state === "offline")) return "offline";
  if (services.some((service) => service.state === "degraded")) return "degraded";
  if (services.every((service) => service.state === "online")) return "online";
  return "unknown";
}

function titleize(value: string) {
  return value
    .split(/[-_]/g)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function OrchestrationPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [edges, setEdges] = useState<TopologyEdge[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);
  const [snapshotAt, setSnapshotAt] = useState<string | null>(null);
  const [source, setSource] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTopology = useCallback(async () => {
    try {
      const response = await fetch("/api/service-discovery", {
        cache: "no-store",
      });
      const payload = (await response.json()) as TopologyResponse;

      if (!response.ok || !payload.success || !payload.data) {
        throw new Error(payload.error?.message ?? `Topology request failed (${response.status})`);
      }

      setServices(payload.data.services);
      setEdges(payload.data.edges);
      setSnapshotAt(payload.meta?.timestamp ?? new Date().toISOString());
      setSource(payload.meta?.source ?? null);
      setError(null);
    } catch (loadError) {
      setServices([]);
      setEdges([]);
      setSnapshotAt(null);
      setSource(null);
      setError(loadError instanceof Error ? loadError.message : "Topology is unavailable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTopology();
    const interval = window.setInterval(() => void loadTopology(), 15_000);
    return () => window.clearInterval(interval);
  }, [loadTopology]);

  const clusters = useMemo<Cluster[]>(() => {
    const grouped = new Map<string, Service[]>();
    services.forEach((service) => {
      const members = grouped.get(service.category) ?? [];
      members.push(service);
      grouped.set(service.category, members);
    });

    const entries = Array.from(grouped.entries()).sort(([left], [right]) =>
      left.localeCompare(right),
    );

    return entries.map(([id, members], index) => {
      const angle = (Math.PI * 2 * index) / Math.max(entries.length, 1) - Math.PI / 2;
      return {
        id,
        name: titleize(id),
        services: members,
        state: clusterState(members),
        x: 600 + Math.cos(angle) * 390,
        y: 350 + Math.sin(angle) * 245,
      };
    });
  }, [services]);

  const visibleServices = selectedCluster
    ? services.filter((service) => service.category === selectedCluster)
    : services;
  const availableCanonicalIds = new Set(
    visibleServices.map((service) => service.topology.canonicalId),
  );
  const visibleEdges = edges.filter(
    (edge) =>
      availableCanonicalIds.has(edge.source) &&
      availableCanonicalIds.has(edge.target),
  );

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/90 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-violet-400">
              Live control plane
            </p>
            <h1 className="mt-1 text-2xl font-semibold">Central Orchestrator</h1>
          </div>
          <nav className="flex items-center gap-4 text-sm">
            <Link className="text-slate-400 hover:text-white" href="/status">
              System status
            </Link>
            <Link className="text-slate-400 hover:text-white" href="/modules">
              Modules
            </Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-medium">Runtime topology</h2>
            <p className="mt-1 text-sm text-slate-400">
              Registry/Compose discovery and real health observations. Refreshes every 15 seconds.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            {source && <span className="rounded-full border border-slate-700 px-3 py-1">source: {source}</span>}
            {snapshotAt && (
              <time className="rounded-full border border-slate-700 px-3 py-1" dateTime={snapshotAt}>
                {new Date(snapshotAt).toLocaleTimeString()}
              </time>
            )}
            <button
              className="rounded-lg bg-violet-600 px-3 py-2 font-medium text-white hover:bg-violet-500 disabled:opacity-50"
              disabled={loading}
              onClick={() => void loadTopology()}
              type="button"
            >
              {loading ? "Loading…" : "Refresh"}
            </button>
          </div>
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-200">
            <h3 className="font-semibold">Live topology unavailable</h3>
            <p className="mt-2 text-sm">{error}</p>
            <p className="mt-2 text-xs text-rose-300/70">No fallback runtime data is displayed.</p>
          </div>
        ) : (
          <>
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
              <svg
                aria-label="Live central orchestrator topology"
                className="h-auto min-h-[420px] w-full"
                role="img"
                viewBox="0 0 1200 700"
              >
                <defs>
                  <radialGradient id="orchestrator-core">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.75" />
                    <stop offset="100%" stopColor="#312e81" stopOpacity="0.9" />
                  </radialGradient>
                </defs>

                {clusters.map((cluster) => (
                  <line
                    key={`line-${cluster.id}`}
                    stroke={STATE_COLORS[cluster.state]}
                    strokeDasharray={cluster.state === "unknown" ? "7 7" : undefined}
                    strokeOpacity="0.45"
                    strokeWidth="2"
                    x1="600"
                    x2={cluster.x}
                    y1="350"
                    y2={cluster.y}
                  />
                ))}

                <circle cx="600" cy="350" fill="url(#orchestrator-core)" r="105" stroke="#a78bfa" strokeWidth="2" />
                <circle cx="600" cy="350" fill="none" r="122" stroke="#8b5cf6" strokeDasharray="8 10" strokeOpacity="0.45">
                  <animateTransform attributeName="transform" dur="28s" from="0 600 350" repeatCount="indefinite" to="360 600 350" type="rotate" />
                </circle>
                <text fill="#ede9fe" fontSize="20" fontWeight="700" textAnchor="middle" x="600" y="342">
                  Central Orchestrator
                </text>
                <text fill="#c4b5fd" fontSize="13" textAnchor="middle" x="600" y="369">
                  {services.length} discovered services
                </text>

                {clusters.map((cluster) => {
                  const selected = selectedCluster === cluster.id;
                  return (
                    <g
                      className="cursor-pointer"
                      key={cluster.id}
                      onClick={() => setSelectedCluster(selected ? null : cluster.id)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          setSelectedCluster(selected ? null : cluster.id);
                        }
                      }}
                    >
                      <rect
                        fill={selected ? "#1e1b4b" : "#0f172a"}
                        height="92"
                        rx="18"
                        stroke={STATE_COLORS[cluster.state]}
                        strokeWidth={selected ? "3" : "2"}
                        width="210"
                        x={cluster.x - 105}
                        y={cluster.y - 46}
                      />
                      <circle cx={cluster.x - 78} cy={cluster.y - 18} fill={STATE_COLORS[cluster.state]} r="6" />
                      <text fill="#f8fafc" fontSize="16" fontWeight="600" x={cluster.x - 62} y={cluster.y - 12}>
                        {cluster.name}
                      </text>
                      <text fill="#94a3b8" fontSize="12" x={cluster.x - 78} y={cluster.y + 15}>
                        {cluster.services.length} services · {cluster.state}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="mt-8 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-medium">
                  {selectedCluster ? `${titleize(selectedCluster)} cluster` : "All services"}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {visibleEdges.length} observed topology dependencies
                </p>
              </div>
              {selectedCluster && (
                <button
                  className="text-sm text-violet-300 hover:text-violet-200"
                  onClick={() => setSelectedCluster(null)}
                  type="button"
                >
                  Show all clusters
                </button>
              )}
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {visibleServices.map((service) => (
                <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-4" key={service.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium">{service.name}</h3>
                      <p className="mt-1 text-xs text-slate-500">{service.topology.canonicalId}</p>
                    </div>
                    <span
                      className="rounded-full px-2.5 py-1 text-xs font-medium"
                      style={{
                        backgroundColor: `${STATE_COLORS[service.state]}1f`,
                        color: STATE_COLORS[service.state],
                      }}
                    >
                      {service.state}
                    </span>
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <dt className="text-slate-500">Latency</dt>
                      <dd className="mt-1 text-slate-300">
                        {service.latencyMs === undefined ? "Unavailable" : `${service.latencyMs} ms`}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-slate-500">Discovery</dt>
                      <dd className="mt-1 text-slate-300">{service.source}</dd>
                    </div>
                  </dl>
                  <div className="mt-4 border-t border-slate-800 pt-3 text-xs text-slate-400">
                    <span className="text-slate-500">Depends on: </span>
                    {service.topology.dependsOn.length > 0
                      ? service.topology.dependsOn.join(", ")
                      : "No discovered dependency"}
                  </div>
                </article>
              ))}
            </div>

            {services.length === 0 && !loading && (
              <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/60 p-5 text-sm text-slate-300">
                No services were returned by discovery. No static topology is shown.
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
