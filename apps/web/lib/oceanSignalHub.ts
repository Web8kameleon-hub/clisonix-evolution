export interface SignalPoint {
  key: string;
  source: string;
  ok: boolean;
  value?: unknown;
  latencyMs?: number;
  note?: string;
}

export interface OpenDataLink {
  name: string;
  url: string;
  domain: string;
  category:
    | "billing"
    | "economy"
    | "science"
    | "weather"
    | "knowledge"
    | "time"
    | "news"
    | "sports"
    | "culture"
    | "media"
    | "iot"
    | "ai"
    | "navigation";
}

export interface PlatformModuleLink {
  name: string;
  url: string;
  category:
    | "core"
    | "labs"
    | "matrix"
    | "behavioral"
    | "commerce"
    | "vision"
    | "mesh"
    | "algebra"
    | "persona";
}

export interface OceanSignalSnapshot {
  mode: "signal-hub";
  generatedAt: string;
  question: string;
  pillars: string[];
  engines: string[];
  internalSignals: SignalPoint[];
  externalSignals: SignalPoint[];
  openDataLinks: OpenDataLink[];
  moduleLinks: PlatformModuleLink[];
  summaryLines: string[];
}

const API_BASE =
  process.env.API_INTERNAL_URL ||
  process.env.BACKEND_API_URL ||
  process.env.API_URL ||
  "http://clisonix-api:8000";

const OCEAN_BASE =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.OCEAN_CORE_URL ||
  "http://clisonix-ocean-core:8030";

const PILLARS = [
  "reasoning",
  "responsibility",
  "reliability",
  "compliance-awareness",
  "open-data-grounding",
  "operational-health",
];

const ENGINES = [
  "ocean-core",
  "main-api",
  "matia",
  "eap",
  "shopping-therapy",
  "alphabet-algebra",
  "nanogrid-zeiss",
  "llava-vision",
  "billing",
  "weather",
  "crypto-market",
  "open-economy-feeds",
];

const MODULE_LINKS: PlatformModuleLink[] = [
  {
    name: "Curiosity Ocean",
    url: "https://www.clisonix.com/modules/curiosity-ocean",
    category: "core",
  },
  {
    name: "Matia",
    url: "https://www.clisonix.com/modules/matia",
    category: "core",
  },
  {
    name: "Shopping Therapy",
    url: "https://www.clisonix.com/modules/shopping-therapy",
    category: "commerce",
  },
  {
    name: "Nanogrid Zeiss",
    url: "https://www.clisonix.com/modules/nanogrid-zeiss",
    category: "mesh",
  },
  {
    name: "Social Intelligence",
    url: "https://www.clisonix.com/modules/social-intelligence",
    category: "behavioral",
  },
  {
    name: "Daily Habits",
    url: "https://www.clisonix.com/modules/daily-habits",
    category: "behavioral",
  },
  {
    name: "Mood Journal",
    url: "https://www.clisonix.com/modules/mood-journal",
    category: "behavioral",
  },
  {
    name: "Neural Biofeedback",
    url: "https://www.clisonix.com/modules/neural-biofeedback",
    category: "labs",
  },
  {
    name: "Neural Synthesis",
    url: "https://www.clisonix.com/modules/neural-synthesis",
    category: "labs",
  },
  {
    name: "Protocol Kitchen",
    url: "https://www.clisonix.com/modules/protocol-kitchen",
    category: "matrix",
  },
  {
    name: "Data Collection",
    url: "https://www.clisonix.com/modules/data-collection",
    category: "matrix",
  },
  {
    name: "Algebra & Layers API",
    url: "https://www.clisonix.com/api/ocean/helpers",
    category: "algebra",
  },
  {
    name: "Ocean Vision (LLaVA)",
    url: "https://www.clisonix.com/api/ocean/vision",
    category: "vision",
  },
  {
    name: "Ocean Personas",
    url: "https://www.clisonix.com/api/ocean/personas",
    category: "persona",
  },
];

