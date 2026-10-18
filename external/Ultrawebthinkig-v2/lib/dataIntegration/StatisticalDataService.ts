/**
 * ASI Statistical Data Service
 * Real-time integration with free statistical data sources
 * 
 * @author Ledjan Ahmati - ASI Ultimate World
 * @version 8.0.0-STATS
 */

export interface StatisticalDataPoint {
  source: string;
  indicator: string;
  country?: string;
  value: number;
  unit: string;
  date: string;
  timestamp: number;
}

export interface EconomicIndicators {
  gdp: StatisticalDataPoint;
  inflation: StatisticalDataPoint;
  unemployment: StatisticalDataPoint;
  population: StatisticalDataPoint;
}

export class StatisticalDataService {
  private static instance: StatisticalDataService;
  private cache: Map<string, { data: any; expires: number }> = new Map();
  private readonly CACHE_DURATION = 15 * 60 * 1000; // 15 minutes

  static getInstance(): StatisticalDataService {
    if (!StatisticalDataService.instance) {
      StatisticalDataService.instance = new StatisticalDataService();
    }
    return StatisticalDataService.instance;
  }

  private async fetchWithCache(url: string, cacheKey: string): Promise<any> {
    // Check cache first
    const cached = this.cache.get(cacheKey);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Cache the result
      this.cache.set(cacheKey, {
        data,
        expires: Date.now() + this.CACHE_DURATION
      });
      
      return data;
    } catch (error) {
      console.error(`Statistical data fetch error for ${cacheKey}:`, error);
      return null;
    }
  }

  // World Bank Data Integration
  async getWorldBankData(indicator: string, country: string = 'WLD'): Promise<StatisticalDataPoint | null> {
    const url = `https://api.worldbank.org/v2/country/${country}/indicator/${indicator}?format=json&date=2023&per_page=1`;
    const cacheKey = `worldbank_${indicator}_${country}`;
    
    const data = await this.fetchWithCache(url, cacheKey);
    if (!data || !data[1] || !data[1][0]) return null;

    const item = data[1][0];
    return {
      source: 'World Bank',
      indicator,
      country: item.country?.value || country,
      value: item.value,
      unit: 'USD' + (indicator.includes('GDP') ? ' (billions)' : ''),
      date: item.date,
      timestamp: Date.now()
    };
  }

  // Yahoo Finance Integration
  async getFinancialData(symbol: string): Promise<StatisticalDataPoint | null> {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`;
    const cacheKey = `yahoo_${symbol}`;
    
    const data = await this.fetchWithCache(url, cacheKey);
    if (!data?.chart?.result?.[0]?.meta) return null;

    const meta = data.chart.result[0].meta;
    return {
      source: 'Yahoo Finance',
      indicator: symbol,
      value: meta.regularMarketPrice || meta.previousClose,
      unit: meta.currency || 'USD',
      date: new Date().toISOString().split('T')[0],
      timestamp: Date.now()
    };
  }

  // Federal Reserve Economic Data (FRED)
  async getFREDData(seriesId: string): Promise<StatisticalDataPoint | null> {
    // Note: FRED requires API key, using alternative approach
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=demo&file_type=json&limit=1&sort_order=desc`;
    const cacheKey = `fred_${seriesId}`;
    
    const data = await this.fetchWithCache(url, cacheKey);
    if (!data?.observations?.[0]) return null;

    const obs = data.observations[0];
    return {
      source: 'FRED',
      indicator: seriesId,
      country: 'USA',
      value: parseFloat(obs.value),
      unit: '%', // Most FRED data is percentage
      date: obs.date,
      timestamp: Date.now()
    };
  }

  // Get comprehensive economic indicators for a country
  async getEconomicIndicators(countryCode: string = 'ALB'): Promise<EconomicIndicators | null> {
    try {
      const [gdp, inflation, unemployment, population] = await Promise.all([
        this.getWorldBankData('NY.GDP.MKTP.CD', countryCode), // GDP
        this.getWorldBankData('FP.CPI.TOTL.ZG', countryCode), // Inflation
        this.getWorldBankData('SL.UEM.TOTL.ZS', countryCode), // Unemployment
        this.getWorldBankData('SP.POP.TOTL', countryCode)     // Population
      ]);

      if (!gdp || !inflation || !unemployment || !population) {
        return null;
      }

      return { gdp, inflation, unemployment, population };
    } catch (error) {
      console.error('Error fetching economic indicators:', error);
      return null;
    }
  }

  // Get live market data
  async getLiveMarketData(): Promise<StatisticalDataPoint[]> {
    const symbols = ['EURUSD=X', 'BTC-USD', 'AAPL', 'TSLA'];
    const results: StatisticalDataPoint[] = [];

    for (const symbol of symbols) {
      const data = await this.getFinancialData(symbol);
      if (data) {
        results.push(data);
      }
    }

    return results;
  }

  // Get Albanian specific data
  async getAlbanianEconomicData(): Promise<EconomicIndicators | null> {
    return this.getEconomicIndicators('ALB');
  }

  // Get global comparison data
  async getGlobalComparison(): Promise<{ [country: string]: EconomicIndicators }> {
    const countries = ['USA', 'DEU', 'FRA', 'ITA', 'ALB', 'MKD', 'SRB'];
    const results: { [country: string]: EconomicIndicators } = {};

    for (const country of countries) {
      const data = await this.getEconomicIndicators(country);
      if (data) {
        results[country] = data;
      }
    }

    return results;
  }

  // Clear cache (for testing/refresh)
  clearCache(): void {
    this.cache.clear();
  }

  // Get cache statistics
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}
