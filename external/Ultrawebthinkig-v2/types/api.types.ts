/**
 * 🌐 API TYPES - TYPE DEFINITIONS FOR API SYSTEMS
 * Type definitions për API Systems dhe Network Communications
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0-API-TYPES
 * @license MIT
 */

/**
 * 🌐 API CONFIGURATION
 */
export interface ApiConfig {
  baseUrl: string;
  version: string;
  timeout: number;
  retries: number;
  rateLimit: {
    requests: number;
    window: number;
    burst: number;
  };
  authentication: {
    type: 'none' | 'basic' | 'bearer' | 'oauth' | 'jwt' | 'api_key';
    credentials?: Record<string, string>;
    refreshThreshold?: number;
  };
  headers: Record<string, string>;
  interceptors: {
    request: boolean;
    response: boolean;
    error: boolean;
  };
  cache: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
    strategy: 'memory' | 'storage' | 'hybrid';
  };
  validation: {
    enabled: boolean;
    strict: boolean;
    schemas: Record<string, any>;
  };
}

/**
 * 📡 API REQUEST
 */
export interface ApiRequest {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
  url: string;
  path: string;
  query?: Record<string, any>;
  headers: Record<string, string>;
  body?: unknown;
  timeout?: number;
  retry?: {
    attempts: number;
    delay: number;
    backoff: 'linear' | 'exponential';
  };
  cache?: {
    enabled: boolean;
    ttl?: number;
    key?: string;
  };
  metadata: {
    timestamp: Date;
    userAgent: string;
    correlationId: string;
    traceId?: string;
    tags: string[];
  };
  validation?: {
    schema: string;
    options: unknown;
  };
}

/**
 * 📨 API RESPONSE
 */
export interface ApiResponse<T = any> {
  id: string;
  requestId: string;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: T;
  error?: ApiError;
  metadata: {
    timestamp: Date;
    duration: number;
    cached: boolean;
    retries: number;
    size: number;
  };
  pagination?: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  links?: {
    self: string;
    next?: string;
    prev?: string;
    first?: string;
    last?: string;
  };
}

/**
 * ❌ API ERROR
 */
export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
  status: number;
  timestamp: Date;
  path: string;
  method: string;
  traceId?: string;
  validation?: {
    field: string;
    message: string;
    value: unknown;
  }[];
  suggestions?: string[];
  documentation?: string;
  retryable: boolean;
}

/**
 * 🔄 API INTERCEPTOR
 */
export interface ApiInterceptor {
  name: string;
  type: 'request' | 'response' | 'error';
  priority: number;
  enabled: boolean;
  
  // Request interceptor
  onRequest?: (request: ApiRequest) => Promise<ApiRequest> | ApiRequest;
  
  // Response interceptor
  onResponse?: (response: ApiResponse) => Promise<ApiResponse> | ApiResponse;
  
  // Error interceptor
  onError?: (error: ApiError, request: ApiRequest) => Promise<ApiError> | ApiError;
  
  // Configuration
  config?: Record<string, any>;
}

/**
 * 📊 API METRICS
 */
export interface ApiMetrics {
  requests: {
    total: number;
    successful: number;
    failed: number;
    cached: number;
    retried: number;
  };
  performance: {
    averageResponseTime: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
    slowestRequest: number;
    fastestRequest: number;
  };
  errors: {
    total: number;
    byStatus: Record<string, number>;
    byEndpoint: Record<string, number>;
    rate: number;
  };
  cache: {
    hits: number;
    misses: number;
    hitRate: number;
    size: number;
    evictions: number;
  };
  rateLimit: {
    remaining: number;
    limit: number;
    resetTime: Date;
    violations: number;
  };
  endpoints: Record<string, {
    requests: number;
    errors: number;
    averageTime: number;
    lastUsed: Date;
  }>;
}

/**
 * 🔌 API ENDPOINT
 */
export interface ApiEndpoint {
  id: string;
  name: string;
  method: string;
  path: string;
  description: string;
  version: string;
  
  // Configuration
  timeout?: number;
  rateLimit?: {
    requests: number;
    window: number;
  };
  cache?: {
    enabled: boolean;
    ttl: number;
    vary: string[];
  };
  
  // Validation
  request?: {
    headers?: Record<string, any>;
    query?: Record<string, any>;
    body?: unknown;
  };
  response?: {
    schema: unknown;
    examples: unknown[];
  };
  
  // Security
  authentication: boolean;
  authorization?: string[];
  scopes?: string[];
  
  // Documentation
  tags: string[];
  deprecated: boolean;
  examples: {
    request: unknown;
    response: unknown;
  }[];
  
  // Monitoring
  enabled: boolean;
  monitoring: {
    metrics: boolean;
    logging: boolean;
    tracing: boolean;
  };
  
  // Metadata
  owner: string;
  created: Date;
  modified: Date;
  usage: {
    requests: number;
    errors: number;
    lastUsed: Date;
  };
}

