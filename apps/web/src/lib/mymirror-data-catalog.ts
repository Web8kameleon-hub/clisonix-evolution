/* cspell:words mqtts */
export type MyMirrorSourceType = 'iot' | 'api' | 'mqtt' | 'database' | 'file' | 'webhook'
export type MyMirrorSourceStatus = 'active' | 'inactive' | 'error'

export interface MyMirrorDataSource {
  id: string
  name: string
  type: MyMirrorSourceType
  endpoint: string
  status: MyMirrorSourceStatus
  last_data: string | null
  data_points: number
  created_at: string
  module_url?: string
  docs_url?: string
  region?: string
  tags?: string[]
}

export interface MyMirrorTenantStats {
  data_sources_count: number
  active_sources: number
  total_data_points: number
  tracked_metrics: number
  storage_used_gb: number
  api_calls_today: number
}

interface GetMymirrorDataSourcesOptions {
  includeCatalog?: boolean;
}

const CATALOG_SYNC_AT = '2026-04-04T18:35:18Z'
const DEFAULT_STORAGE_GB = 18.4
const DEFAULT_API_CALLS_TODAY = 127800

const runtimeSources: MyMirrorDataSource[] = []

const CATALOG_SOURCES: MyMirrorDataSource[] = [
  {
    id: 'industrial-temperature-array',
    name: 'Industrial Temperature Array',
    type: 'iot',
    endpoint: 'mqtt://sensors.clisonix.cloud:1883/temp/*',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 284930,
    created_at: '2025-11-15T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: '/modules/my-data-dashboard',
    region: 'EU',
    tags: ['iot', 'mqtt', 'industrial', 'temperature'],
  },
  {
    id: 'weather-service-api',
    name: 'Weather Service API',
    type: 'api',
    endpoint: 'https://api.weather.clisonix.cloud/v2',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 45120,
    created_at: '2025-12-01T00:00:00Z',
    module_url: '/modules/aviation-weather',
    docs_url: '/modules/my-data-dashboard',
    region: 'EU',
    tags: ['weather', 'forecast', 'aviation'],
  },
  {
    id: 'lorawan-gateway-eu868',
    name: 'LoRaWAN Gateway EU868',
    type: 'iot',
    endpoint: 'lorawan://eu868.clisonix.cloud',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 128450,
    created_at: '2025-10-20T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: '/modules/my-data-dashboard',
    region: 'EU',
    tags: ['iot', 'lorawan', 'gateway'],
  },
  {
    id: 'cellular-modem-fleet',
    name: 'Cellular Modem Fleet',
    type: 'iot',
    endpoint: 'gsm://fleet.clisonix.cloud',
    status: 'inactive',
    last_data: '2026-04-04T14:35:18Z',
    data_points: 12340,
    created_at: '2026-01-05T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: '/modules/my-data-dashboard',
    region: 'EU',
    tags: ['iot', 'gsm', 'fleet'],
  },
  {
    id: 'production-mqtt-cluster',
    name: 'Production MQTT Cluster',
    type: 'mqtt',
    endpoint: 'mqtts://prod.clisonix.cloud:8883',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 1900000,
    created_at: '2025-08-10T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: '/modules/my-data-dashboard',
    region: 'Global',
    tags: ['mqtt', 'iot', 'production'],
  },
  {
    id: 'stripe-payment-webhooks',
    name: 'Stripe Payment Webhooks',
    type: 'webhook',
    endpoint: 'https://clisonix.cloud/api/webhooks/stripe',
    status: 'active',
    last_data: '2026-04-04T18:27:18Z',
    data_points: 4520,
    created_at: '2025-12-15T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: '/modules/marketplace',
    region: 'Global',
    tags: ['webhook', 'payments', 'business'],
  },
  {
    id: 'eurostat-eu-statistics',
    name: 'Eurostat - EU Statistics',
    type: 'api',
    endpoint: 'https://ec.europa.eu/eurostat/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 45230,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://ec.europa.eu/eurostat/api/',
    region: 'EU',
    tags: ['economy', 'statistics', 'europe'],
  },
  {
    id: 'european-central-bank',
    name: 'European Central Bank',
    type: 'api',
    endpoint: 'https://www.ecb.europa.eu/stats/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 12478,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.ecb.europa.eu/stats/',
    region: 'EU',
    tags: ['economy', 'finance', 'banking'],
  },
  {
    id: 'destatis-germany',
    name: 'Destatis (Germany)',
    type: 'api',
    endpoint: 'https://www.destatis.de/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 8920,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.destatis.de/api/',
    region: 'DE',
    tags: ['economy', 'statistics', 'germany'],
  },
  {
    id: 'insee-france',
    name: 'INSEE (France)',
    type: 'api',
    endpoint: 'https://www.insee.fr/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 7650,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.insee.fr/api/',
    region: 'FR',
    tags: ['economy', 'statistics', 'france'],
  },
  {
    id: 'ons-uk',
    name: 'ONS (United Kingdom)',
    type: 'api',
    endpoint: 'https://www.ons.gov.uk/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 9120,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.ons.gov.uk/api/',
    region: 'UK',
    tags: ['economy', 'statistics', 'uk'],
  },
  {
    id: 'instat-albania',
    name: 'INSTAT Albania',
    type: 'api',
    endpoint: 'https://www.instat.gov.al/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 3420,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.instat.gov.al/api/',
    region: 'AL',
    tags: ['economy', 'statistics', 'albania'],
  },
  {
    id: 'bank-of-albania',
    name: 'Bank of Albania',
    type: 'api',
    endpoint: 'https://www.bankofalbania.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 2180,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.bankofalbania.org/',
    region: 'AL',
    tags: ['economy', 'banking', 'albania'],
  },
  {
    id: 'kosovo-statistics-agency',
    name: 'Kosovo Statistics Agency',
    type: 'api',
    endpoint: 'https://ask.rks-gov.net/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 1890,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://ask.rks-gov.net/',
    region: 'XK',
    tags: ['economy', 'statistics', 'kosovo'],
  },
  {
    id: 'serbia-statistics',
    name: 'Serbia Statistics',
    type: 'api',
    endpoint: 'https://www.stat.gov.rs/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 2450,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.stat.gov.rs/',
    region: 'RS',
    tags: ['economy', 'statistics', 'serbia'],
  },
  {
    id: 'north-macedonia-statistics',
    name: 'N.Macedonia Statistics',
    type: 'api',
    endpoint: 'https://www.stat.gov.mk/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 1750,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.stat.gov.mk/',
    region: 'MK',
    tags: ['economy', 'statistics', 'macedonia'],
  },
  {
    id: 'us-census-bureau',
    name: 'US Census Bureau',
    type: 'api',
    endpoint: 'https://api.census.gov/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 28500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://api.census.gov/',
    region: 'US',
    tags: ['economy', 'statistics', 'usa'],
  },
  {
    id: 'federal-reserve',
    name: 'Federal Reserve',
    type: 'api',
    endpoint: 'https://api.stlouisfed.org/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 15680,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://fred.stlouisfed.org/docs/api/fred/',
    region: 'US',
    tags: ['economy', 'finance', 'usa'],
  },
  {
    id: 'ibge-brazil',
    name: 'IBGE Brazil',
    type: 'api',
    endpoint: 'https://servicodados.ibge.gov.br/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 12340,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://servicodados.ibge.gov.br/api/',
    region: 'BR',
    tags: ['economy', 'statistics', 'brazil'],
  },
  {
    id: 'china-nbs-statistics',
    name: 'China NBS Statistics',
    type: 'api',
    endpoint: 'https://data.stats.gov.cn/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 35200,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://data.stats.gov.cn/',
    region: 'CN',
    tags: ['economy', 'statistics', 'china'],
  },
  {
    id: 'japan-statistics-bureau',
    name: 'Japan Statistics Bureau',
    type: 'api',
    endpoint: 'https://www.stat.go.jp/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 18900,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.stat.go.jp/english/data/',
    region: 'JP',
    tags: ['economy', 'statistics', 'japan'],
  },
  {
    id: 'korea-statistics',
    name: 'Korea Statistics',
    type: 'api',
    endpoint: 'https://kostat.go.kr/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 14500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://kostat.go.kr/',
    region: 'KR',
    tags: ['economy', 'statistics', 'korea'],
  },
  {
    id: 'india-open-data',
    name: 'India Open Data',
    type: 'api',
    endpoint: 'https://data.gov.in/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 42100,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://data.gov.in/',
    region: 'IN',
    tags: ['economy', 'open-data', 'india'],
  },
  {
    id: 'reserve-bank-of-india',
    name: 'Reserve Bank of India',
    type: 'api',
    endpoint: 'https://www.rbi.org.in/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 8750,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.rbi.org.in/',
    region: 'IN',
    tags: ['economy', 'banking', 'india'],
  },
  {
    id: 'un-data',
    name: 'UN Data',
    type: 'api',
    endpoint: 'https://data.un.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 55000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://data.un.org/',
    region: 'Global',
    tags: ['economy', 'health', 'global'],
  },
  {
    id: 'world-bank-open-data',
    name: 'World Bank Open Data',
    type: 'api',
    endpoint: 'https://api.worldbank.org/v2/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 48200,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://api.worldbank.org/',
    region: 'Global',
    tags: ['economy', 'finance', 'global'],
  },
  {
    id: 'imf-data',
    name: 'IMF Data',
    type: 'api',
    endpoint: 'https://www.imf.org/external/datamapper/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 22500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.imf.org/external/datamapper/',
    region: 'Global',
    tags: ['economy', 'finance', 'global'],
  },
  {
    id: 'who-health-data',
    name: 'WHO Health Data',
    type: 'api',
    endpoint: 'https://www.who.int/data/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 18900,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/mymirror-now',
    docs_url: 'https://www.who.int/data',
    region: 'Global',
    tags: ['health', 'research', 'global'],
  },
  {
    id: 'openneuro-eeg-data',
    name: 'OpenNeuro - EEG Data',
    type: 'api',
    endpoint: 'https://openneuro.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 125000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/albi-eeg-live',
    docs_url: 'https://openneuro.org/',
    region: 'Global',
    tags: ['eeg', 'neuro', 'research'],
  },
  {
    id: 'physionet-physiological-data',
    name: 'PhysioNet - Physiological Data',
    type: 'api',
    endpoint: 'https://physionet.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 89500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/albi-eeg-live',
    docs_url: 'https://physionet.org/',
    region: 'Global',
    tags: ['physiology', 'health', 'research'],
  },
  {
    id: 'arxiv-research-papers',
    name: 'arXiv - Research Papers',
    type: 'api',
    endpoint: 'https://export.arxiv.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 250000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/developer-docs',
    docs_url: 'https://arxiv.org/help/api/',
    region: 'Global',
    tags: ['research', 'knowledge', 'papers'],
  },
  {
    id: 'pubmed-medical-literature',
    name: 'PubMed - Medical Literature',
    type: 'api',
    endpoint: 'https://eutils.ncbi.nlm.nih.gov/entrez/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 380000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/developer-docs',
    docs_url: 'https://www.ncbi.nlm.nih.gov/home/develop/api/',
    region: 'Global',
    tags: ['health', 'medical', 'research'],
  },
  {
    id: 'fiware-iot-platform',
    name: 'FIWARE IoT Platform',
    type: 'iot',
    endpoint: 'https://www.fiware.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 45800,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: 'https://www.fiware.org/developers/',
    region: 'EU',
    tags: ['iot', 'platform', 'fiware'],
  },
  {
    id: 'smart-data-models',
    name: 'Smart Data Models',
    type: 'iot',
    endpoint: 'https://smartdatamodels.org/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 28500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/my-data-dashboard',
    docs_url: 'https://smartdatamodels.org/',
    region: 'EU',
    tags: ['iot', 'models', 'smart-city'],
  },
  {
    id: 'copernicus-earth-observation',
    name: 'Copernicus Earth Observation',
    type: 'api',
    endpoint: 'https://www.copernicus.eu/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 156000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/aviation-weather',
    docs_url: 'https://www.copernicus.eu/',
    region: 'EU',
    tags: ['weather', 'earth-observation', 'satellite'],
  },
  {
    id: 'nasa-earth-data',
    name: 'NASA Earth Data',
    type: 'api',
    endpoint: 'https://earthdata.nasa.gov/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 198000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/aviation-weather',
    docs_url: 'https://earthdata.nasa.gov/',
    region: 'Global',
    tags: ['weather', 'earth-observation', 'nasa'],
  },
  {
    id: 'noaa-climate-data',
    name: 'NOAA Climate Data',
    type: 'api',
    endpoint: 'https://www.ncdc.noaa.gov/cdo-web/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 175000,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/aviation-weather',
    docs_url: 'https://www.ncdc.noaa.gov/cdo-web/',
    region: 'Global',
    tags: ['weather', 'climate', 'noaa'],
  },
  {
    id: 'european-environment-agency',
    name: 'European Environment Agency',
    type: 'api',
    endpoint: 'https://www.eea.europa.eu/api/',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 32500,
    created_at: '2025-09-01T00:00:00Z',
    module_url: '/modules/aviation-weather',
    docs_url: 'https://www.eea.europa.eu/',
    region: 'EU',
    tags: ['weather', 'environment', 'europe'],
  },
]

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function normalizeType(value: unknown): MyMirrorSourceType {
  const lowered = String(value || 'api').toLowerCase()
  if (lowered === 'iot' || lowered === 'api' || lowered === 'mqtt' || lowered === 'database' || lowered === 'file' || lowered === 'webhook') {
    return lowered
  }
  return 'api'
}

