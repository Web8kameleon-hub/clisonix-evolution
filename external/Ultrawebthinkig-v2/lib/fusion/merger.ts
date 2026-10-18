/**
 * 🌍 Multi-Source Data Fusion Engine
 * Combines local Cube.js data with external APIs (WorldBank, Guardian, Reuters)
 * 
 * @version 1.0.0
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 */

export interface DataPoint {
  x: string;
  [key: string]: any;
}

export interface ExternalDataSource {
  source: 'worldbank' | 'guardian' | 'reuters' | 'opendata';
  data: any[];
  timestamp: number;
  reliability: number; // 0-1 score
}

/**
 * 🔗 Main Data Fusion Function
 */
export function mergeDataSets(
  primaryData: DataPoint[],
  externalData: any[],
  options: MergeOptions = {}
): DataPoint[] {
  if (!externalData || externalData.length === 0) {
    return primaryData;
  }

  try {
    const merged = primaryData.map(primaryPoint => {
      const matchingExternal = findMatchingDataPoint(
        primaryPoint,
        externalData,
        options.matchStrategy || 'date'
      );

      if (matchingExternal) {
        return {
          ...primaryPoint,
          ...enrichWithExternalData(primaryPoint, matchingExternal, options)
        };
      }

      return primaryPoint;
    });

    return merged;
  } catch (error) {
    console.warn('Data fusion failed:', error);
    return primaryData;
  }
}

export interface MergeOptions {
  matchStrategy?: 'date' | 'nearest' | 'interpolate';
  externalPrefix?: string;
  confidenceThreshold?: number;
  smoothing?: boolean;
}

/**
 * 🎯 Find Matching External Data Point
 */
function findMatchingDataPoint(
  primaryPoint: DataPoint,
  externalData: any[],
  strategy: 'date' | 'nearest' | 'interpolate'
): any | null {
  const primaryDate = new Date(primaryPoint.x);

  switch (strategy) {
    case 'date':
      return externalData.find(ext => {
        const extDate = new Date(ext.date || ext.timestamp || ext.x);
        return isSameDay(primaryDate, extDate);
      });

    case 'nearest':
      return findNearestByDate(primaryDate, externalData);

    case 'interpolate':
      return interpolateValue(primaryDate, externalData);

    default:
      return null;
  }
}

/**
 * 📈 Enrich Primary Data with External Context
 */
function enrichWithExternalData(
  primaryPoint: DataPoint,
  externalPoint: any,
  options: MergeOptions
): Record<string, any> {
  const prefix = options.externalPrefix || 'external';
  const enriched: Record<string, any> = {};

  // Economic indicators from World Bank
  if (externalPoint.gdp_growth) {
    enriched[`${prefix}.gdp_growth`] = externalPoint.gdp_growth;
  }
  if (externalPoint.inflation_rate) {
    enriched[`${prefix}.inflation`] = externalPoint.inflation_rate;
  }
  if (externalPoint.unemployment) {
    enriched[`${prefix}.unemployment`] = externalPoint.unemployment;
  }

  // Market sentiment from news APIs
  if (externalPoint.sentiment_score) {
    enriched[`${prefix}.sentiment`] = externalPoint.sentiment_score;
  }
  if (externalPoint.market_volatility) {
    enriched[`${prefix}.volatility`] = externalPoint.market_volatility;
  }

  // Currency exchange rates
  if (externalPoint.exchange_rate) {
    enriched[`${prefix}.exchange_rate`] = externalPoint.exchange_rate;
  }

  // Apply smoothing if requested
  if (options.smoothing) {
    Object.keys(enriched).forEach(key => {
      if (typeof enriched[key] === 'number') {
        enriched[key] = applySmoothing(enriched[key]);
      }
    });
  }

  return enriched;
}

/**
 * 🌍 World Bank Data Integration
 */
export async function fetchWorldBankData(
  country = 'ALB', // Albania
  indicators = ['NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG'] // GDP growth, Inflation
): Promise<any[]> {
  try {
    const promises = indicators.map(indicator =>
      fetch(`https://api.worldbank.org/v2/country/${country}/indicator/${indicator}?format=json&per_page=100&date=2020:2025`)
        .then(r => r.json())
    );

    const results = await Promise.all(promises);
    
    // Process and normalize World Bank data
    const normalized = results.flatMap((result, index) => {
      if (!Array.isArray(result) || result.length < 2) return [];
      
      const data = result[1]; // World Bank returns [metadata, data]
      if (!Array.isArray(data)) return [];
      
      return data
        .filter(item => item.value !== null)
        .map(item => ({
          date: `${item.date}-01-01`,
          indicator: indicators[index],
          value: item.value,
          country: item.country?.value,
          source: 'worldbank'
        }));
    });

    return normalized;
  } catch (error) {
    console.warn('World Bank API failed:', error);
    return [];
  }
}

