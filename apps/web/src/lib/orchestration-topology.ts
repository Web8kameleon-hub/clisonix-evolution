export type ServiceState = "online" | "degraded" | "offline" | "unknown";

export type ServiceTopology = {
  canonicalId: string;
  dependsOn: string[];
};

const ALIASES: Record<string, string> = {
  api: "main-api",
  "ocean-api": "main-api",
  "main-api": "main-api",
  ocean: "ocean-core",
  "ocean-core": "ocean-core",
  "kloud-upstream-runtime": "kloud-bridge",
  "kloud-bridge": "kloud-bridge",
  web: "web-frontend",
  "web-frontend": "web-frontend",
  ultraweb: "web-frontend",
  "alba-service": "alba",
  alba: "alba",
  "albi-service": "albi",
  albi: "albi",
  "jona-service": "jona",
  jona: "jona",
};

const DEPENDENCIES: Record<string, string[]> = {
  alba: ["postgres", "redis"],
  albi: ["alba", "postgres", "redis"],
  jona: ["alba", "albi", "ocean-core", "redis"],
  asi: ["alba", "albi", "jona", "ocean-core"],
  "ocean-core": ["postgres", "redis"],
  "kloud-bridge": ["ocean-core", "redis"],
  auth: ["main-api", "postgres", "redis"],
  office: ["auth", "main-api"],
  reporting: ["main-api", "postgres", "redis"],
  marketplace: ["main-api", "auth", "postgres"],
  "main-api": ["ocean-core", "kloud-bridge", "postgres", "redis"],
  "web-frontend": ["main-api", "reporting", "auth", "office"],
  nginx: ["web-frontend", "main-api"],
};

function canonicalize(serviceId: string) {
  const normalized = serviceId.trim().toLowerCase();
  return ALIASES[normalized] ?? normalized;
}

export function attachTopology<T extends { id: string }>(services: T[]) {
  const availableIds = new Set(
    services.map((service) => canonicalize(service.id)),
  );

  return services.map((service) => {
    const canonicalId = canonicalize(service.id);
    return {
      ...service,
      topology: {
        canonicalId,
        dependsOn: (DEPENDENCIES[canonicalId] ?? []).filter((dependency) =>
          availableIds.has(dependency),
        ),
      } satisfies ServiceTopology,
    };
  });
}

export function buildTopologyEdges(
  services: Array<{ topology: ServiceTopology }>,
) {
  return services.flatMap((service) =>
    service.topology.dependsOn.map((source) => ({
      id: `${source}->${service.topology.canonicalId}`,
      source,
      target: service.topology.canonicalId,
      type: "dependency" as const,
    })),
  );
}

export function parseServiceState(value: unknown): ServiceState {
  if (typeof value === "boolean") {
    return value ? "online" : "offline";
  }

  if (typeof value !== "string") {
    return "unknown";
  }

  const normalized = value.trim().toLowerCase();
  if (
    ["ok", "healthy", "live", "online", "operational", "ready", "running"].includes(
      normalized,
    )
  ) {
    return "online";
  }
  if (["degraded", "warning", "partial"].includes(normalized)) {
    return "degraded";
  }
  if (
    ["down", "failed", "offline", "outage", "stopped", "unhealthy"].includes(
      normalized,
    )
  ) {
    return "offline";
  }
  return "unknown";
}

export function stateFromHealthPayload(payload: unknown): ServiceState {
  if (!payload || typeof payload !== "object") {
    return "unknown";
  }

  const record = payload as Record<string, unknown>;
  const direct =
    parseServiceState(record.healthy) !== "unknown"
      ? parseServiceState(record.healthy)
      : parseServiceState(record.status);
  if (direct !== "unknown") {
    return direct;
  }

  if (record.data && typeof record.data === "object") {
    const data = record.data as Record<string, unknown>;
    const nested =
      parseServiceState(data.healthy) !== "unknown"
        ? parseServiceState(data.healthy)
        : parseServiceState(data.status);
    if (nested !== "unknown") {
      return nested;
    }
  }

  return "unknown";
}
