/**
 * Web8 Industrial Production Configuration
 * Production-ready setup për deployment industrial
 *
 * @author UltraWeb Industrial Team
 * @version 8.0.0-PRODUCTION
 */

// Production Environment Variables
export const PRODUCTION_CONFIG = {
  // Application Settings
  APP: {
    NAME: 'EuroWeb Ultra Platform',
    VERSION: '8.0.0-PRODUCTION',
    ENVIRONMENT: 'production',
    PORT: process.env.PORT || 3000,
    BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || 'https://ultra.clisonix.com',
    API_VERSION: 'v1'
  },

  // Security Settings
  SECURITY: {
    SESSION_SECRET: process.env.SESSION_SECRET,
    JWT_SECRET: process.env.JWT_SECRET,
    ENCRYPTION_KEY: process.env.ENCRYPTION_KEY,
    CORS_ORIGINS: [
      'https://ultra.clisonix.com',
      'https://www.ultra.clisonix.com'
    ],
    RATE_LIMIT: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 1000, // limit each IP to 1000 requests per windowMs
      standardHeaders: true,
      legacyHeaders: false
    },
    HELMET_OPTIONS: {
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "https://api.github.com", "https://en.wikipedia.org", "https://ultra.clisonix.com", "https://www.ultra.clisonix.com"]
        }
      },
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
      }
    }
  },

  // Database Configuration
  DATABASE: {
    // MongoDB Production
    MONGODB_URI: process.env.MONGODB_URI,
    MONGODB_DB_NAME: process.env.MONGODB_DB_NAME || 'euroweb_production',

    // Redis Cache
    REDIS_URL: process.env.REDIS_URL,
    REDIS_TTL: 3600, // 1 hour

    // Connection Pool Settings
    MAX_CONNECTIONS: 100,
    MIN_CONNECTIONS: 10,
    CONNECTION_TIMEOUT: 30000
  },

  // External API Services
  APIS: {
    // Search APIs
    SERP_API_KEY: process.env.SERP_API_KEY,
    BING_API_KEY: process.env.BING_API_KEY,
    GOOGLE_API_KEY: process.env.GOOGLE_API_KEY,
    NEWS_API_KEY: process.env.NEWS_API_KEY,

    // AI/ML Services
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,

    // Monitoring
    SENTRY_DSN: process.env.SENTRY_DSN,
    ANALYTICS_ID: process.env.ANALYTICS_ID,

    // Rate Limits per API
    API_RATE_LIMITS: {
      serp: { requests: 100, window: 3600 },
      openai: { requests: 50, window: 60 },
      github: { requests: 5000, window: 3600 }
    }
  },

  // Performance Settings
  PERFORMANCE: {
    // Caching
    CACHE_TTL: {
      static: 31536000, // 1 year
      api: 300, // 5 minutes
      neural: 1800, // 30 minutes
      search: 600 // 10 minutes
    },

    // Compression
    COMPRESSION: {
      threshold: 1024,
      level: 6,
      memLevel: 8
    },

    // CDN Settings
    CDN_URL: process.env.CDN_URL,
    STATIC_ASSETS_URL: process.env.STATIC_ASSETS_URL,

    // Memory Management
    MAX_MEMORY_USAGE: '2GB',
    GC_INTERVAL: 300000 // 5 minutes
  },

  // Monitoring & Logging
  MONITORING: {
    // Logging Levels
    LOG_LEVEL: process.env.LOG_LEVEL || 'info',
    LOG_FORMAT: 'json',

    // Health Check
    HEALTH_CHECK_INTERVAL: 30000, // 30 seconds

    // Metrics
    METRICS_ENABLED: true,
    METRICS_PORT: 9090,

    // Alerts
    ERROR_THRESHOLD: 10,
    RESPONSE_TIME_THRESHOLD: 2000
  },

  // Deployment Settings
  DEPLOYMENT: {
    CLUSTER_MODE: true,
    WORKERS: process.env.WEB_CONCURRENCY || 4,
    GRACEFUL_SHUTDOWN_TIMEOUT: 30000,

    // Health Checks
    READINESS_PROBE: '/api/health/ready',
    LIVENESS_PROBE: '/api/health/live',

    // Auto-scaling
    MIN_REPLICAS: 2,
    MAX_REPLICAS: 10,
    TARGET_CPU_UTILIZATION: 70
  },

  // Feature Flags
  FEATURES: {
    NEURAL_SEARCH: true,
    AGI_PROCESSING: true,
    REAL_TIME_SYNC: true,
    ADVANCED_ANALYTICS: true,
    AUTO_SCALING: true,
    EDGE_COMPUTING: true,
    MULTILINGUAL_SUPPORT: true,
    RTL_LANGUAGES: true,
    AUTO_LANGUAGE_DETECTION: true,
    LANGUAGE_PERSISTENCE: true
  },

  // Internationalization Settings
  I18N: {
    DEFAULT_LANGUAGE: 'sq',
    FALLBACK_LANGUAGE: 'en',
    SUPPORTED_LANGUAGES: [
      'sq', 'en', 'de', 'fr', 'it', 'es', 'pt', 'ru',
      'zh-CN', 'ja', 'ar', 'tr', 'el', 'sr', 'mk', 'bg'
    ],
    RTL_LANGUAGES: ['ar'],
    AUTO_DETECT: true,
    PERSIST_CHOICE: true,
    CACHE_TRANSLATIONS: true,
    TRANSLATION_API: process.env.TRANSLATION_API_KEY,
    FALLBACK_STRATEGY: 'cascade'
  }
};

// Environment Validation
export function validateProductionConfig(): void {
  const required = [
    'SESSION_SECRET',
    'JWT_SECRET',
    'MONGODB_URI',
    'REDIS_URL'
  ];

  const missing = required.filter(key => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }

  }

// Export for use in other modules
export default PRODUCTION_CONFIG;