const OPEN_DATA_LINKS: OpenDataLink[] = [
  {
    name: "Frankfurter FX (free ECB-based rates)",
    url: "https://api.frankfurter.app/latest",
    domain: "frankfurter.app",
    category: "billing",
  },
  {
    name: "Open-Meteo Forecast API",
    url: "https://api.open-meteo.com/v1/forecast",
    domain: "open-meteo.com",
    category: "weather",
  },
  {
    name: "CoinGecko Public API",
    url: "https://api.coingecko.com/api/v3/ping",
    domain: "coingecko.com",
    category: "economy",
  },
  {
    name: "World Bank Open Data",
    url: "https://datahelpdesk.worldbank.org/knowledgebase/topics/125589",
    domain: "worldbank.org",
    category: "economy",
  },
  {
    name: "Eurostat Open Data",
    url: "https://ec.europa.eu/eurostat/web/main/data/database",
    domain: "europa.eu",
    category: "economy",
  },
  {
    name: "Wikidata Query Service",
    url: "https://query.wikidata.org/",
    domain: "wikidata.org",
    category: "knowledge",
  },
  {
    name: "World Time API",
    url: "https://worldtimeapi.org/api/timezone/Europe/Tirane",
    domain: "worldtimeapi.org",
    category: "time",
  },
  {
    name: "RSSHub (Open RSS Feeds)",
    url: "https://docs.rsshub.app/",
    domain: "rsshub.app",
    category: "news",
  },
  {
    name: "TheSportsDB Public API",
    url: "https://www.thesportsdb.com/api.php",
    domain: "thesportsdb.com",
    category: "sports",
  },
  {
    name: "Europeana Open Culture Data",
    url: "https://pro.europeana.eu/page/search",
    domain: "europeana.eu",
    category: "culture",
  },
  {
    name: "Wikipedia REST (free knowledge)",
    url: "https://en.wikipedia.org/api/rest_v1/",
    domain: "wikipedia.org",
    category: "knowledge",
  },
  {
    name: "Wikimedia Commons Media Search",
    url: "https://commons.wikimedia.org/w/index.php?search=",
    domain: "wikimedia.org",
    category: "media",
  },
  {
    name: "YouTube Search",
    url: "https://www.youtube.com/results?search_query=",
    domain: "youtube.com",
    category: "media",
  },
  {
    name: "DuckDuckGo Image Search",
    url: "https://duckduckgo.com/?iax=images&ia=images&q=",
    domain: "duckduckgo.com",
    category: "media",
  },
];

function buildExternalMediaLinks(question: string): OpenDataLink[] {
  const query = encodeURIComponent(question.trim() || "clisonix ocean");
  return [
    {
      name: "Web Search",
      url: `https://duckduckgo.com/?q=${query}`,
      domain: "duckduckgo.com",
      category: "navigation",
    },
    {
      name: "Image Search",
      url: `https://duckduckgo.com/?iax=images&ia=images&q=${query}`,
      domain: "duckduckgo.com",
      category: "media",
    },
    {
      name: "Video Search",
      url: `https://www.youtube.com/results?search_query=${query}`,
      domain: "youtube.com",
      category: "media",
    },
  ];
}

function shouldUseMeshMode(question: string): boolean {
  const q = (question || "").toLowerCase();
  return /(matia|eap|shopping|algebra|alphabet|nanogrid|zeiss|llava|persona|lora|iot|mesh|labs|matrix|behavior)/i.test(
    q,
  );
}

async function fetchJsonSignal(
  key: string,
  source: string,
  url: string,
  timeoutMs = 3500,
): Promise<SignalPoint> {
  const startedAt = Date.now();

  try {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(timeoutMs),
    });

    const latencyMs = Date.now() - startedAt;

    if (!response.ok) {
      return {
        key,
        source,
        ok: false,
        latencyMs,
        note: `HTTP ${response.status}`,
      };
    }

    const payload = (await response.json()) as unknown;
    return {
      key,
      source,
      ok: true,
      latencyMs,
      value: payload,
    };
  } catch (error) {
    return {
      key,
      source,
      ok: false,
      latencyMs: Date.now() - startedAt,
      note: error instanceof Error ? error.message : "signal unavailable",
    };
  }
}

function summarizeSignals(
  internalSignals: SignalPoint[],
  externalSignals: SignalPoint[],
): string[] {
  const internalOk = internalSignals.filter((item) => item.ok).length;
  const externalOk = externalSignals.filter((item) => item.ok).length;

  const lines = [
    `Internal signals: ${internalOk}/${internalSignals.length} healthy`,
    `External signals: ${externalOk}/${externalSignals.length} healthy`,
  ];

  const slowest = [...internalSignals, ...externalSignals]
    .filter((item) => typeof item.latencyMs === "number")
    .sort((a, b) => (b.latencyMs || 0) - (a.latencyMs || 0))[0];

  if (slowest?.latencyMs) {
    lines.push(`Slowest signal: ${slowest.key} (${slowest.latencyMs}ms)`);
  }

  const failed = [...internalSignals, ...externalSignals].filter((item) => !item.ok);
  if (failed.length) {
    lines.push(
      `Degraded signals: ${failed
        .slice(0, 4)
        .map((item) => item.key)
        .join(", ")}`,
    );
  }

  return lines;
}

