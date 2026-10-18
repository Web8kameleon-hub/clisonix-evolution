/**
 * Web8 Real Search Configuration
 * Setup për API keys dhe konfigurimin e motorit real të kërkimit
 * 
 * @author UltraWeb Team
 * @version 8.0.0-REAL-SEARCH-CONFIG
 */

// Environment Variables për Real Search APIs
export const REAL_SEARCH_CONFIG = {
  // SerpAPI - Për kërkime web profesionale
  SERPAPI_KEY: process.env.NEXT_PUBLIC_SERPAPI_KEY || process.env.SERPAPI_KEY,
  
  // Bing Search API - Microsoft
  BING_SEARCH_KEY: process.env.NEXT_PUBLIC_BING_SEARCH_KEY || process.env.BING_SEARCH_KEY,
  
  // Google Custom Search
  GOOGLE_API_KEY: process.env.NEXT_PUBLIC_GOOGLE_API_KEY || process.env.GOOGLE_API_KEY,
  GOOGLE_SEARCH_ENGINE_ID: process.env.NEXT_PUBLIC_GOOGLE_SEARCH_ENGINE_ID || process.env.GOOGLE_SEARCH_ENGINE_ID,
  
  // News API
  NEWS_API_KEY: process.env.NEXT_PUBLIC_NEWS_API_KEY || process.env.NEWS_API_KEY,
  
  // YouTube Data API
  YOUTUBE_API_KEY: process.env.NEXT_PUBLIC_YOUTUBE_API_KEY || process.env.YOUTUBE_API_KEY,
  
  // OpenWeatherMap (për local search)
  OPENWEATHER_API_KEY: process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY || process.env.OPENWEATHER_API_KEY,
  
  // Rate limiting configuration
  RATE_LIMIT: {
    REQUESTS_PER_MINUTE: 60,
    REQUESTS_PER_HOUR: 1000,
    CONCURRENT_REQUESTS: 5
  },
  
  // Cache configuration
  CACHE: {
    ENABLED: true,
    TTL_SECONDS: 300, // 5 minutes
    MAX_SIZE: 1000 // Max cached items
  },
  
  // Search configuration
  SEARCH: {
    MAX_RESULTS: 20,
    TIMEOUT_MS: 15000,
    USER_AGENT: 'UltraWeb/8.0 Real Search Engine',
    ENABLE_FALLBACK: true
  }
};

// Validation function
export function validateSearchConfig(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check if at least one search API is configured
  const hasSearchAPI = !!(
    REAL_SEARCH_CONFIG.SERPAPI_KEY ||
    REAL_SEARCH_CONFIG.BING_SEARCH_KEY ||
    REAL_SEARCH_CONFIG.GOOGLE_API_KEY
  );
  
  if (!hasSearchAPI) {
    errors.push('❌ No search API configured. Set SERPAPI_KEY, BING_SEARCH_KEY, or GOOGLE_API_KEY');
  }
  
  // Validate Google Custom Search
  if (REAL_SEARCH_CONFIG.GOOGLE_API_KEY && !REAL_SEARCH_CONFIG.GOOGLE_SEARCH_ENGINE_ID) {
    errors.push('❌ Google API key found but GOOGLE_SEARCH_ENGINE_ID is missing');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// Environment setup instructions
export const SETUP_INSTRUCTIONS = `
🔧 Web8 Real Search Engine Setup Instructions

1. SerpAPI (Recommended for web search):
   - Register at: https://serpapi.com/
   - Get your API key
   - Set: NEXT_PUBLIC_SERPAPI_KEY=your_key_here

2. Bing Search API (Microsoft):
   - Register at: https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/
   - Get your subscription key
   - Set: NEXT_PUBLIC_BING_SEARCH_KEY=your_key_here

3. Google Custom Search:
   - Create project at: https://console.developers.google.com/
   - Enable Custom Search API
   - Create custom search engine at: https://cse.google.com/
   - Set: NEXT_PUBLIC_GOOGLE_API_KEY=your_key_here
   - Set: NEXT_PUBLIC_GOOGLE_SEARCH_ENGINE_ID=your_engine_id

4. News API (For news search):
   - Register at: https://newsapi.org/
   - Get your API key
   - Set: NEXT_PUBLIC_NEWS_API_KEY=your_key_here

5. YouTube Data API (For video search):
   - Enable at: https://console.developers.google.com/
   - Set: NEXT_PUBLIC_YOUTUBE_API_KEY=your_key_here

Environment file example (.env.local):
NEXT_PUBLIC_SERPAPI_KEY=your_serpapi_key_here
NEXT_PUBLIC_BING_SEARCH_KEY=your_bing_key_here
NEXT_PUBLIC_NEWS_API_KEY=your_news_api_key_here

⚠️  IMPORTANT: Web8 does NOT use mock data!
   Every search connects to real APIs or scraping engines.
   Configure at least one API key for the system to work.
`;

// Configuration checker
export function checkRealSearchStatus(): {
  status: 'ready' | 'partial' | 'not-configured';
  availableServices: string[];
  missingServices: string[];
  message: string;
} {
  const availableServices: string[] = [];
  const missingServices: string[] = [];
  
  // Check each service
  const services = [
    { name: 'SerpAPI', key: REAL_SEARCH_CONFIG.SERPAPI_KEY },
    { name: 'Bing Search', key: REAL_SEARCH_CONFIG.BING_SEARCH_KEY },
    { name: 'Google Search', key: REAL_SEARCH_CONFIG.GOOGLE_API_KEY && REAL_SEARCH_CONFIG.GOOGLE_SEARCH_ENGINE_ID },
    { name: 'News API', key: REAL_SEARCH_CONFIG.NEWS_API_KEY },
    { name: 'YouTube API', key: REAL_SEARCH_CONFIG.YOUTUBE_API_KEY }
  ];
  
  services.forEach(service => {
    if (service.key) {
      availableServices.push(service.name);
    } else {
      missingServices.push(service.name);
    }
  });
  
  let status: 'ready' | 'partial' | 'not-configured';
  let message: string;
  
  if (availableServices.length === 0) {
    status = 'not-configured';
    message = '❌ No search APIs configured. Web8 real search engine is not functional.';
  } else if (availableServices.length < 3) {
    status = 'partial';
    message = `⚠️  Partial configuration. ${availableServices.length} service(s) available: ${availableServices.join(', ')}`;
  } else {
    status = 'ready';
    message = `✅ Web8 real search engine ready! ${availableServices.length} service(s) configured: ${availableServices.join(', ')}`;
  }
  
  return {
    status,
    availableServices,
    missingServices,
    message
  };
}

export default REAL_SEARCH_CONFIG;
