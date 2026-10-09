#!/usr/bin/env node
/**
 * BALANCER SERVICE (Port 3338)
 * TypeScript Implementation
 * 
 * Advanced load balancing with:
 * - Query complexity analysis
 * - Connection pooling
 * - Resource management
 * - Database performance optimization
 */

import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import axios from 'axios';
import { Pool, PoolClient } from 'pg';
import http from 'http';

interface QueryStats {
  queryId: string;
  complexity: number;
  executionTime: number;
  rowsAffected: number;
  status: 'fast' | 'slow' | 'critical';
}

interface PoolStats {
  totalConnections: number;
  activeConnections: number;
  idleConnections: number;
  waitingRequests: number;
  poolSize: number;
  maxSize: number;
}

interface LoadBalanceDecision {
  routeToNode: string;
  reason: string;
  complexity: number;
  estimatedTime: number;
}

const app: Express = express();
const PORT = parseInt(process.env.BALANCER_TS_PORT || '3338', 10);
const HOST = process.env.BALANCER_TS_HOST || '0.0.0.0';

// Middleware
app.use(express.json());
app.use(cors());

// PostgreSQL Connection Pool Configuration
const dbConfig = {
  host: process.env.DB_HOST || 'postgres',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME || 'readme_to_recover',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  
  // Connection pooling tuning
  max: parseInt(process.env.DB_POOL_SIZE || '20', 10),              // Maximum pool size
  min: parseInt(process.env.DB_POOL_MIN || '5', 10),                // Minimum connections
  idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000', 10),  // 30 seconds
  connectionTimeoutMillis: parseInt(process.env.DB_CONN_TIMEOUT || '10000', 10), // 10 seconds
  statement_timeout: parseInt(process.env.DB_STATEMENT_TIMEOUT || '30000', 10), // 30 seconds
};

const pool = new Pool(dbConfig);

// Metrics
const metrics = {
  startTime: new Date(),
  requestsProcessed: 0,
  queriesAnalyzed: 0,
  slowQueriesDetected: 0,
  connectionPoolStats: [] as PoolStats[],
};

// Query complexity calculator
class QueryAnalyzer {
  static calculateComplexity(query: string): number {
    let complexity = 0;
    
    // Join complexity
    complexity += (query.match(/JOIN/gi)?.length || 0) * 10;
    
    // Subquery complexity
    complexity += (query.match(/SELECT/gi)?.length || 0) * 5;
    
    // Group by complexity
    if (query.match(/GROUP BY/i)) complexity += 15;
    
    // Order by complexity
    if (query.match(/ORDER BY/i)) complexity += 10;
    
    // Where clause complexity
    complexity += (query.match(/WHERE|AND|OR/gi)?.length || 0) * 3;
    
    // Window functions
    if (query.match(/OVER|PARTITION BY/i)) complexity += 20;
    
    return complexity;
  }

  static categorizeSeverity(complexity: number): 'fast' | 'slow' | 'critical' {
    if (complexity < 20) return 'fast';
    if (complexity < 50) return 'slow';
    return 'critical';
  }
}

// Connection Pool Manager
class PoolManager {
  static async getStats(): Promise<PoolStats> {
    return {
      totalConnections: pool.totalCount,
      activeConnections: pool.waitingCount === 0 ? pool.totalCount - (pool.idleCount || 0) : pool.totalCount,
      idleConnections: pool.idleCount || 0,
      waitingRequests: pool.waitingCount,
      poolSize: pool.totalCount,
      maxSize: dbConfig.max,
    };
  }

  static async optimizePool(): Promise<{ optimized: boolean; changes: string[] }> {
    const changes: string[] = [];
    
    // If waiting requests are high, suggest pool expansion
    const stats = await this.getStats();
    if (stats.waitingRequests > 5) {
      changes.push(`Increase pool size from ${dbConfig.max} to ${Math.min(dbConfig.max * 1.5, 50)}`);
    }
    
    // If idle connections are high, suggest reduction
    if (stats.idleConnections > dbConfig.max * 0.7) {
      changes.push('Reduce idle timeout to close unused connections faster');
    }
    
    return {
      optimized: changes.length > 0,
      changes,
    };
  }
}

// Load Balancer
class QueryLoadBalancer {
  static makeDecision(query: string, poolStats: PoolStats): LoadBalanceDecision {
    const complexity = QueryAnalyzer.calculateComplexity(query);
    const severity = QueryAnalyzer.categorizeSeverity(complexity);
    
    let routeToNode = 'primary';
    let reason = 'Route to primary database';
    let estimatedTime = complexity * 2;
    
    // High complexity queries route to read replica
    if (severity === 'critical' && poolStats.activeConnections > poolStats.maxSize * 0.7) {
      routeToNode = 'replica';
      reason = 'Route to read replica (high complexity + high load)';
      estimatedTime = complexity * 1.5;
    }
    
    // Queue if pool is saturated
    if (poolStats.waitingRequests > 10) {
      routeToNode = 'queue';
      reason = 'Queue query (pool saturated)';
      estimatedTime = complexity * 5;
    }
    
    return {
      routeToNode,
      reason,
      complexity,
      estimatedTime,
    };
  }
}

// Routes

/**
 * POST /api/query/analyze
 * Analyze query complexity and get routing recommendation
 */