function normalizeServiceRows(raw: unknown): Array<Record<string, unknown>> {
  if (!raw || typeof raw !== "object") return [];
  const asRecord = raw as Record<string, unknown>;

  const direct = asRecord.services;
  if (Array.isArray(direct)) {
    return direct.filter((item) => item && typeof item === "object") as Array<
      Record<string, unknown>
    >;
  }

  const nested =
    asRecord.data && typeof asRecord.data === "object"
      ? (asRecord.data as Record<string, unknown>).services
      : null;
  if (Array.isArray(nested)) {
    return nested.filter((item) => item && typeof item === "object") as Array<
      Record<string, unknown>
    >;
  }

  return [];
}

function classifyDiscoveryCategory(
  name: string,
): PlatformModuleLink["category"] {
  const n = name.toLowerCase();
  if (/(mesh|lora|iot|nanogrid|zeiss)/i.test(n)) return "mesh";
  if (/(persona|agent)/i.test(n)) return "persona";
  if (/(lab|matrix|engine)/i.test(n)) return "labs";
  if (/(shop|billing|commerce)/i.test(n)) return "commerce";
  if (/(vision|llava|video|image)/i.test(n)) return "vision";
  if (/(algebra|alphabet|layer)/i.test(n)) return "algebra";
  return "core";
}

function extractServiceUrl(row: Record<string, unknown>): string {
  const direct = [
    "url",
    "endpoint",
    "base_url",
    "baseUrl",
    "health",
    "public_url",
    "publicUrl",
  ];
  for (const key of direct) {
    const value = row[key];
    if (typeof value === "string" && /^https?:\/\//i.test(value.trim())) {
      return value.trim();
    }
  }
  return "";
}

function buildDiscoveryLinks(
  serviceDiscoveryPayload: unknown,
): PlatformModuleLink[] {
  const rows = normalizeServiceRows(serviceDiscoveryPayload);
  const links = rows
    .map((row) => {
      const rawName =
        (typeof row.name === "string" && row.name.trim()) ||
        (typeof row.service === "string" && row.service.trim()) ||
        (typeof row.id === "string" && row.id.trim()) ||
        "";
      const url = extractServiceUrl(row);
      if (!rawName || !url) return null;
      return {
        name: rawName,
        url,
        category: classifyDiscoveryCategory(rawName),
      } as PlatformModuleLink;
    })
    .filter((item): item is PlatformModuleLink => Boolean(item));

  const unique = new Map<string, PlatformModuleLink>();
  for (const item of links) {
    const key = `${item.name.toLowerCase()}|${item.url.toLowerCase()}`;
    if (!unique.has(key)) unique.set(key, item);
  }
  return Array.from(unique.values()).slice(0, 40);
}

function extractGramGs26Links(
  links: PlatformModuleLink[],
): PlatformModuleLink[] {
  return links.filter((item) =>
    /(\bgram\b|\bgs\s*26\b|\bgs26\b)/i.test(item.name),
  );
}

