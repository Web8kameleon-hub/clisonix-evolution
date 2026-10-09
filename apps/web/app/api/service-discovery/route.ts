/**
 * SERVICE DISCOVERY API
 * ====================
 * Gateway endpoint for frontend to discover services dynamically
 */

import fs from "node:fs";
import path from "node:path";
import { NextRequest } from "next/server";
import { apiError, apiSuccess } from "@/lib/api/response";

const isDev = process.env.NODE_ENV === "development";
const API_BASE =
  process.env.API_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (isDev ? "http://localhost:8000" : "http://clisonix-api:8000");
const OCEAN_BASE =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_OCEAN_URL ||
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://ocean-core:8030");

type KnownService = {
  id: string;
  name: string;
  url: string;
  category: string;
  capabilities: string[];
  health?: string;
  stack?: string;
  runtime?: "live" | "compose" | "catalog";
  source: "catalog" | "compose" | "registry";
};

const REGISTRY_LIST_PATHS = ["/api/v1/services", "/api/services", "/services"];
const REGISTRY_DISCOVERY_PATHS = [
  "/api/v1/service-discovery",
  "/api/service-discovery",
];

const ROOT_COMPOSE_CANDIDATES = [
  path.resolve(process.cwd(), "docker-compose.yml"),
  path.resolve(process.cwd(), "..", "..", "docker-compose.yml"),
];

const KLOUD_COMPOSE_CANDIDATES = [
  path.resolve(
    process.cwd(),
    "_imports",
    "Kloud-web8-pr",
    "docker-compose.yml",
  ),
  path.resolve(
    process.cwd(),
    "..",
    "..",
    "_imports",
    "Kloud-web8-pr",
    "docker-compose.yml",
  ),
  path.resolve(
    process.cwd(),
    "_imports",
    "Kloud-web8-master",
    "docker-compose.yml",
  ),
  path.resolve(
    process.cwd(),
    "..",
    "..",
    "_imports",
    "Kloud-web8-master",
    "docker-compose.yml",
  ),
];

