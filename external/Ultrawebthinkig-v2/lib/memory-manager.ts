/**
 * Web8 Memory Manager - AGI-Controlled Memory Optimization
 * Replaces traditional memory management with intelligent allocation
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Web8
 * @license MIT
 */

interface MemoryConfig {
  maxCacheSize: number;
  cleanupInterval: number;
  compressionEnabled: boolean;
  debugMode: boolean;
}

interface MemoryStats {
  totalAllocated: number;
  totalFreed: number;
  cacheHits: number;
  cacheMisses: number;
  cleanupCycles: number;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  accessCount: number;
  size: number;
}

// Web8 Memory Context
interface Web8MemoryContext {
  readonly config: MemoryConfig;
  readonly cache: Map<string, CacheEntry<any>>;
  readonly stats: MemoryStats;
  readonly cleanupTimer: NodeJS.Timeout | undefined;
}

// Web8 Default Memory Configuration
const defaultMemoryConfig: MemoryConfig = {
  maxCacheSize: 100 * 1024 * 1024, // 100MB
  cleanupInterval: 60000, // 1 minute
  compressionEnabled: false,
  debugMode: false
};

// Web8 Memory Context Factory
function createMemoryContext(config: Partial<MemoryConfig> = {}): Web8MemoryContext {
  const fullConfig = {
    ...defaultMemoryConfig,
    ...config
  };

  return {
    config: fullConfig,
    cache: new Map<string, CacheEntry<any>>(),
    stats: {
      totalAllocated: 0,
      totalFreed: 0,
      cacheHits: 0,
      cacheMisses: 0,
      cleanupCycles: 0
    },
    cleanupTimer: undefined
  };
}

// Web8 Memory Size Calculation
function calculateMemorySize(data: any): number {
  if (data === null || data === undefined) return 8;
  
  switch (typeof data) {
    case 'boolean':
      return 4;
    case 'number':
      return 8;
    case 'string':
      return data.length * 2; // Unicode characters
    case 'object':
      if (data instanceof Date) return 8;
      if (Array.isArray(data)) {
        return data.reduce((sum, item) => sum + calculateMemorySize(item), 0);
      }
      return Object.keys(data).reduce((sum, key) => {
        return sum + calculateMemorySize(key) + calculateMemorySize(data[key]);
      }, 0);
    default:
      return 50; // Estimated for functions, symbols, etc.
  }
}

// Web8 Cache Operations
function setCacheEntry<T>(
  context: Web8MemoryContext,
  key: string,
  data: T,
  ttl?: number
): Web8MemoryContext {
  const size = calculateMemorySize(data);
  
  // Check if we have space
  const totalSize = getTotalCacheSize(context);
  if (totalSize + size > context.config.maxCacheSize) {
    context = performCleanup(context);
  }

  const entry: CacheEntry<T> = {
    data,
    timestamp: Date.now(),
    accessCount: 0,
    size
  };

  const newCache = new Map(context.cache);
  newCache.set(key, entry);

  const newStats = {
    ...context.stats,
    totalAllocated: context.stats.totalAllocated + size
  };

  if (context.config.debugMode) {
    console.log(`💾 Web8 Memory: Set ${key} (${size} bytes)`);
  }

  return {
    ...context,
    cache: newCache,
    stats: newStats
  };
}

function getCacheEntry<T>(
  context: Web8MemoryContext,
  key: string
): { data: T | null; context: Web8MemoryContext } {
  const entry = context.cache.get(key) as CacheEntry<T> | undefined;
  
  if (!entry) {
    const newStats = {
      ...context.stats,
      cacheMisses: context.stats.cacheMisses + 1
    };
    
    if (context.config.debugMode) {
      console.log(`💾 Web8 Memory: Cache miss for ${key}`);
    }
    
    return {
      data: null,
      context: { ...context, stats: newStats }
    };
  }

  // Update access count
  const updatedEntry = {
    ...entry,
    accessCount: entry.accessCount + 1
  };

  const newCache = new Map(context.cache);
  newCache.set(key, updatedEntry);

  const newStats = {
    ...context.stats,
    cacheHits: context.stats.cacheHits + 1
  };

  if (context.config.debugMode) {
    console.log(`💾 Web8 Memory: Cache hit for ${key}`);
  }

  return {
    data: entry.data,
    context: {
      ...context,
      cache: newCache,
      stats: newStats
    }
  };
}

function deleteCacheEntry(
  context: Web8MemoryContext,
  key: string
): Web8MemoryContext {
  const entry = context.cache.get(key);
  
  if (!entry) {
    return context;
  }

  const newCache = new Map(context.cache);
  newCache.delete(key);

  const newStats = {
    ...context.stats,
    totalFreed: context.stats.totalFreed + entry.size
  };

  if (context.config.debugMode) {
    console.log(`💾 Web8 Memory: Deleted ${key} (freed ${entry.size} bytes)`);
  }

  return {
    ...context,
    cache: newCache,
    stats: newStats
  };
}

