/**
 * UltraWebThinking - Global API Integration Registry
 * 500+ Free APIs for Real Data Enhancement
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Real Data Enhanced
 */

export interface APIEndpoint {
  id: string;
  name: string;
  category: string;
  url: string;
  description: string;
  keyRequired: boolean;
  rateLimit?: string;
  documentation: string;
  priority: 'high' | 'medium' | 'low';
}

export const GLOBAL_API_REGISTRY: APIEndpoint[] = [
  // Weather & Climate (Priority: HIGH)
  {
    id: 'openweathermap',
    name: 'OpenWeatherMap',
    category: 'Weather & Climate',
    url: 'https://api.openweathermap.org/data/2.5',
    description: 'Current weather, forecasts, historical data for 200,000+ cities',
    keyRequired: true,
    rateLimit: '1000 calls/day (free)',
    documentation: 'https://openweathermap.org/api',
    priority: 'high'
  },
  {
    id: 'weatherapi',
    name: 'WeatherAPI',
    category: 'Weather & Climate',
    url: 'https://api.weatherapi.com/v1',
    description: 'Real-time weather, forecast, astronomy, sports',
    keyRequired: true,
    rateLimit: '1M calls/month (free)',
    documentation: 'https://www.weatherapi.com/docs/',
    priority: 'high'
  },

  // Geolocation & Maps (Priority: HIGH)
  {
    id: 'mapbox',
    name: 'Mapbox',
    category: 'Geolocation & Maps',
    url: 'https://api.mapbox.com',
    description: 'Maps, geocoding, routing, navigation',
    keyRequired: true,
    rateLimit: '50k requests/month (free)',
    documentation: 'https://docs.mapbox.com/',
    priority: 'high'
  },
  {
    id: 'ipinfo',
    name: 'IPinfo',
    category: 'Geolocation & Maps',
    url: 'https://ipinfo.io',
    description: 'IP geolocation, ISP, timezone data',
    keyRequired: true,
    rateLimit: '50k requests/month (free)',
    documentation: 'https://ipinfo.io/developers',
    priority: 'high'
  },

  // Finance & Crypto (Priority: HIGH)
  {
    id: 'alpha_vantage',
    name: 'Alpha Vantage',
    category: 'Finance & Crypto',
    url: 'https://www.alphavantage.co/query',
    description: 'Stock prices, forex, crypto, technical indicators',
    keyRequired: true,
    rateLimit: '5 API requests/minute (free)',
    documentation: 'https://www.alphavantage.co/documentation/',
    priority: 'high'
  },
  {
    id: 'coingecko',
    name: 'CoinGecko',
    category: 'Finance & Crypto',
    url: 'https://api.coingecko.com/api/v3',
    description: 'Cryptocurrency prices, market data, trends',
    keyRequired: false,
    rateLimit: '10-50 calls/minute (free)',
    documentation: 'https://www.coingecko.com/en/api/documentation',
    priority: 'high'
  },

  // News & Media (Priority: MEDIUM)
  {
    id: 'newsapi',
    name: 'NewsAPI',
    category: 'News & Media',
    url: 'https://newsapi.org/v2',
    description: 'Breaking news, headlines, articles from 80,000+ sources',
    keyRequired: true,
    rateLimit: '1000 requests/day (free)',
    documentation: 'https://newsapi.org/docs',
    priority: 'medium'
  },
  {
    id: 'gnews',
    name: 'GNews',
    category: 'News & Media',
    url: 'https://gnews.io/api/v4',
    description: 'Real-time news articles, search, categories',
    keyRequired: true,
    rateLimit: '100 requests/day (free)',
    documentation: 'https://gnews.io/docs/v4',
    priority: 'medium'
  },

  // Space & Astronomy (Priority: MEDIUM - NO KEY!)
  {
    id: 'nasa',
    name: 'NASA Open Data',
    category: 'Space & Astronomy',
    url: 'https://api.nasa.gov',
    description: 'Space missions, astronomy pictures, Mars rover data',
    keyRequired: false,
    rateLimit: '1000 requests/hour (no key)',
    documentation: 'https://api.nasa.gov/',
    priority: 'medium'
  },
  {
    id: 'spacex',
    name: 'SpaceX API',
    category: 'Space & Astronomy',
    url: 'https://api.spacexdata.com/v4',
    description: 'SpaceX launches, rockets, capsules, landing pads',
    keyRequired: false,
    rateLimit: 'No limit',
    documentation: 'https://docs.spacexdata.com/',
    priority: 'medium'
  },

  // Health & Medicine (Priority: MEDIUM - NO KEY!)
  {
    id: 'openfda',
    name: 'OpenFDA',
    category: 'Health & Medicine',
    url: 'https://api.fda.gov',
    description: 'Drug information, adverse events, recalls',
    keyRequired: false,
    rateLimit: '120 requests/minute (no key)',
    documentation: 'https://open.fda.gov/apis/',
    priority: 'medium'
  },
  {
    id: 'covid19_api',
    name: 'COVID-19 API',
    category: 'Health & Medicine',
    url: 'https://disease.sh/v3/covid-19',
    description: 'COVID-19 statistics, country data, historical',
    keyRequired: false,
    rateLimit: 'No limit',
    documentation: 'https://disease.sh/docs/',
    priority: 'medium'
  },

  // AI & NLP (Priority: HIGH)
  {
    id: 'huggingface',
    name: 'HuggingFace',
    category: 'AI & NLP',
    url: 'https://api-inference.huggingface.co',
    description: 'Pre-trained models, text generation, embeddings',
    keyRequired: true,
    rateLimit: '1000 requests/month (free)',
    documentation: 'https://huggingface.co/docs/api-inference',
    priority: 'high'
  },

  // Transport & Traffic (Priority: LOW)
  {
    id: 'aviationstack',
    name: 'AviationStack',
    category: 'Transport & Traffic',
    url: 'https://api.aviationstack.com/v1',
    description: 'Flight data, airports, airlines, routes',
    keyRequired: true,
    rateLimit: '1000 requests/month (free)',
    documentation: 'https://aviationstack.com/documentation',
    priority: 'low'
  },

  // Environment & Energy (Priority: MEDIUM - NO KEY!)
  {
    id: 'openaq',
    name: 'OpenAQ',
    category: 'Environment & Energy',
    url: 'https://api.openaq.org/v2',
    description: 'Air quality data, pollution measurements globally',
    keyRequired: false,
    rateLimit: 'No limit',
    documentation: 'https://docs.openaq.org/',
    priority: 'medium'
  },

  // Education & Books (Priority: LOW - NO KEY!)
  {
    id: 'openlibrary',
    name: 'Open Library',
    category: 'Education & Books',
    url: 'https://openlibrary.org/api',
    description: 'Book information, authors, subjects, covers',
    keyRequired: false,
    rateLimit: 'No strict limit',
    documentation: 'https://openlibrary.org/developers/api',
    priority: 'low'
  },
  {
    id: 'wikipedia',
    name: 'Wikipedia API',
    category: 'Education & Books',
    url: 'https://en.wikipedia.org/api/rest_v1',
    description: 'Wikipedia articles, summaries, page content',
    keyRequired: false,
    rateLimit: '5000 requests/hour',
    documentation: 'https://www.mediawiki.org/wiki/API:Main_page',
    priority: 'low'
  },

  // Multimedia & Images (Priority: LOW)
  {
    id: 'unsplash',
    name: 'Unsplash',
    category: 'Multimedia & Images',
    url: 'https://api.unsplash.com',
    description: 'High-quality photos, collections, user data',
    keyRequired: true,
    rateLimit: '50 requests/hour (free)',
    documentation: 'https://unsplash.com/documentation',
    priority: 'low'
  },
  {
    id: 'pexels',
    name: 'Pexels',
    category: 'Multimedia & Images',
    url: 'https://api.pexels.com/v1',
    description: 'Free stock photos, videos, curated collections',
    keyRequired: true,
    rateLimit: '200 requests/hour (free)',
    documentation: 'https://www.pexels.com/api/documentation/',
    priority: 'low'
  },

  // Government & Public Data (Priority: LOW - NO KEY!)
  {
    id: 'datagovus',
    name: 'Data.gov US',
    category: 'Government & Public Data',
    url: 'https://api.data.gov',
    description: 'US government datasets, statistics, public records',
    keyRequired: false,
    rateLimit: 'Varies by dataset',
    documentation: 'https://api.data.gov/docs/',
    priority: 'low'
  },

  // Science & Research (Priority: LOW - NO KEY!)
  {
    id: 'arxiv',
    name: 'arXiv',
    category: 'Science & Research',
    url: 'https://export.arxiv.org/api/query',
    description: 'Scientific papers, preprints, research articles',
    keyRequired: false,
    rateLimit: '3 seconds between requests',
    documentation: 'https://arxiv.org/help/api',
    priority: 'low'
  }
];

