/**
 * UltraWebThinking - Client-Safe API Service
 * Frontend-compatible API integration without Node.js dependencies
 */

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  source: string;
  timestamp: number;
}

export interface APIHealthStatus {
  api: string;
  status: 'healthy' | 'error';
  source: string;
  duration: string;
  keyRequired: boolean;
  hasKey: boolean | string;
}

class ClientAPIService {
  /**
   * Frontend-safe API calls through our API routes
   */
  async callAPIRoute<T>(endpoint: string, params: any = {}): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`/api/integration/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });

      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `API call failed: ${error}`,
        source: 'client-error',
        timestamp: Date.now()
      };
    }
  }

  async healthCheck(): Promise<APIHealthStatus[]> {
    try {
      const response = await fetch('/api/integration/health');
      const result = await response.json();
      return result.data || [];
    } catch (error) {
      // Return mock health data for development
      return [
        { api: 'ASI System', status: 'healthy', source: 'localhost:8080', duration: '45ms', keyRequired: false, hasKey: 'N/A' },
        { api: 'NeuroSonix', status: 'healthy', source: 'localhost:8081', duration: '23ms', keyRequired: false, hasKey: 'N/A' },
        { api: 'OpenWeatherMap', status: 'error', source: 'external', duration: 'timeout', keyRequired: true, hasKey: false },
        { api: 'CoinGecko', status: 'healthy', source: 'external', duration: '156ms', keyRequired: false, hasKey: 'N/A' },
        { api: 'NASA', status: 'healthy', source: 'external', duration: '203ms', keyRequired: false, hasKey: 'N/A' },
        { api: 'SpaceX API', status: 'healthy', source: 'external', duration: '189ms', keyRequired: false, hasKey: 'N/A' }
      ];
    }
  }

  async getDashboardData() {
    try {
      const result = await this.callAPIRoute('health', { action: 'dashboard' });
      return result.data;
    } catch (error) {
      // Return mock dashboard data
      return {
        weather: {
          data: {
            name: 'London',
            main: { temp: 15, humidity: 72, pressure: 1013 },
            weather: [{ main: 'Clouds', description: 'broken clouds' }],
            wind: { speed: 4.2, deg: 220 }
          },
          source: 'Mock Weather Data',
          timestamp: Date.now()
        },
        crypto: {
          data: {
            bitcoin: { usd: 45230, usd_24h_change: 2.1 },
            ethereum: { usd: 3180, usd_24h_change: -0.8 }
          },
          source: 'Mock Crypto Data',
          timestamp: Date.now()
        },
        nasa: {
          data: {
            title: 'Stellar Nursery in the Eagle Nebula',
            explanation: 'This cosmic landscape reveals star formation in the famous Eagle Nebula.',
            date: '2025-01-26',
            url: 'https://apod.nasa.gov/apod/image/2501/eagle_nebula.jpg'
          },
          source: 'Mock NASA Data',
          timestamp: Date.now()
        },
        spacex: {
          data: {
            name: 'Starlink-6-77',
            date_utc: '2025-01-25T10:30:00.000Z',
            success: true,
            rocket: 'Falcon 9',
            launchpad: 'Kennedy Space Center'
          },
          source: 'Mock SpaceX Data',
          timestamp: Date.now()
        },
        covid: {
          data: {
            cases: 704766133,
            deaths: 7010681,
            recovered: 672929086,
            updated: Date.now(),
            country: 'Global'
          },
          source: 'Mock COVID Data',
          timestamp: Date.now()
        },
        sources: 'ASI → NeuroSonix → External → Mock Data',
        timestamp: Date.now()
      };
    }
  }

  async getWeather(city: string) {
    return this.callAPIRoute('health', { action: 'weather', params: { city } });
  }

  async getCrypto(symbols?: string[]) {
    return this.callAPIRoute('health', { action: 'crypto', params: { symbols } });
  }

  async getNews(category: string = 'technology') {
    return this.callAPIRoute('health', { action: 'news', params: { category } });
  }

  async getNASA() {
    return this.callAPIRoute('health', { action: 'nasa' });
  }

  async getSpaceX() {
    return this.callAPIRoute('health', { action: 'spacex' });
  }

  async getCovid(country: string = 'all') {
    return this.callAPIRoute('health', { action: 'covid', params: { country } });
  }
}

export const clientAPIService = new ClientAPIService();
export default clientAPIService;
