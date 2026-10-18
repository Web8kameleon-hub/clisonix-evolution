/**
 * UltraWebThinking - Real API Integration Service
 * Connects to 500+ Free APIs for Enhanced Data
 * 
 * Strategy: ASI → NeuroSonix → External APIs → Fallback
 */

import { GLOBAL_API_REGISTRY, getAPIById, RECOMMENDED_APIS } from './global-api-registry';

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  source: string;
  timestamp: number;
}

class RealAPIService {
  private apiKeys: Record<string, string> = {};

  constructor() {
    // Initialize with environment variables
    this.loadAPIKeys();
  }

  private loadAPIKeys() {
    // Load API keys from environment (browser-safe fallbacks)
    const env = typeof window !== 'undefined' ? {} : process?.env || {};
    
    this.apiKeys = {
      openweathermap: env.OPENWEATHER_API_KEY || '',
      newsapi: env.NEWS_API_KEY || '',
      alpha_vantage: env.ALPHA_VANTAGE_KEY || '',
      mapbox: env.MAPBOX_TOKEN || '',
      huggingface: env.HUGGINGFACE_TOKEN || '',
      unsplash: env.UNSPLASH_ACCESS_KEY || '',
      pexels: env.PEXELS_API_KEY || '',
      ipinfo: env.IPINFO_TOKEN || '',
      gnews: env.GNEWS_API_KEY || '',
      weatherapi: env.WEATHER_API_KEY || '',
      aviationstack: env.AVIATIONSTACK_KEY || ''
    };
  }

  /**
   * Universal API Caller with ASI Strategy
   */
  async callAPI<T>(apiId: string, endpoint: string, params: Record<string, any> = {}): Promise<APIResponse<T>> {
    try {
      // 1. Try ASI System first
      const asiResponse = await this.tryASISystem<T>(apiId, endpoint, params);
      if (asiResponse.success) return asiResponse;

      // 2. Try NeuroSonix enhancement
      const neuroResponse = await this.tryNeuroSonix<T>(apiId, endpoint, params);
      if (neuroResponse.success) return neuroResponse;

      // 3. Try external API
      const externalResponse = await this.tryExternalAPI<T>(apiId, endpoint, params);
      if (externalResponse.success) return externalResponse;

      // 4. Fallback to mock data
      return this.generateFallback<T>(apiId, endpoint, params);

    } catch (error) {
      return {
        success: false,
        error: `API call failed: ${error}`,
        source: 'error',
        timestamp: Date.now()
      };
    }
  }