function normalizeStatus(source: Record<string, unknown>): MyMirrorSourceStatus {
  const lowered = String(source.status || '').toLowerCase()
  if (lowered === 'active' || lowered === 'connected' || lowered === 'online' || lowered === 'healthy') return 'active'
  if (lowered === 'error' || lowered === 'failed' || lowered === 'offline') return 'error'
  if (typeof source.active === 'boolean') return source.active ? 'active' : 'inactive'
  return lowered === 'inactive' ? 'inactive' : 'active'
}

function toNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const cleaned = value.replace(/,/g, '').trim()
    const parsed = Number(cleaned)
    if (Number.isFinite(parsed)) return parsed
  }
  return 0
}

export function normalizeMymirrorSource(source: unknown): MyMirrorDataSource | null {
  if (!source || typeof source !== 'object') return null

  const record = source as Record<string, unknown>
  const name = String(record.name || '').trim()
  const endpoint = String(record.endpoint || record.url || '').trim()

  if (!name && !endpoint) return null

  const id = String(record.id || slugify(name || endpoint) || `source-${Date.now()}`)

  return {
    id,
    name: name || id,
    type: normalizeType(record.type),
    endpoint: endpoint || 'pending-endpoint',
    status: normalizeStatus(record),
    last_data: typeof record.last_data === 'string'
      ? record.last_data
      : typeof record.lastSync === 'string'
        ? record.lastSync
        : CATALOG_SYNC_AT,
    data_points: toNumber(record.data_points ?? record.dataPoints),
    created_at: typeof record.created_at === 'string'
      ? record.created_at
      : typeof record.createdAt === 'string'
        ? record.createdAt
        : CATALOG_SYNC_AT,
    module_url: typeof record.module_url === 'string' ? record.module_url : undefined,
    docs_url: typeof record.docs_url === 'string' ? record.docs_url : undefined,
    region: typeof record.region === 'string' ? record.region : undefined,
    tags: Array.isArray(record.tags) ? record.tags.filter((tag): tag is string => typeof tag === 'string') : undefined,
  }
}

