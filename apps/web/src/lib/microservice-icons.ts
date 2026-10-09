export const MICROSERVICE_ICONS: Record<string, string> = {
  api: "/icons/microservices/api.svg",
  web: "/icons/microservices/web.svg",
  "ocean-core": "/icons/microservices/ocean-core.svg",
  alba: "/icons/microservices/alba.svg",
  albi: "/icons/microservices/albi.svg",
  jona: "/icons/microservices/jona.svg",
  asi: "/icons/microservices/asi.svg",
  excel: "/icons/microservices/excel.svg",
  kitchen: "/icons/microservices/kitchen.svg",
  postman: "/icons/microservices/postman.svg",
  reporting: "/icons/microservices/excel.svg",
  analytics: "/icons/microservices/alba.svg",
  marketplace: "/icons/microservices/web.svg",
  billing: "/icons/microservices/web.svg",
  observability: "/icons/microservices/api.svg",
  monitoring: "/icons/microservices/api.svg",
  database: "/icons/microservices/api.svg",
  storage: "/icons/microservices/excel.svg",
  bridge: "/icons/microservices/asi.svg",
  kloud: "/icons/microservices/asi.svg",
  service: "/icons/microservices/service-default.svg",
};

export function getMicroserviceIcon(serviceName: string): string {
  const normalized = serviceName.toLowerCase().trim();

  if (MICROSERVICE_ICONS[normalized]) {
    return MICROSERVICE_ICONS[normalized];
  }

  if (
    normalized.includes("kloud") ||
    normalized.includes("bridge") ||
    normalized.includes("node")
  )
    return MICROSERVICE_ICONS.kloud;
  if (
    normalized.includes("market") ||
    normalized.includes("portal") ||
    normalized.includes("billing")
  )
    return MICROSERVICE_ICONS.marketplace;
  if (
    normalized.includes("report") ||
    normalized.includes("excel") ||
    normalized.includes("document")
  )
    return MICROSERVICE_ICONS.reporting;
  if (
    normalized.includes("analytic") ||
    normalized.includes("telemetry") ||
    normalized.includes("behavior")
  )
    return MICROSERVICE_ICONS.analytics;
  if (
    normalized.includes("monitor") ||
    normalized.includes("prometheus") ||
    normalized.includes("grafana") ||
    normalized.includes("loki") ||
    normalized.includes("jaeger") ||
    normalized.includes("tempo")
  )
    return MICROSERVICE_ICONS.monitoring;
  if (
    normalized.includes("redis") ||
    normalized.includes("postgres") ||
    normalized.includes("neo4j") ||
    normalized.includes("minio") ||
    normalized.includes("data")
  )
    return MICROSERVICE_ICONS.database;
  if (
    normalized.includes("api") ||
    normalized.includes("gateway") ||
    normalized.includes("proxy") ||
    normalized.includes("nginx")
  )
    return MICROSERVICE_ICONS.api;
  if (normalized.includes("web")) return MICROSERVICE_ICONS.web;
  if (
    normalized.includes("ocean") ||
    normalized.includes("curiosity") ||
    normalized.includes("knowledge")
  )
    return MICROSERVICE_ICONS["ocean-core"];
  if (normalized.includes("alba") || normalized.includes("analytical"))
    return MICROSERVICE_ICONS.alba;
  if (normalized.includes("albi") || normalized.includes("creative"))
    return MICROSERVICE_ICONS.albi;
  if (normalized.includes("jona") || normalized.includes("coordinator"))
    return MICROSERVICE_ICONS.jona;
  if (normalized.includes("asi")) return MICROSERVICE_ICONS.asi;
  if (normalized.includes("kitchen")) return MICROSERVICE_ICONS.kitchen;
  if (normalized.includes("postman")) return MICROSERVICE_ICONS.postman;

  return MICROSERVICE_ICONS.service;
}