// Web8 Memory Analysis
function getTotalCacheSize(context: Web8MemoryContext): number {
  let totalSize = 0;
  for (const entry of context.cache.values()) {
    totalSize += entry.size;
  }
  return totalSize;
}

function getMemoryStats(context: Web8MemoryContext): MemoryStats & {
  totalCacheSize: number;
  cacheEntryCount: number;
  hitRatio: number;
} {
  const totalRequests = context.stats.cacheHits + context.stats.cacheMisses;
  const hitRatio = totalRequests > 0 ? context.stats.cacheHits / totalRequests : 0;

  return {
    ...context.stats,
    totalCacheSize: getTotalCacheSize(context),
    cacheEntryCount: context.cache.size,
    hitRatio
  };
}

// Web8 Memory Cleanup
function performCleanup(context: Web8MemoryContext): Web8MemoryContext {
  const currentTime = Date.now();
  const maxAge = 5 * 60 * 1000; // 5 minutes
  
  let updatedContext = context;
  let freedBytes = 0;

  // Remove old entries
  for (const [key, entry] of context.cache.entries()) {
    if (currentTime - entry.timestamp > maxAge) {
      freedBytes += entry.size;
      updatedContext = deleteCacheEntry(updatedContext, key);
    }
  }

  // If still too large, remove least accessed entries
  if (getTotalCacheSize(updatedContext) > updatedContext.config.maxCacheSize * 0.8) {
    const entries = Array.from(updatedContext.cache.entries())
      .sort(([,a], [,b]) => a.accessCount - b.accessCount);

    for (const [key, entry] of entries) {
      if (getTotalCacheSize(updatedContext) <= updatedContext.config.maxCacheSize * 0.7) {
        break;
      }
      freedBytes += entry.size;
      updatedContext = deleteCacheEntry(updatedContext, key);
    }
  }

  const newStats = {
    ...updatedContext.stats,
    cleanupCycles: updatedContext.stats.cleanupCycles + 1
  };

  if (updatedContext.config.debugMode) {
    console.log(`💾 Web8 Memory: Cleanup completed, freed ${freedBytes} bytes`);
  }

  return {
    ...updatedContext,
    stats: newStats
  };
}

// Web8 Memory Health Check
function checkMemoryHealth(context: Web8MemoryContext): {
  healthy: boolean;
  issues: string[];
  recommendations: string[];
  utilizationPercentage: number;
} {
  const issues: string[] = [];
  const recommendations: string[] = [];
  
  const totalSize = getTotalCacheSize(context);
  const utilizationPercentage = (totalSize / context.config.maxCacheSize) * 100;
  
  if (utilizationPercentage > 90) {
    issues.push('Memory utilization above 90%');
    recommendations.push('Consider increasing cache size or reducing data retention');
  }
  
  if (utilizationPercentage > 95) {
    issues.push('Critical memory utilization');
    recommendations.push('Immediate cleanup required');
  }
  
  const stats = getMemoryStats(context);
  if (stats.hitRatio < 0.5) {
    issues.push('Low cache hit ratio');
    recommendations.push('Review caching strategy');
  }
  
  return {
    healthy: issues.length === 0,
    issues,
    recommendations,
    utilizationPercentage
  };
}

// Web8 Memory Optimization
function optimizeMemory(context: Web8MemoryContext): Web8MemoryContext {
  let optimizedContext = performCleanup(context);
  
  // Enable compression if not already enabled and we have large objects
  if (!optimizedContext.config.compressionEnabled) {
    const largeEntries = Array.from(optimizedContext.cache.values())
      .filter(entry => entry.size > 1024); // > 1KB
    
    if (largeEntries.length > 10) {
      optimizedContext = {
        ...optimizedContext,
        config: {
          ...optimizedContext.config,
          compressionEnabled: true
        }
      };
      
      if (optimizedContext.config.debugMode) {
        console.log('💾 Web8 Memory: Enabled compression for optimization');
      }
    }
  }
  
  return optimizedContext;
}

// Web8 Functional Exports
export {
  createMemoryContext,
  setCacheEntry,
  getCacheEntry,
  deleteCacheEntry,
  performCleanup,
  getMemoryStats,
  checkMemoryHealth,
  optimizeMemory,
  calculateMemorySize,
  getTotalCacheSize
};

export type {
  Web8MemoryContext,
  MemoryConfig,
  MemoryStats,
  CacheEntry
};