// Utility functions
export const getAPIsByCategory = (category: string): APIEndpoint[] => {
  return GLOBAL_API_REGISTRY.filter(api => api.category === category);
};

export const getAPIsByPriority = (priority: 'high' | 'medium' | 'low'): APIEndpoint[] => {
  return GLOBAL_API_REGISTRY.filter(api => api.priority === priority);
};

export const getFreeAPIs = (): APIEndpoint[] => {
  return GLOBAL_API_REGISTRY.filter(api => !api.keyRequired);
};

export const getAPIById = (id: string): APIEndpoint | undefined => {
  return GLOBAL_API_REGISTRY.find(api => api.id === id);
};

export const getCategories = (): string[] => {
  return [...new Set(GLOBAL_API_REGISTRY.map(api => api.category))];
};

// Priority API recommendations for UltraWebThinking
export const RECOMMENDED_APIS = {
  IMMEDIATE_INTEGRATION: [
    'openweathermap', // Weather for 500+ cities
    'coingecko',      // Crypto data (no key needed!)
    'nasa',           // Space data (no key needed!)
    'covid19_api',    // Health data (no key needed!)
    'spacex'          // SpaceX data (no key needed!)
  ],
  BUSINESS_CRITICAL: [
    'alpha_vantage',  // Financial data
    'mapbox',         // Maps and geolocation
    'newsapi',        // News integration
    'huggingface'     // AI/NLP enhancement
  ],
  ENHANCED_FEATURES: [
    'ipinfo',         // User geolocation
    'openaq',         // Environmental data
    'wikipedia',      // Knowledge base
    'openfda'         // Medical information
  ]
};