function titleize(value: string) {
  return value
    .split(/[-_]/g)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function inferCategory(serviceName: string, stack: string) {
  const normalized = serviceName.toLowerCase();

  if (
    stack === "kloud" ||
    normalized.includes("kloud") ||
    /^node\d+$/.test(normalized)
  )
    return "kloud";
  if (
    normalized.includes("ocean") ||
    normalized.includes("curiosity") ||
    normalized.includes("knowledge")
  )
    return "ai";
  if (
    normalized.includes("alba") ||
    normalized.includes("analytics") ||
    normalized.includes("behavioral")
  )
    return "analytics";
  if (
    normalized.includes("albi") ||
    normalized.includes("jona") ||
    normalized.includes("asi") ||
    normalized.includes("agi")
  )
    return "intelligence";
  if (
    normalized.includes("report") ||
    normalized.includes("excel") ||
    normalized.includes("publisher") ||
    normalized.includes("video")
  )
    return "reporting";
  if (
    normalized.includes("market") ||
    normalized.includes("billing") ||
    normalized.includes("user") ||
    normalized.includes("saas")
  )
    return "business";
  if (
    normalized.includes("redis") ||
    normalized.includes("postgres") ||
    normalized.includes("neo4j") ||
    normalized.includes("minio") ||
    normalized.includes("data")
  )
    return "data";
  if (
    normalized.includes("grafana") ||
    normalized.includes("prometheus") ||
    normalized.includes("loki") ||
    normalized.includes("jaeger") ||
    normalized.includes("tempo") ||
    normalized.includes("telemetry")
  )
    return "observability";
  if (
    normalized.includes("nginx") ||
    normalized.includes("router") ||
    normalized.includes("bridge") ||
    normalized.includes("gateway")
  )
    return "infrastructure";
  return stack === "clisonix" ? "platform" : "services";
}

function inferCapabilities(serviceName: string, stack: string) {
  const normalized = serviceName.toLowerCase();
  const caps = new Set<string>();

  if (stack === "kloud" || normalized.includes("kloud")) {
    caps.add("mesh");
    caps.add("distributed-sync");
  }
  if (/^node\d+$/.test(normalized)) {
    caps.add("nanogrid-node");
    caps.add("gossip");
  }
  if (normalized.includes("bridge")) caps.add("bridge-connectivity");
  if (normalized.includes("ocean")) caps.add("reasoning");
  if (normalized.includes("chat")) caps.add("chat");
  if (normalized.includes("alba") || normalized.includes("analytics"))
    caps.add("analytics");
  if (normalized.includes("albi")) caps.add("creative-intelligence");
  if (normalized.includes("jona")) caps.add("coordination");
  if (normalized.includes("asi")) caps.add("trinity");
  if (normalized.includes("report") || normalized.includes("excel"))
    caps.add("reporting");
  if (normalized.includes("market") || normalized.includes("billing"))
    caps.add("commerce");
  if (
    normalized.includes("telemetry") ||
    normalized.includes("grafana") ||
    normalized.includes("prometheus") ||
    normalized.includes("tempo") ||
    normalized.includes("loki") ||
    normalized.includes("jaeger")
  )
    caps.add("observability");
  if (
    normalized.includes("postgres") ||
    normalized.includes("redis") ||
    normalized.includes("neo4j") ||
    normalized.includes("minio")
  )
    caps.add("data-layer");
  if (normalized.includes("lab-")) caps.add("regional-lab");
  if (normalized.includes("datasource")) caps.add("open-data");

  if (caps.size === 0) {
    caps.add(inferCategory(serviceName, stack));
  }

  return Array.from(caps);
}

function inferHealthPath(serviceName: string) {
  const normalized = serviceName.toLowerCase();

  if (normalized === "kloud-bridge") return "/api/kloud-bridge/health";
  if (normalized === "api" || normalized === "main-api") return "/health";
  if (normalized.includes("report")) return "/api/reporting/health";
  if (normalized.includes("ocean")) return "/api/ocean/health";
  if (
    normalized.includes("asi") ||
    normalized.includes("alba") ||
    normalized.includes("albi") ||
    normalized.includes("jona")
  )
    return "/api/asi/health";
  if (normalized.includes("market")) return "/api/asi/marketplace/health";
  if (normalized.includes("docker") || normalized.includes("nginx"))
    return "/api/proxy/health";
  return undefined;
}

function parseComposeServices(
  composePath: string,
  stack: "clisonix" | "kloud",
): KnownService[] {
  if (!fs.existsSync(composePath)) {
    return [];
  }

  const raw = fs.readFileSync(composePath, "utf8");
  const lines = raw.split(/\r?\n/);
  const services: KnownService[] = [];
  let inServicesBlock = false;

  for (const line of lines) {
    if (!inServicesBlock) {
      if (/^services:\s*$/.test(line)) {
        inServicesBlock = true;
      }
      continue;
    }

    if (/^[A-Za-z0-9_-]+:\s*$/.test(line) && !/^  /.test(line)) {
      break;
    }

    const match = line.match(/^  ([A-Za-z0-9_-]+):\s*$/);
    if (!match) {
      continue;
    }

    const serviceName = match[1];
    if (
      [
        "default",
        "ollama_data",
        "kitchen_jobs",
        "kitchen_reports",
        "nanogrid_net",
      ].includes(serviceName)
    ) {
      continue;
    }

    services.push({
      id: serviceName,
      name: titleize(serviceName),
      url:
        stack === "kloud" && /^node\d+$/.test(serviceName)
          ? `http://localhost:${8000 + Number(serviceName.replace("node", ""))}`
          : `${API_BASE}/${serviceName}`,
      category: inferCategory(serviceName, stack),
      capabilities: inferCapabilities(serviceName, stack),
      health: inferHealthPath(serviceName),
      stack,
      runtime: "compose",
      source: "compose",
    });
  }

  return services;
}

function getKnownServices(): KnownService[] {
  const curated: KnownService[] = [
    {
      id: "main-api",
      name: "Main API",
      url: API_BASE,
      category: "core",
      capabilities: ["excel", "kitchen", "reporting", "metrics", "api-gateway"],
      health: "/health",
      stack: "clisonix",
      runtime: "live",
      source: "catalog",
    },
    {
      id: "ocean-core",
      name: "Ocean Core",
      url: OCEAN_BASE,
      category: "ai",
      capabilities: [
        "nlp-generation",
        "multilingual",
        "reasoning",
        "chat",
        "web-reader",
      ],
      health: "/api/ocean/health",
      stack: "clisonix",
      runtime: "live",
      source: "catalog",
    },
    {
      id: "kloud-bridge",
      name: "Kloud Bridge",
      url: `${API_BASE}/api/kloud-bridge/status`,
      category: "kloud",
      capabilities: ["bridge-connectivity", "distributed-sync", "mesh"],
      health: "/api/kloud-bridge/health",
      stack: "kloud",
      runtime: "live",
      source: "catalog",
    },
    {
      id: "reporting",
      name: "ULTRA Reporting",
      url: `${API_BASE}/api/reporting/dashboard`,
      category: "reporting",
      capabilities: ["dashboard", "export", "analytics"],
      health: "/api/reporting/health",
      stack: "clisonix",
      runtime: "live",
      source: "catalog",
    },
    {
      id: "marketplace",
      name: "Marketplace",
      url: `${API_BASE}/api/marketplace`,
      category: "business",
      capabilities: ["billing", "plans", "subscriptions"],
      health: "/api/proxy/marketplace-health",
      stack: "clisonix",
      runtime: "live",
      source: "catalog",
    },
  ];

  const composeServices = [
    ...ROOT_COMPOSE_CANDIDATES.flatMap((candidate) =>
      parseComposeServices(candidate, "clisonix"),
    ),
    ...KLOUD_COMPOSE_CANDIDATES.flatMap((candidate) =>
      parseComposeServices(candidate, "kloud"),
    ),
  ];

  const merged = new Map<string, KnownService>();
  [...curated, ...composeServices].forEach((service) => {
    if (!service.url) {
      return;
    }

    const existing = merged.get(service.id);
    if (!existing || existing.source === "compose") {
      merged.set(service.id, service);
    }
  });

  return Array.from(merged.values());
}

function buildServiceSummary(services: Array<Record<string, unknown>>) {
  const categorySet = new Set<string>();
  const capabilitySet = new Set<string>();
  let kloudNodes = 0;

  services.forEach((service) => {
    const category =
      typeof service.category === "string" ? service.category : "unknown";
    categorySet.add(category);

    if (
      category === "kloud" ||
      String(service.id || "")
        .toLowerCase()
        .startsWith("node")
    ) {
      kloudNodes += 1;
    }

    if (Array.isArray(service.capabilities)) {
      service.capabilities.forEach((capability) =>
        capabilitySet.add(String(capability)),
      );
    }
  });

  return {
    totalServices: services.length,
    categories: categorySet.size,
    capabilities: capabilitySet.size,
    kloudNodes,
  };
}

function normalizeService(service: Record<string, unknown>, index: number) {
  return {
    id: String(service.id || service.name || `service-${index + 1}`),
    name: String(service.name || service.id || `service-${index + 1}`),
    url: typeof service.url === "string" ? service.url : "",
    category:
      typeof service.category === "string" ? service.category : "discovered",
    capabilities: Array.isArray(service.capabilities)
      ? service.capabilities.map((value) => String(value))
      : [],
    health: typeof service.health === "string" ? service.health : undefined,
    stack: typeof service.stack === "string" ? service.stack : "registry",
    runtime: typeof service.runtime === "string" ? service.runtime : "live",
    metadata: service,
    source: "registry" as const,
  };
}

async function tryListServicesFromRegistry() {
  for (const path of REGISTRY_LIST_PATHS) {
    const upstream = `${API_BASE}${path}`;
    try {
      const response = await fetch(upstream, {
        cache: "no-store",
        signal: AbortSignal.timeout(4000),
      });

      if (!response.ok) {
        continue;
      }

      const payload = await response.json();
      const servicesValue = payload?.services;
      if (!Array.isArray(servicesValue)) {
        continue;
      }

      return {
        services: servicesValue
          .filter((service: unknown) => service && typeof service === "object")
          .map((service: unknown, index: number) =>
            normalizeService(service as Record<string, unknown>, index),
          ),
        upstream,
      };
    } catch {
      continue;
    }
  }

  return null;
}

async function tryDiscoverCapability(capability: string) {
  for (const path of REGISTRY_DISCOVERY_PATHS) {
    const upstream = `${API_BASE}${path}?capability=${encodeURIComponent(capability)}`;
    try {
      const response = await fetch(upstream, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.timeout(4000),
      });

      if (!response.ok) {
        continue;
      }

      const payload = await response.json();
      return { payload, upstream };
    } catch {
      continue;
    }
  }

  return null;
}