export async function collectOceanSignalSnapshot(
  question: string,
): Promise<OceanSignalSnapshot> {
  const [
    oceanStatus,
    apiStatus,
    weatherSignal,
    cryptoSignal,
    billingSignal,
    serviceDiscovery,
    userDataSources,
    fxSignal,
    meteoSignal,
    geckoSignal,
    worldTimeSignal,
    wikipediaSignal,
    oceanPersonas,
    oceanLayers,
    oceanNanogrid,
  ] = await Promise.all([
    fetchJsonSignal("ocean_status", "internal", `${OCEAN_BASE}/api/v1/status`),
    fetchJsonSignal("api_status", "internal", `${API_BASE}/status`),
    fetchJsonSignal("weather_feed", "internal", `${API_BASE}/api/weather`),
    fetchJsonSignal(
      "crypto_market",
      "internal",
      `${API_BASE}/api/crypto/market`,
    ),
    fetchJsonSignal(
      "billing_plans",
      "internal",
      `${API_BASE}/api/v1/billing/plans`,
    ),
    fetchJsonSignal(
      "service_discovery",
      "internal",
      `${API_BASE}/service-discovery`,
    ),
    fetchJsonSignal(
      "user_data_sources",
      "internal",
      `${API_BASE}/api/user/data-sources`,
    ),
    fetchJsonSignal(
      "fx_rates_free",
      "external",
      "https://api.frankfurter.app/latest?from=EUR&to=USD,CHF,GBP",
    ),
    fetchJsonSignal(
      "open_meteo_free",
      "external",
      "https://api.open-meteo.com/v1/forecast?latitude=47.37&longitude=8.54&current=temperature_2m",
    ),
    fetchJsonSignal(
      "coingecko_ping",
      "external",
      "https://api.coingecko.com/api/v3/ping",
    ),
    fetchJsonSignal(
      "world_time_tirane",
      "external",
      "https://worldtimeapi.org/api/timezone/Europe/Tirane",
    ),
    fetchJsonSignal(
      "wikipedia_summary_ai",
      "external",
      "https://en.wikipedia.org/api/rest_v1/page/summary/Artificial_intelligence",
    ),
    fetchJsonSignal(
      "ocean_personas",
      "internal",
      `${OCEAN_BASE}/api/v1/personas`,
    ),
    fetchJsonSignal("ocean_layers", "internal", `${OCEAN_BASE}/api/v1/layers`),
    fetchJsonSignal(
      "ocean_nanogrid",
      "internal",
      `${OCEAN_BASE}/api/v1/nanogrid/status`,
    ),
  ]);

  const internalSignals = [
    oceanStatus,
    apiStatus,
    weatherSignal,
    cryptoSignal,
    billingSignal,
    serviceDiscovery,
    userDataSources,
    oceanPersonas,
    oceanLayers,
    oceanNanogrid,
  ];
  const externalSignals = [
    fxSignal,
    meteoSignal,
    geckoSignal,
    worldTimeSignal,
    wikipediaSignal,
  ];
  const moduleLinks = shouldUseMeshMode(question)
    ? MODULE_LINKS
    : MODULE_LINKS.slice(0, 6);
  const discoveredLinks = buildDiscoveryLinks(serviceDiscovery.value);
  const gramGs26Links = extractGramGs26Links(discoveredLinks);
  const combinedModuleLinks = [...moduleLinks, ...discoveredLinks].reduce<
    PlatformModuleLink[]
  >((acc, current) => {
    const exists = acc.some(
      (item) =>
        item.name.toLowerCase() === current.name.toLowerCase() &&
        item.url.toLowerCase() === current.url.toLowerCase(),
    );
    if (!exists) acc.push(current);
    return acc;
  }, []);
  const openDataLinks = [
    ...OPEN_DATA_LINKS,
    ...buildExternalMediaLinks(question),
  ];
  const summaryLines = summarizeSignals(internalSignals, externalSignals);
  if (gramGs26Links.length > 0) {
    summaryLines.push(
      `GRAM/GS26 discovered: ${gramGs26Links.map((item) => item.name).join(", ")}`,
    );
  } else {
    summaryLines.push(
      "GRAM/GS26 not found in current service-discovery snapshot",
    );
  }

  return {
    mode: "signal-hub",
    generatedAt: new Date().toISOString(),
    question: question.trim(),
    pillars: PILLARS,
    engines: ENGINES,
    internalSignals,
    externalSignals,
    openDataLinks,
    moduleLinks: combinedModuleLinks,
    summaryLines,
  };
}

export function buildSignalSystemMessage(
  snapshot: OceanSignalSnapshot | null,
): string | null {
  if (!snapshot) {
    return null;
  }

  const internalOk = snapshot.internalSignals.filter((item) => item.ok).length;
  const externalOk = snapshot.externalSignals.filter((item) => item.ok).length;

  return [
    "Ocean Signal Hub is active.",
    `Question context: ${snapshot.question}`,
    `Pillars: ${snapshot.pillars.join(" | ")}`,
    `Engines: ${snapshot.engines.join(" | ")}`,
    `Internal health: ${internalOk}/${snapshot.internalSignals.length}`,
    `External health: ${externalOk}/${snapshot.externalSignals.length}`,
    `Signal summary: ${snapshot.summaryLines.join(" ; ")}`,
    `Module links: ${snapshot.moduleLinks.map((item) => `${item.name} -> ${item.url}`).join(" | ")}`,
    `Open/free APIs: ${snapshot.openDataLinks
      .slice(0, 8)
      .map((item) => `${item.name} -> ${item.url}`)
      .join(" | ")}`,
    "When relevant, include clickable markdown links and optional image/video web links in the final answer.",
    "Use available internal and external signals as context, but do not invent missing telemetry.",
  ].join("\n");
}

export function buildPlatformNavigationChunk(
  snapshot: OceanSignalSnapshot | null,
): string {
  if (!snapshot) return "";

  const moduleLines = snapshot.moduleLinks
    .slice(0, 8)
    .map((item) => `- [${item.name}](${item.url})`)
    .join("\n");

  const mediaLines = snapshot.openDataLinks
    .filter(
      (item) => item.category === "media" || item.category === "navigation",
    )
    .slice(0, 4)
    .map((item) => `- [${item.name}](${item.url})`)
    .join("\n");

  return [
    "Quick Clisonix Navigation:",
    moduleLines,
    "",
    "Web / Image / Video Links:",
    mediaLines,
  ]
    .filter(Boolean)
    .join("\n");
}
