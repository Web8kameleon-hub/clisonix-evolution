export type ModulePlatform =
  | "core-web"
  | "ocean-core"
  | "kloud-bridge"
  | "research-stack"
  | "account-zone"
  | "external-runtime";

export interface ModulePlatformMapping {
  id: string;
  route: string;
  platform: ModulePlatform;
  service: string;
  indexable: boolean;
}

export const MODULE_PLATFORM_MAP: ModulePlatformMapping[] = [
  { id: "about-us", route: "/modules/about-us", platform: "core-web", service: "clisonix-web", indexable: false },
  { id: "account", route: "/modules/account", platform: "account-zone", service: "auth-billing", indexable: false },
  { id: "albi-eeg-live", route: "/modules/albi-eeg-live", platform: "ocean-core", service: "albi", indexable: false },
  { id: "archive", route: "/modules/archive", platform: "research-stack", service: "archive-search", indexable: false },
  { id: "aviation-weather", route: "/modules/aviation-weather", platform: "research-stack", service: "weather", indexable: false },
  { id: "crypto-dashboard", route: "/modules/crypto-dashboard", platform: "research-stack", service: "market-data", indexable: false },
  { id: "curiosity-ocean", route: "/modules/curiosity-ocean", platform: "ocean-core", service: "ocean", indexable: true },
  { id: "daily-habits", route: "/modules/daily-habits", platform: "core-web", service: "behavioral", indexable: false },
  { id: "data-collection", route: "/modules/data-collection", platform: "core-web", service: "ingestion", indexable: true },
  { id: "developer-docs", route: "/modules/developer-docs", platform: "core-web", service: "docs", indexable: false },
  { id: "eeg-analysis", route: "/modules/eeg-analysis", platform: "ocean-core", service: "albi", indexable: false },
  { id: "excel-dashboard", route: "/modules/excel-dashboard", platform: "core-web", service: "excel", indexable: true },
  { id: "fitness-dashboard", route: "/modules/fitness-dashboard", platform: "core-web", service: "behavioral", indexable: false },
  { id: "focus-timer", route: "/modules/focus-timer", platform: "core-web", service: "behavioral", indexable: false },
  { id: "functions-registry", route: "/modules/functions-registry", platform: "core-web", service: "registry", indexable: false },
  { id: "how-to-use", route: "/modules/how-to-use", platform: "core-web", service: "docs", indexable: false },
  { id: "hybrid-biometric-dashboard", route: "/modules/hybrid-biometric-dashboard", platform: "ocean-core", service: "hybrid-biometrics", indexable: false },
  { id: "industrial-dashboard", route: "/modules/industrial-dashboard", platform: "core-web", service: "industrial", indexable: true },
  { id: "jona-neural", route: "/modules/jona-neural", platform: "ocean-core", service: "jona", indexable: false },
  { id: "kloud-bridge", route: "/modules/kloud-bridge", platform: "kloud-bridge", service: "kloud-bridge", indexable: true },
  { id: "mood-journal", route: "/modules/mood-journal", platform: "core-web", service: "behavioral", indexable: false },
  { id: "music-studio", route: "/modules/music-studio", platform: "ocean-core", service: "audio", indexable: false },
  { id: "my-data-dashboard", route: "/modules/my-data-dashboard", platform: "account-zone", service: "user-data", indexable: false },
  { id: "mymirror-now", route: "/modules/mymirror-now", platform: "account-zone", service: "mymirror", indexable: false },
  { id: "nanogrid-zeiss", route: "/modules/nanogrid-zeiss", platform: "kloud-bridge", service: "nanogrid", indexable: false },
  { id: "neural-biofeedback", route: "/modules/neural-biofeedback", platform: "ocean-core", service: "biofeedback", indexable: false },
  { id: "neural-synthesis", route: "/modules/neural-synthesis", platform: "ocean-core", service: "neural-synthesis", indexable: false },
  { id: "neuroacoustic-converter", route: "/modules/neuroacoustic-converter", platform: "ocean-core", service: "audio", indexable: false },
  { id: "omnitalk", route: "/modules/omnitalk", platform: "ocean-core", service: "omnitalk", indexable: false },
  { id: "openmind", route: "/modules/openmind", platform: "ocean-core", service: "openmind", indexable: false },
  { id: "phone-monitor", route: "/modules/phone-monitor", platform: "core-web", service: "device-sensors", indexable: false },
  { id: "phone-sensors", route: "/modules/phone-sensors", platform: "core-web", service: "device-sensors", indexable: false },
  { id: "protocol-kitchen", route: "/modules/protocol-kitchen", platform: "core-web", service: "kitchen", indexable: false },
  { id: "reporting-dashboard", route: "/modules/reporting-dashboard", platform: "core-web", service: "reporting", indexable: true },
  { id: "social-intelligence", route: "/modules/social-intelligence", platform: "research-stack", service: "social-intel", indexable: false },
  { id: "specialized-chat", route: "/modules/specialized-chat", platform: "ocean-core", service: "ocean-specialized", indexable: false },
  { id: "spectrum-analyzer", route: "/modules/spectrum-analyzer", platform: "ocean-core", service: "spectrum", indexable: false },
  { id: "user-data", route: "/modules/user-data", platform: "account-zone", service: "user-data", indexable: false },
  { id: "weather-dashboard", route: "/modules/weather-dashboard", platform: "research-stack", service: "weather", indexable: false },
  { id: "web-reader", route: "/modules/web-reader", platform: "research-stack", service: "web-reader", indexable: true },
  { id: "zurich", route: "/zurich", platform: "ocean-core", service: "zurich", indexable: true },
  { id: "debate", route: "/debate", platform: "ocean-core", service: "trinity", indexable: true },
  { id: "specialized-chat-backend", route: "http://localhost:8030/chat", platform: "external-runtime", service: "ocean-specialized", indexable: false },
];

export const SEO_INDEXABLE_MODULE_SLUGS = MODULE_PLATFORM_MAP
  .filter((entry) => entry.indexable && entry.route.startsWith("/modules/"))
  .map((entry) => entry.route.replace("/modules/", ""));

const MODULE_BY_ID = new Map(MODULE_PLATFORM_MAP.map((entry) => [entry.id, entry]));
const MODULE_BY_ROUTE = new Map(MODULE_PLATFORM_MAP.map((entry) => [entry.route, entry]));

export function getModulePlatformById(id: string): ModulePlatformMapping | undefined {
  return MODULE_BY_ID.get(id);
}

export function getModulePlatformByRoute(route: string): ModulePlatformMapping | undefined {
  return MODULE_BY_ROUTE.get(route);
}

export const PLATFORM_LABELS: Record<ModulePlatform, string> = {
  "core-web": "Core Web",
  "ocean-core": "Ocean Core",
  "kloud-bridge": "Kloud Bridge",
  "research-stack": "Research Stack",
  "account-zone": "Account Zone",
  "external-runtime": "External Runtime",
};
