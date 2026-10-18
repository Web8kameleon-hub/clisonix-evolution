/**
 * Cube.js Configuration - EuroWeb Platform Analytics
 * Ultra-Industrial Business Intelligence & Real-time Analytics
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-CUBE-ANALYTICS
 * @license MIT
 */

module.exports = {
  // API Configuration
  contextToAppId: ({ securityContext }) => `CUBEJS_APP_${securityContext.tenant || 'default'}`,
  
  // Database Configuration
  driverFactory: ({ dataSource }) => {
    if (dataSource === 'default') {
      return {
        type: 'postgres',
        host: process.env.POSTGRES_HOST || 'localhost',
        port: process.env.POSTGRES_PORT || 5432,
        database: process.env.POSTGRES_DB || 'euroweb_analytics',
        username: process.env.POSTGRES_USER || 'euroweb',
        password: process.env.POSTGRES_PASSWORD,
        ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
        pool: {
          min: 0,
          max: 8,
          acquireTimeoutMillis: 30000,
          createTimeoutMillis: 30000,
          destroyTimeoutMillis: 5000,
          idleTimeoutMillis: 30000,
          reapIntervalMillis: 1000,
          createRetryIntervalMillis: 200
        }
      };
    }
    
    // Additional data sources for multi-tenant architecture
    if (dataSource === 'financial') {
      return {
        type: 'mysql',
        host: process.env.MYSQL_HOST || 'localhost',
        port: process.env.MYSQL_PORT || 3306,
        database: process.env.MYSQL_DB || 'financial_data',
        username: process.env.MYSQL_USER || 'finance_user',
        password: process.env.MYSQL_PASSWORD
      };
    }
    
    if (dataSource === 'realtime') {
      return {
        type: 'clickhouse',
        host: process.env.CLICKHOUSE_HOST || 'localhost',
        port: process.env.CLICKHOUSE_PORT || 8123,
        database: process.env.CLICKHOUSE_DB || 'realtime_analytics',
        username: process.env.CLICKHOUSE_USER || 'analytics',
        password: process.env.CLICKHOUSE_PASSWORD
      };
    }
  },

  // Security & Authentication
  checkAuth: async (req, auth) => {
    // JWT Authentication
    if (!auth) {
      throw new Error('Authentication required');
    }
    
    try {
      const jwt = require('jsonwebtoken');
      const decoded = jwt.verify(auth, process.env.JWT_SECRET || 'euroweb-ultra-secret');
      
      return {
        userId: decoded.sub,
        tenant: decoded.tenant || 'default',
        roles: decoded.roles || ['viewer'],
        permissions: decoded.permissions || []
      };
    } catch (error) {
      throw new Error('Invalid authentication token');
    }
  },

  // Query Authorization
  queryTransformer: (query, { securityContext }) => {
    // Row-level security based on user context
    if (securityContext.tenant !== 'admin') {
      query.filters.push({
        member: 'Users.tenantId',
        operator: 'equals',
        values: [securityContext.tenant]
      });
    }
    
    // Role-based access control
    if (!securityContext.roles.includes('admin')) {
      // Restrict sensitive data access
      const restrictedMeasures = ['Revenue.totalProfit', 'Users.personalData'];
      query.measures = query.measures.filter(m => !restrictedMeasures.includes(m));
    }
    
    return query;
  },

  // Pre-aggregations Configuration
  orchestratorOptions: {
    redisPool: process.env.REDIS_URL ? {
      poolMin: 2,
      poolMax: 10,
      acquireTimeoutMillis: 5000,
      retryDelayOnFailover: 100,
      enableOfflineQueue: false,
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT,
      password: process.env.REDIS_PASSWORD,
      db: process.env.REDIS_DB || 0
    } : undefined,
    
    rollupOnlyMode: process.env.NODE_ENV === 'production',
    
    queryCacheOptions: {
      refreshKeyRenewalThreshold: 30,
      backgroundRenew: true,
      queueOptions: {
        concurrency: 3
      }
    }
  },

  // Development Configuration
  telemetry: false,
  devServer: {
    host: '0.0.0.0',
    port: process.env.CUBE_DEV_PORT || 4000
  },

  // API Configuration
  http: {
    cors: {
      origin: process.env.NODE_ENV === 'production' 
        ? ['https://euroweb.al', 'https://www.euroweb.al']
        : ['http://localhost:3000', 'http://localhost:3002'],
      credentials: true
    }
  },

  // Schema Configuration
  repositoryFactory: ({ securityContext }) => {
    return {
      dataSchemaFiles: () => {
        const baseSchemas = [
          'schema/Users.js',
          'schema/Sessions.js',
          'schema/Events.js',
          'schema/Performance.js'
        ];
        
        // Add tenant-specific schemas
        if (securityContext.tenant === 'financial') {
          baseSchemas.push(
            'schema/Transactions.js',
            'schema/Revenue.js',
            'schema/Stocks.js'
          );
        }
        
        if (securityContext.tenant === 'industrial') {
          baseSchemas.push(
            'schema/Production.js',
            'schema/Machinery.js',
            'schema/Quality.js'
          );
        }
        
        return baseSchemas;
      }
    };
  },

  // Real-time Configuration
  scheduledRefreshTimer: 30, // seconds
  
  // Caching Strategy
  cacheAndQueueDriver: process.env.REDIS_URL ? 'redis' : 'memory',
  
  // Logging
  logger: (msg, params) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[CUBE] ${msg}`, params);
    }
  },

  // Custom Environment Variables
  contextToOrchestratorId: ({ securityContext }) => 
    `${securityContext.tenant}_${process.env.NODE_ENV}`,

  // Pre-aggregation Build Configuration
  preAggregationsSchema: process.env.CUBE_PRE_AGG_SCHEMA || 'pre_aggregations',

  // External Database Refresh
  externalRefresh: async () => {
    // Custom refresh logic for external data sources
    console.log('Refreshing external data sources...');
    
    // Trigger webhook or API call to refresh external data
    if (process.env.EXTERNAL_REFRESH_WEBHOOK) {
      try {
        const fetch = require('node-fetch');
        await fetch(process.env.EXTERNAL_REFRESH_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            timestamp: new Date().toISOString(),
            source: 'cube_refresh'
          })
        });
      } catch (error) {
        console.error('External refresh failed:', error);
      }
    }
  }
};