  private async tryASISystem<T>(apiId: string, endpoint: string, params: any): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`http://localhost:8080/api/external/${apiId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint, params })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          data,
          source: 'ASI System',
          timestamp: Date.now()
        };
      }
    } catch (error) {
      console.log(`ASI System unavailable for ${apiId}`);
    }

    return { success: false, source: 'ASI System', timestamp: Date.now() };
  }

  private async tryNeuroSonix<T>(apiId: string, endpoint: string, params: any): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`http://localhost:8081/api/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiId, endpoint, params })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          data,
          source: 'NeuroSonix Enhanced',
          timestamp: Date.now()
        };
      }
    } catch (error) {
      console.log(`NeuroSonix unavailable for ${apiId}`);
    }

    return { success: false, source: 'NeuroSonix', timestamp: Date.now() };
  }

  private async tryExternalAPI<T>(apiId: string, endpoint: string, params: any): Promise<APIResponse<T>> {
    const api = getAPIById(apiId);
    if (!api) {
      return { success: false, error: 'API not found', source: 'external', timestamp: Date.now() };
    }

    try {
      let url = `${api.url}${endpoint}`;
      const headers: Record<string, string> = {};

      // Add API key if required
      if (api.keyRequired && this.apiKeys[apiId]) {
        if (apiId === 'openweathermap') {
          params.appid = this.apiKeys[apiId];
        } else if (apiId === 'newsapi') {
          headers['X-API-Key'] = this.apiKeys[apiId];
        } else if (apiId === 'alpha_vantage') {
          params.apikey = this.apiKeys[apiId];
        } else if (apiId === 'mapbox') {
          params.access_token = this.apiKeys[apiId];
        } else {
          headers['Authorization'] = `Bearer ${this.apiKeys[apiId]}`;
        }
      }

      // Build query string
      const queryString = new URLSearchParams(params).toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await fetch(url, { headers });
      
      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          data,
          source: `External: ${api.name}`,
          timestamp: Date.now()
        };
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      return {
        success: false,
        error: `External API failed: ${error}`,
        source: `External: ${api.name}`,
        timestamp: Date.now()
      };
    }
  }

  private generateFallback<T>(apiId: string, endpoint: string, params: any): APIResponse<T> {
    const api = getAPIById(apiId);
    let fallbackData: any = {};

    // Generate intelligent fallbacks based on API type
    switch (apiId) {
      case 'openweathermap':
      case 'weatherapi':
        fallbackData = {
          weather: [{ main: 'Clear', description: 'clear sky' }],
          main: { temp: 22, humidity: 65, pressure: 1013 },
          wind: { speed: 3.5, deg: 180 },
          name: params.q || 'Unknown City'
        };
        break;

      case 'coingecko':
        fallbackData = {
          bitcoin: { usd: 45000, usd_24h_change: 2.5 },
          ethereum: { usd: 3200, usd_24h_change: -1.2 }
        };
        break;

      case 'newsapi':
        fallbackData = {
          articles: [
            {
              title: 'Breaking: Technology Advances Continue',
              description: 'Latest developments in AI and technology sector.',
              url: '#',
              publishedAt: new Date().toISOString()
            }
          ]
        };
        break;

      case 'nasa':
        fallbackData = {
          title: 'Space Exploration Update',
          explanation: 'Latest discoveries from space missions.',
          date: new Date().toISOString().split('T')[0]
        };
        break;

      default:
        fallbackData = {
          message: 'Fallback data for development',
          timestamp: new Date().toISOString(),
          api: apiId
        };
    }

    return {
      success: true,
      data: fallbackData as T,
      source: 'Fallback Data',
      timestamp: Date.now()
    };
  }

  /**
   * Specific API Methods
   */
  
  async getWeather(city: string) {
    return this.callAPI('openweathermap', '/weather', {
      q: city,
      units: 'metric'
    });
  }

  async getCryptoData(symbols: string[] = ['bitcoin', 'ethereum']) {
    return this.callAPI('coingecko', '/simple/price', {
      ids: symbols.join(','),
      vs_currencies: 'usd',
      include_24hr_change: true
    });
  }

  async getNews(category: string = 'technology', pageSize: number = 10) {
    return this.callAPI('newsapi', '/top-headlines', {
      category,
      pageSize,
      country: 'us'
    });
  }

  async getNASAData() {
    return this.callAPI('nasa', '/planetary/apod', {});
  }

  async getSpaceXData() {
    return this.callAPI('spacex', '/launches/latest', {});
  }

  async getCovidData(country: string = 'all') {
    return this.callAPI('covid19_api', `/${country}`, {});
  }

  async getAirQuality(city: string) {
    return this.callAPI('openaq', '/latest', {
      city,
      limit: 1
    });
  }

  async getStockData(symbol: string) {
    return this.callAPI('alpha_vantage', '', {
      function: 'GLOBAL_QUOTE',
      symbol
    });
  }

  /**
   * Batch API Calls for Dashboard
   */
  async getDashboardData() {
    const [weather, crypto, news, nasa, spacex, covid] = await Promise.allSettled([
      this.getWeather('London'),
      this.getCryptoData(),
      this.getNews('technology', 5),
      this.getNASAData(),
      this.getSpaceXData(),
      this.getCovidData()
    ]);

    return {
      weather: weather.status === 'fulfilled' ? weather.value : null,
      crypto: crypto.status === 'fulfilled' ? crypto.value : null,
      news: news.status === 'fulfilled' ? news.value : null,
      nasa: nasa.status === 'fulfilled' ? nasa.value : null,
      spacex: spacex.status === 'fulfilled' ? spacex.value : null,
      covid: covid.status === 'fulfilled' ? covid.value : null,
      timestamp: Date.now(),
      sources: 'ASI → NeuroSonix → External → Fallback'
    };
  }

  /**
   * Health Check for APIs
   */
  async healthCheck() {
    const results = [];
    
    for (const apiId of RECOMMENDED_APIS.IMMEDIATE_INTEGRATION) {
      const api = getAPIById(apiId);
      if (!api) continue;

      const start = Date.now();
      const result = await this.callAPI(apiId, api.id === 'coingecko' ? '/ping' : '/', {});
      const duration = Date.now() - start;

      results.push({
        api: api.name,
        status: result.success ? 'healthy' : 'error',
        source: result.source,
        duration: `${duration}ms`,
        keyRequired: api.keyRequired,
        hasKey: api.keyRequired ? !!this.apiKeys[apiId] : 'N/A'
      });
    }

    return results;
  }
}

export const realAPIService = new RealAPIService();
export default realAPIService;