app.post('/api/query/analyze', async (req: Request, res: Response) => {
  try {
    const { query } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query required' });
    }
    
    const complexity = QueryAnalyzer.calculateComplexity(query);
    const severity = QueryAnalyzer.categorizeSeverity(complexity);
    const poolStats = await PoolManager.getStats();
    const decision = QueryLoadBalancer.makeDecision(query, poolStats);
    
    metrics.queriesAnalyzed++;
    if (severity === 'slow' || severity === 'critical') {
      metrics.slowQueriesDetected++;
    }
    
    res.json({
      query: query.substring(0, 100) + (query.length > 100 ? '...' : ''),
      complexity,
      severity,
      poolStats,
      decision,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

/**
 * GET /api/pool/stats
 * Get current connection pool statistics
 */
app.get('/api/pool/stats', async (req: Request, res: Response) => {
  try {
    const stats = await PoolManager.getStats();
    
    res.json({
      timestamp: new Date().toISOString(),
      poolStats: stats,
      configuration: {
        maxConnections: dbConfig.max,
        minConnections: dbConfig.min,
        idleTimeoutMs: dbConfig.idleTimeoutMillis,
        connectionTimeoutMs: dbConfig.connectionTimeoutMillis,
        statementTimeoutMs: dbConfig.statement_timeout,
      },
    });
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

/**
 * POST /api/pool/optimize
 * Suggest pool optimizations
 */
app.post('/api/pool/optimize', async (req: Request, res: Response) => {
  try {
    const optimization = await PoolManager.optimizePool();
    
    res.json({
      timestamp: new Date().toISOString(),
      ...optimization,
      recommendations: [
        `Max connections: ${dbConfig.max}`,
        `Idle timeout: ${dbConfig.idleTimeoutMillis}ms`,
        `Connection timeout: ${dbConfig.connectionTimeoutMillis}ms`,
        `Statement timeout: ${dbConfig.statement_timeout}ms`,
      ],
    });
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

/**
 * POST /api/query/execute
 * Execute query with pooling and monitoring
 */
app.post('/api/query/execute', async (req: Request, res: Response) => {
  let client: PoolClient | null = null;
  
  try {
    const { query, timeout = 30000 } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query required' });
    }
    
    // Get client from pool
    const startAcquisition = Date.now();
    client = await pool.connect();
    const acquisitionTime = Date.now() - startAcquisition;
    
    // Execute query with timeout
    const startExecution = Date.now();
    const result = await Promise.race([
      client.query(query),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Query timeout')), timeout)
      ),
    ]);
    const executionTime = Date.now() - startExecution;
    
    metrics.requestsProcessed++;
    
    res.json({
      success: true,
      query: query.substring(0, 50) + '...',
      rowsAffected: result.rowCount,
      executionTimeMs: executionTime,
      acquisitionTimeMs: acquisitionTime,
      complexity: QueryAnalyzer.calculateComplexity(query),
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({
      error: String(error),
      timestamp: new Date().toISOString(),
    });
  } finally {
    if (client) {
      client.release();
    }
  }
});

/**
 * GET /api/slow-queries
 * Get recommendations for slow queries
 */
app.get('/api/slow-queries', async (req: Request, res: Response) => {
  try {
    const client = await pool.connect();
    
    try {
      const result = await client.query(`
        SELECT 
          query,
          calls,
          mean_time,
          max_time,
          total_time
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat_statements%'
        ORDER BY mean_time DESC
        LIMIT 10;
      `);
      
        const slowQueries = result.rows.map((row: {
            query: string;
            calls: number;
            mean_time: string | number;
            max_time: string | number;
            total_time: string | number;
        }) => ({
        query: row.query.substring(0, 100),
        calls: row.calls,
          meanTimeMs: parseFloat(row.mean_time as string).toFixed(2),
          maxTimeMs: parseFloat(row.max_time as string).toFixed(2),
          totalTimeMs: parseFloat(row.total_time as string).toFixed(2),
        complexity: QueryAnalyzer.calculateComplexity(row.query),
      }));
      
      res.json({
        timestamp: new Date().toISOString(),
        slowQueryCount: slowQueries.length,
        queries: slowQueries,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', async (req: Request, res: Response) => {
  try {
    const poolStats = await PoolManager.getStats();
    
    res.json({
      status: 'healthy',
      service: 'balancer-ts-3338',
      timestamp: new Date().toISOString(),
      poolStats,
      metrics: {
        requestsProcessed: metrics.requestsProcessed,
        queriesAnalyzed: metrics.queriesAnalyzed,
        slowQueriesDetected: metrics.slowQueriesDetected,
        uptimeMs: Date.now() - metrics.startTime.getTime(),
      },
    });
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: String(error) });
  }
});

/**
 * GET /info
 * Service information
 */
app.get('/info', (req: Request, res: Response) => {
  res.json({
    service: 'Balancer (TypeScript)',
    port: PORT,
    type: 'query-load-balancer',
    version: '1.0.0',
    startedAt: metrics.startTime.toISOString(),
    timestamp: new Date().toISOString(),
    features: [
      'Query complexity analysis',
      'Connection pooling optimization',
      'Load balancing decisions',
      'Slow query detection',
      'Pool statistics monitoring',
    ],
    endpoints: {
      'POST /api/query/analyze': 'Analyze query and get routing decision',
      'GET /api/pool/stats': 'Get connection pool statistics',
      'POST /api/pool/optimize': 'Get pool optimization suggestions',
      'POST /api/query/execute': 'Execute query with pooling',
      'GET /api/slow-queries': 'Get slow queries from pg_stat_statements',
      'GET /health': 'Health check',
      'GET /info': 'Service information',
    },
  });
});

// Error handling
app.use((err: any, req: Request, res: Response) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const server = http.createServer(app);

server.listen(PORT, HOST, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  BALANCER SERVICE (TypeScript)`);
  console.log(`  Listening on ${HOST}:${PORT}`);
  console.log(`  Query load balancing & connection pooling`);
  console.log(`${'='.repeat(60)}\n`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('\n⏹️ Shutting down gracefully...');
  server.close(async () => {
    await pool.end();
    process.exit(0);
  });
});

export { app, QueryAnalyzer, PoolManager, QueryLoadBalancer };