/**
 * 📰 Guardian News Sentiment Analysis
 */
export async function fetchGuardianSentiment(
  section = 'business',
  pageSize = 20
): Promise<any[]> {
  try {
    // Note: In production, you'd need Guardian API key
    const response = await fetch(
      `https://content.guardianapis.com/search?section=${section}&page-size=${pageSize}&api-key=${process.env.GUARDIAN_API_KEY || 'test'}`
    );
    
    if (!response.ok) {
      throw new Error(`Guardian API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Simple sentiment analysis (in production, use NLP service)
    return data.response?.results?.map((article: any) => ({
      date: article.webPublicationDate.split('T')[0],
      headline: article.webTitle,
      sentiment_score: analyzeSentiment(article.webTitle), // -1 to 1
      url: article.webUrl,
      source: 'guardian'
    })) || [];
  } catch (error) {
    console.warn('Guardian API failed:', error);
    return [];
  }
}

/**
 * 📊 Reuters Market Data Integration
 */
export async function fetchReutersMarketData(): Promise<any[]> {
  try {
    // Mock data for now (Reuters requires enterprise access)
    return generateMockMarketData();
  } catch (error) {
    console.warn('Reuters API failed:', error);
    return [];
  }
}

// =================== HELPER FUNCTIONS ===================

function isSameDay(date1: Date, date2: Date): boolean {
  return date1.toDateString() === date2.toDateString();
}

function findNearestByDate(targetDate: Date, data: any[]): any | null {
  if (!data.length) return null;

  let nearest = data[0];
  let minDiff = Math.abs(targetDate.getTime() - new Date(nearest.date || nearest.x).getTime());

  for (const item of data) {
    const itemDate = new Date(item.date || item.x);
    const diff = Math.abs(targetDate.getTime() - itemDate.getTime());
    
    if (diff < minDiff) {
      minDiff = diff;
      nearest = item;
    }
  }

  return nearest;
}

function interpolateValue(targetDate: Date, data: any[]): any | null {
  if (data.length < 2) return findNearestByDate(targetDate, data);

  // Sort data by date
  const sortedData = data
    .map(item => ({
      ...item,
      parsedDate: new Date(item.date || item.x)
    }))
    .sort((a, b) => a.parsedDate.getTime() - b.parsedDate.getTime());

  const targetTime = targetDate.getTime();

  // Find surrounding points
  let before = null;
  let after = null;

  for (const item of sortedData) {
    if (item.parsedDate.getTime() <= targetTime) {
      before = item;
    } else if (item.parsedDate.getTime() > targetTime && !after) {
      after = item;
      break;
    }
  }

  if (!before && !after) return null;
  if (!before) return after;
  if (!after) return before;

  // Linear interpolation
  const beforeTime = before.parsedDate.getTime();
  const afterTime = after.parsedDate.getTime();
  const ratio = (targetTime - beforeTime) / (afterTime - beforeTime);

  const interpolated: any = {
    date: targetDate.toISOString().split('T')[0],
    source: 'interpolated'
  };

  // Interpolate numeric values
  Object.keys(before).forEach(key => {
    if (typeof before[key] === 'number' && typeof after[key] === 'number') {
      interpolated[key] = before[key] + (after[key] - before[key]) * ratio;
    }
  });

  return interpolated;
}

function applySmoothing(value: number, factor = 0.1): number {
  // Simple exponential smoothing
  return Math.round(value * (1 - factor) * 100) / 100;
}

function analyzeSentiment(text: string): number {
  // Simple sentiment analysis (in production, use proper NLP)
  const positiveWords = ['growth', 'increase', 'profit', 'success', 'strong', 'up', 'rise'];
  const negativeWords = ['decline', 'fall', 'loss', 'weak', 'down', 'crisis', 'drop'];
  
  const lowerText = text.toLowerCase();
  let score = 0;
  
  positiveWords.forEach(word => {
    if (lowerText.includes(word)) score += 0.1;
  });
  
  negativeWords.forEach(word => {
    if (lowerText.includes(word)) score -= 0.1;
  });
  
  return Math.max(-1, Math.min(1, score));
}

function generateMockMarketData(): any[] {
  // Generate realistic market data for demonstration
  const now = new Date();
  const data = [];
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    data.push({
      date: date.toISOString().split('T')[0],
      market_volatility: Math.random() * 0.3 + 0.1, // 0.1-0.4
      exchange_rate: 1.0 + (Math.random() - 0.5) * 0.1, // 0.95-1.05
      sentiment_score: (Math.random() - 0.5) * 2, // -1 to 1
      source: 'reuters_mock'
    });
  }
  
  return data;
}