/**
 * 🎯 API CLIENT
 */
export interface ApiClient {
  config: ApiConfig;
  
  // Core methods
  request<T = any>(request: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  get<T = any>(url: string, config?: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  post<T = any>(url: string, data?: unknown, config?: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  put<T = any>(url: string, data?: unknown, config?: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  patch<T = any>(url: string, data?: unknown, config?: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  delete<T = any>(url: string, config?: Partial<ApiRequest>): Promise<ApiResponse<T>>;
  
  // Configuration
  setConfig(config: Partial<ApiConfig>): void;
  getConfig(): ApiConfig;
  setBaseUrl(url: string): void;
  setHeaders(headers: Record<string, string>): void;
  
  // Interceptors
  addInterceptor(interceptor: ApiInterceptor): void;
  removeInterceptor(name: string): void;
  getInterceptors(): ApiInterceptor[];
  
  // Authentication
  setAuth(auth: unknown): void;
  refreshAuth(): Promise<void>;
  clearAuth(): void;
  
  // Cache
  clearCache(): void;
  getCacheStats(): unknown;
  
  // Metrics
  getMetrics(): ApiMetrics;
  resetMetrics(): void;
  
  // Utilities
  isOnline(): boolean;
  healthCheck(): Promise<boolean>;
  destroy(): void;
}

/**
 * 🏗️ API BUILDER
 */
export interface ApiBuilder {
  reset(): ApiBuilder;
  setBaseUrl(url: string): ApiBuilder;
  setVersion(version: string): ApiBuilder;
  setTimeout(timeout: number): ApiBuilder;
  setRetries(retries: number): ApiBuilder;
  setAuth(auth: unknown): ApiBuilder;
  setHeaders(headers: Record<string, string>): ApiBuilder;
  enableCache(config?: unknown): ApiBuilder;
  enableRateLimit(config: unknown): ApiBuilder;
  addInterceptor(interceptor: ApiInterceptor): ApiBuilder;
  addEndpoint(endpoint: ApiEndpoint): ApiBuilder;
  build(): ApiClient;
  validate(): boolean;
  getSpec(): ApiSpec;
}

/**
 * 📋 API SPECIFICATION
 */
export interface ApiSpec {
  info: {
    title: string;
    version: string;
    description: string;
    contact: {
      name: string;
      email: string;
      url: string;
    };
    license: {
      name: string;
      url: string;
    };
  };
  servers: {
    url: string;
    description: string;
    variables?: Record<string, any>;
  }[];
  endpoints: ApiEndpoint[];
  security: {
    schemes: Record<string, any>;
    requirements: unknown[];
  };
  components: {
    schemas: Record<string, any>;
    responses: Record<string, any>;
    parameters: Record<string, any>;
    examples: Record<string, any>;
  };
  tags: {
    name: string;
    description: string;
  }[];
}

/**
 * 🔍 API MONITOR
 */
export interface ApiMonitor {
  id: string;
  name: string;
  enabled: boolean;
  
  // Monitoring
  startMonitoring(): void;
  stopMonitoring(): void;
  isMonitoring(): boolean;
  
  // Metrics collection
  collectMetrics(): Promise<ApiMetrics>;
  getHistoricalMetrics(period: string): Promise<ApiMetrics[]>;
  
  // Alerts
  addAlert(alert: ApiAlert): void;
  removeAlert(id: string): void;
  getAlerts(): ApiAlert[];
  
  // Health checks
  healthCheck(): Promise<ApiHealthCheck>;
  uptime(): Promise<number>;
  
  // Reporting
  generateReport(type: string, period: string): Promise<any>;
  exportMetrics(format: 'json' | 'csv' | 'xml'): Promise<string>;
}

/**
 * 🚨 API ALERT
 */
export interface ApiAlert {
  id: string;
  name: string;
  description: string;
  type: 'threshold' | 'anomaly' | 'error_rate' | 'availability' | 'latency';
  condition: {
    metric: string;
    operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte' | 'ne';
    value: number;
    duration: number;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
  enabled: boolean;
  channels: {
    email?: string[];
    web8ProactivePolling?: boolean;
    slack?: string;
    sms?: string[];
  };
  schedule: {
    timezone: string;
    active: {
      days: string[];
      hours: string;
    };
  };
  metadata: {
    created: Date;
    modified: Date;
    triggered: number;
    lastTriggered?: Date;
  };
}

/**
 * 🏥 API HEALTH CHECK
 */
export interface ApiHealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  timestamp: Date;
  duration: number;
  checks: {
    name: string;
    status: 'pass' | 'fail' | 'warn';
    duration: number;
    message?: string;
    details?: unknown;
  }[];
  metrics: {
    uptime: number;
    responseTime: number;
    errorRate: number;
    availability: number;
  };
  dependencies: {
    name: string;
    status: 'available' | 'unavailable' | 'degraded';
    responseTime: number;
    lastChecked: Date;
  }[];
}

/**
 * 📡 WEB8 PROACTIVE POLLING
 * Web8 proactive, AGI-controlled data fetching architecture
 */
export interface Web8PollingConfig {
  readonly id: string;
  readonly name: string;
  readonly endpoint: string;
  readonly events: readonly string[];
  readonly active: boolean;
  
  // Web8 Configuration
  readonly interval: number;
  readonly validator: string;
  readonly signingKey: string;
  readonly maxRetries: number;
  readonly agiControlled: boolean;
  
  // Security (NO passive listening)
  readonly authentication: {
    readonly type: 'signed' | 'bearer' | 'api-key';
    readonly credentials: Record<string, string>;
  };
  
  // Proactive Delivery Stats
  readonly delivery: {
    readonly polls: number;
    readonly successful: number;
    readonly failed: number;
    readonly lastPoll?: Date;
    readonly lastSuccess?: Date;
    readonly nextPoll?: Date;
  };
  
  // Metadata
  readonly created: Date;
  readonly modified: Date;
  readonly owner: string;
  readonly tags: readonly string[];
}

/**
 * 📨 WEB8 SECURE FETCH DELIVERY
 * Web8 secure, verified data polling architecture
 */
export interface Web8SecureFetch {
  readonly id: string;
  readonly pollingConfigId: string;
  readonly event: {
    readonly type: string;
    readonly data: unknown;
    readonly timestamp: Date;
    readonly signature: string;
  };
  readonly request: {
    readonly endpoint: string;
    readonly method: string;
    readonly headers: Record<string, string>;
    readonly signature: string;
    readonly timestamp: Date;
  };
  readonly response?: {
    readonly status: number;
    readonly headers: Record<string, string>;
    readonly body: string;
    readonly duration: number;
    readonly timestamp: Date;
    readonly verified: boolean;
  };
  readonly status: 'pending' | 'fetched' | 'failed' | 'retrying';
  readonly attempts: number;
  readonly error?: string;
  readonly nextPoll?: Date;
}

/**
 * 🔄 API RETRY POLICY
 */
export interface ApiRetryPolicy {
  enabled: boolean;
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffStrategy: 'linear' | 'exponential' | 'constant';
  jitter: boolean;
  retryableStatuses: number[];
  retryableErrors: string[];
  onRetry?: (attempt: number, error: unknown) => void;
  shouldRetry?: (error: unknown, attempt: number) => boolean;
}

/**
 * 🎯 API EVENTS
 */
export type ApiEvent = 
  | { type: 'request_started'; data: { request: ApiRequest } }
  | { type: 'request_completed'; data: { request: ApiRequest; response: ApiResponse } }
  | { type: 'request_failed'; data: { request: ApiRequest; error: ApiError } }
  | { type: 'cache_hit'; data: { key: string; request: ApiRequest } }
  | { type: 'cache_miss'; data: { key: string; request: ApiRequest } }
  | { type: 'rate_limit_exceeded'; data: { request: ApiRequest; limit: unknown } }
  | { type: 'auth_refreshed'; data: { timestamp: Date } }
  | { type: 'auth_failed'; data: { error: string } }
  | { type: 'endpoint_added'; data: { endpoint: ApiEndpoint } }
  | { type: 'endpoint_removed'; data: { id: string } }
  | { type: 'web8_fetch_success'; data: { fetch: Web8SecureFetch } }
  | { type: 'web8_fetch_failed'; data: { fetch: Web8SecureFetch; error: string } }
  | { type: 'alert_triggered'; data: { alert: ApiAlert; value: number } }
  | { type: 'health_check_completed'; data: { result: ApiHealthCheck } };

/**
 * 📊 API ANALYTICS
 */
export interface ApiAnalytics {
  usage: {
    totalRequests: number;
    uniqueClients: number;
    requestsPerSecond: number;
    bandwidthUsage: number;
    topEndpoints: Array<{
      path: string;
      requests: number;
      percentage: number;
    }>;
  };
  performance: {
    averageResponseTime: number;
    medianResponseTime: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
    slowestEndpoints: Array<{
      path: string;
      avgTime: number;
    }>;
  };
  errors: {
    errorRate: number;
    totalErrors: number;
    errorsByStatus: Record<string, number>;
    errorsByEndpoint: Record<string, number>;
    commonErrors: Array<{
      message: string;
      count: number;
    }>;
  };
  trends: {
    requestVolume: Array<{
      timestamp: Date;
      requests: number;
    }>;
    responseTime: Array<{
      timestamp: Date;
      avg: number;
      p95: number;
    }>;
    errorRate: Array<{
      timestamp: Date;
      rate: number;
    }>;
  };
  clients: {
    topClients: Array<{
      id: string;
      requests: number;
      errors: number;
      lastSeen: Date;
    }>;
    userAgents: Record<string, number>;
    locations: Record<string, number>;
  };
}