function findKnownServiceByCapability(capability: string) {
  const normalizedCapability = capability.trim().toLowerCase();
  return getKnownServices().find((service) =>
    service.capabilities.some(
      (candidate) => candidate.toLowerCase() === normalizedCapability,
    ),
  );
}

/**
 * POST /api/service-discovery
 * Query registry for capability
 */
export async function POST(request: NextRequest) {
  try {
    const { capability } = await request.json();

    if (!capability) {
      return apiError("VALIDATION_ERROR", "capability is required", {
        status: 400,
      });
    }

    const discovered = await tryDiscoverCapability(capability);
    if (discovered) {
      return apiSuccess(discovered.payload, {
        meta: {
          capability,
          upstream: discovered.upstream,
        },
      });
    }

    const knownService = findKnownServiceByCapability(capability);
    if (knownService) {
      return apiSuccess(
        {
          service: knownService.name,
          capability,
          url: knownService.url,
          metadata: {
            source: knownService.source,
            category: knownService.category,
            health: knownService.health,
          },
        },
        {
          meta: {
            capability,
            fallback: true,
            source: knownService.source,
          },
        },
      );
    }

    return apiError(
      "NOT_FOUND",
      `No service found for capability: ${capability}`,
      {
        status: 404,
        details: {
          capability,
        },
      },
    );
  } catch (error) {
    console.error("[Service Discovery] Error:", error);
    return apiError("UPSTREAM_UNAVAILABLE", "Service discovery failed", {
      status: 503,
      details: String(error),
    });
  }
}

/**
 * GET /api/service-discovery
 * List all available services
 */
export async function GET() {
  try {
    const discovered = await tryListServicesFromRegistry();
    if (discovered) {
      return apiSuccess(
        {
          count: discovered.services.length,
          services: discovered.services,
          summary: buildServiceSummary(discovered.services),
        },
        {
          meta: {
            upstream: discovered.upstream,
            source: "registry",
          },
        },
      );
    }

    const services = getKnownServices();
    return apiSuccess(
      {
        count: services.length,
        services,
        summary: buildServiceSummary(services),
      },
      {
        meta: {
          source: "catalog",
          upstream: null,
          degraded: true,
        },
      },
    );
  } catch (error) {
    console.error("[Service Discovery] Error listing services:", error);
    return apiError("UPSTREAM_UNAVAILABLE", "Service listing failed", {
      status: 503,
      details: String(error),
    });
  }
}
