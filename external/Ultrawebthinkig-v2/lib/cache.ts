/**
 * Real Redis Cache Service
 * NO MOCK DATA - Production Ready
 */

import Redis from 'ioredis';

export class CacheService {
  private redis: Redis;
  private static instance: CacheService;
  private unavailableUntil: number = 0;
  private lastConnectionLogAt: number = 0;
  private readonly isDisabled: boolean;

  private constructor() {
    this.isDisabled = process.env.CACHE_ENABLED === 'false';

    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379', {
      retryStrategy: (times) => {
        if (times > 1 && process.env.NODE_ENV !== 'production') {
          return null;
        }
        const delay = Math.min(times * 50, 500);
        return delay;
      },
      maxRetriesPerRequest: process.env.NODE_ENV === 'production' ? 3 : 1,
      enableOfflineQueue: process.env.NODE_ENV === 'production',
    });

    this.redis.on('error', (err) => {
      const message = err instanceof Error ? err.message : String(err);
      const isConnRefused = message.includes('ECONNREFUSED');
      if (isConnRefused) {
        this.unavailableUntil = Date.now() + 15000;
      }

      const now = Date.now();
      const canLogConnectionWarning = now - this.lastConnectionLogAt > 15000;

      if (!isConnRefused || process.env.NODE_ENV === 'production') {
        console.error('Redis Client Error', err);
      } else if (canLogConnectionWarning) {
        this.lastConnectionLogAt = now;
        console.warn('⚠️ Redis unavailable in dev mode (ECONNREFUSED). Cache fallback enabled.');
      }
    });

    this.redis.on('connect', () => {
      console.log('✅ Redis connected');
    });
  }

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  private shouldBypassCache(): boolean {
    if (this.isDisabled) {
      return true;
    }
    return Date.now() < this.unavailableUntil;
  }

  async get<T>(key: string): Promise<T | null> {
    if (this.shouldBypassCache()) {
      return null;
    }
    try {
      const value = await this.redis.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error(`Cache get error for key ${key}:`, error);
      return null;
    }
  }

  async set(key: string, value: any, ttlSeconds?: number): Promise<boolean> {
    if (this.shouldBypassCache()) {
      return false;
    }
    try {
      const serialized = JSON.stringify(value);
      if (ttlSeconds) {
        await this.redis.setex(key, ttlSeconds, serialized);
      } else {
        await this.redis.set(key, serialized);
      }
      return true;
    } catch (error) {
      console.error(`Cache set error for key ${key}:`, error);
      return false;
    }
  }

  async del(key: string): Promise<boolean> {
    if (this.shouldBypassCache()) {
      return false;
    }
    try {
      await this.redis.del(key);
      return true;
    } catch (error) {
      console.error(`Cache delete error for key ${key}:`, error);
      return false;
    }
  }

  async exists(key: string): Promise<boolean> {
    if (this.shouldBypassCache()) {
      return false;
    }
    try {
      const result = await this.redis.exists(key);
      return result === 1;
    } catch (error) {
      console.error(`Cache exists error for key ${key}:`, error);
      return false;
    }
  }

  async keys(pattern: string): Promise<string[]> {
    if (this.shouldBypassCache()) {
      return [];
    }
    try {
      return await this.redis.keys(pattern);
    } catch (error) {
      console.error(`Cache keys error for pattern ${pattern}:`, error);
      return [];
    }
  }

  async flushAll(): Promise<boolean> {
    if (this.shouldBypassCache()) {
      return false;
    }
    try {
      await this.redis.flushall();
      return true;
    } catch (error) {
      console.error('Cache flush error:', error);
      return false;
    }
  }

  async healthCheck(): Promise<boolean> {
    if (this.shouldBypassCache()) {
      return false;
    }
    try {
      const pong = await this.redis.ping();
      return pong === 'PONG';
    } catch (error) {
      console.error('Redis health check failed:', error);
      return false;
    }
  }

  async disconnect(): Promise<void> {
    await this.redis.quit();
  }
}

export const cache = CacheService.getInstance();
