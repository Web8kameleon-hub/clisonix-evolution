/**
 * Real Database Service - PostgreSQL Integration
 * Production Ready with Connection Pooling
 * Author: Ledjan Ahmati
 * Date: March 4, 2026
 */

import { Pool, PoolClient, QueryResult, QueryResultRow } from 'pg';

interface DatabaseConfig {
  connectionString?: string;
  host?: string;
  port?: number;
  database?: string;
  user?: string;
  password?: string;
  max?: number;
  idleTimeoutMillis?: number;
  connectionTimeoutMillis?: number;
}

export class DatabaseService {
  private pool: Pool;
  private static instance: DatabaseService;
  private isConnected: boolean = false;
  private unavailableUntil: number = 0;
  private lastConnectionLogAt: number = 0;

  private constructor() {
    const config: DatabaseConfig = {
      connectionString: process.env.DATABASE_URL,
      host: process.env.POSTGRES_HOST || 'localhost',
      port: parseInt(process.env.POSTGRES_PORT || '5432'),
      database: process.env.POSTGRES_DB || 'ultrawebthinking',
      user: process.env.POSTGRES_USER || 'postgres',
      password: process.env.POSTGRES_PASSWORD,
      max: parseInt(process.env.DATABASE_POOL_MAX || '10'),
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000,
    };

    this.pool = new Pool(config);
    
    this.pool.on('connect', () => {
      this.isConnected = true;
      console.log('✅ Database connected');
    });

    this.pool.on('error', (err: Error) => {
      console.error('❌ Unexpected error on idle database client:', err);
      this.isConnected = false;
    });

    // Initialize connection
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      await this.healthCheck();
      console.log('✅ Database initialized successfully');
    } catch (error) {
      console.error('❌ Database initialization failed:', error);
    }
  }

  static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  async query<T extends QueryResultRow = QueryResultRow>(text: string, params?: unknown[]): Promise<QueryResult<T>> {
    if (Date.now() < this.unavailableUntil) {
      throw new Error('Database temporarily unavailable');
    }

    const start = Date.now();
    try {
      const res = await this.pool.query<T>(text, params);
      const duration = Date.now() - start;
      
      if (process.env.NODE_ENV !== 'production') {
        console.log('Executed query', { 
          text: text.substring(0, 100), 
          duration, 
          rows: res.rowCount 
        });
      }
      
      return res;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const isConnRefused = message.includes('ECONNREFUSED');

      if (isConnRefused) {
        this.unavailableUntil = Date.now() + 15000;
      }

      const shouldLogDetailed = !isConnRefused || process.env.NODE_ENV === 'production';
      const now = Date.now();
      const canLogConnectionWarning = now - this.lastConnectionLogAt > 15000;

      if (shouldLogDetailed) {
        console.error('Database query error:', { text, error });
      } else if (canLogConnectionWarning) {
        this.lastConnectionLogAt = now;
        console.warn('⚠️ Database unavailable in dev mode (ECONNREFUSED). Using degraded health response.');
      }

      throw error;
    }
  }


  async getClient(): Promise<PoolClient> {
    try {
      const client = await this.pool.connect();
      return client;
    } catch (error) {
      console.error('Failed to get database client:', error);
      throw new Error('Database connection unavailable');
    }
  }

  async transaction<T>(callback: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.getClient();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (e) {
      await client.query('ROLLBACK');
      console.error('Transaction rolled back:', e);
      throw e;
    } finally {
      client.release();
    }
  }

  async close(): Promise<void> {
    try {
      await this.pool.end();
      this.isConnected = false;
      console.log('✅ Database connection closed');
    } catch (error) {
      console.error('❌ Error closing database connection:', error);
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const result = await this.query('SELECT NOW() as current_time, version() as db_version');
      if (result.rows.length > 0) {
        console.log('✅ Database health check passed:', {
          time: result.rows[0].current_time,
          version: result.rows[0].db_version?.substring(0, 50)
        });
        return true;
      }
      return false;
    } catch (error) {
      console.error('❌ Database health check failed:', error);
      return false;
    }
  }

  getStatus(): { connected: boolean; poolSize: number } {
    return {
      connected: this.isConnected,
      poolSize: this.pool.totalCount
    };
  }
}

// Export singleton instance
export const db = DatabaseService.getInstance();

// Helper functions for common queries
export async function findUserByEmail(email: string) {
  const result = await db.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0] || null;
}

export async function createUser(email: string, username: string, passwordHash: string) {
  const result = await db.query(
    `INSERT INTO users (email, username, password_hash) 
     VALUES ($1, $2, $3) 
     RETURNING id, email, username, role, created_at`,
    [email, username, passwordHash]
  );
  return result.rows[0];
}

export async function createSession(userId: string, token: string, expiresAt: Date, ipAddress?: string, userAgent?: string) {
  const result = await db.query(
    `INSERT INTO sessions (user_id, token, expires_at, ip_address, user_agent) 
     VALUES ($1, $2, $3, $4, $5) 
     RETURNING id, token, expires_at`,
    [userId, token, expiresAt, ipAddress, userAgent]
  );
  return result.rows[0];
}

export async function findSessionByToken(token: string) {
  const result = await db.query(
    `SELECT s.*, u.id as user_id, u.email, u.username, u.role 
     FROM sessions s 
     JOIN users u ON s.user_id = u.id 
     WHERE s.token = $1 AND s.expires_at > NOW()`,
    [token]
  );
  return result.rows[0] || null;
}

export async function deleteSession(token: string) {
  await db.query('DELETE FROM sessions WHERE token = $1', [token]);
}

export async function cleanupExpiredSessions() {
  const result = await db.query('DELETE FROM sessions WHERE expires_at < NOW()');
  console.log(`🧹 Cleaned up ${result.rowCount} expired sessions`);
  return result.rowCount;
}