export function addRuntimeMymirrorSource(payload: unknown): MyMirrorDataSource {
  const source = normalizeMymirrorSource(payload) || {
    id: `source-${Date.now()}`,
    name: 'New Data Source',
    type: 'api',
    endpoint: 'pending-endpoint',
    status: 'active',
    last_data: CATALOG_SYNC_AT,
    data_points: 0,
    created_at: CATALOG_SYNC_AT,
  }

  const runtimeSource: MyMirrorDataSource = {
    ...source,
    id: source.id || `source-${Date.now()}`,
    status: source.status || 'active',
    last_data: source.last_data || CATALOG_SYNC_AT,
    created_at: source.created_at || CATALOG_SYNC_AT,
  }

  runtimeSources.unshift(runtimeSource)
  return runtimeSource
}

export function removeRuntimeMymirrorSource(id: string): boolean {
  const index = runtimeSources.findIndex((source) => source.id === id)
  if (index === -1) return false
  runtimeSources.splice(index, 1)
  return true
}

export function getMymirrorDataSources(
  dynamicSources: unknown[] = [],
  options: GetMymirrorDataSourcesOptions = {},
): MyMirrorDataSource[] {
  const { includeCatalog = false } = options;
  const merged = [
    ...dynamicSources
      .map(normalizeMymirrorSource)
      .filter((source): source is MyMirrorDataSource => Boolean(source)),
    ...runtimeSources,
    ...(includeCatalog ? CATALOG_SOURCES : []),
  ];

  const deduped = new Map<string, MyMirrorDataSource>();

  for (const source of merged) {
    const key = `${source.id}::${source.endpoint}`;
    if (!deduped.has(key)) {
      deduped.set(key, source);
    }
  }

  return Array.from(deduped.values()).sort((left, right) => {
    const rank = { active: 0, inactive: 1, error: 2 };
    const statusDelta = rank[left.status] - rank[right.status];
    if (statusDelta !== 0) return statusDelta;
    return left.name.localeCompare(right.name);
  });
}

export function getMymirrorStats(sources: MyMirrorDataSource[]): MyMirrorTenantStats {
  const dataSourcesCount = sources.length
  const activeSources = sources.filter((source) => source.status === 'active').length
  const totalDataPoints = sources.reduce((total, source) => total + source.data_points, 0)
  const trackedMetrics = new Set(sources.flatMap((source) => source.tags && source.tags.length ? source.tags : [source.type])).size

  return {
    data_sources_count: dataSourcesCount,
    active_sources: activeSources,
    total_data_points: totalDataPoints,
    tracked_metrics: trackedMetrics,
    storage_used_gb: DEFAULT_STORAGE_GB,
    api_calls_today: DEFAULT_API_CALLS_TODAY,
  }
}
