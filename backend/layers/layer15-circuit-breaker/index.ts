/**
 * Layer 15: Circuit Breaker
 * Fault tolerance and resilience patterns
 */

import CircuitBreaker from "opossum";

// ═══════════════════════════════════════════════════════════════════════════════
// CIRCUIT BREAKER CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const defaultOptions = {
  timeout: 10000, // 10 seconds
  errorThresholdPercentage: 50, // Open circuit if 50% of requests fail
  resetTimeout: 30000, // Try again after 30 seconds
  volumeThreshold: 5, // Minimum requests before calculating error percentage
};

// ═══════════════════════════════════════════════════════════════════════════════
// CREATE CIRCUIT BREAKER
// ═══════════════════════════════════════════════════════════════════════════════

export function createCircuitBreaker<T>(
  fn: (...args: any[]) => Promise<T>,
  name: string,
  options: Partial<typeof defaultOptions> = {},
): CircuitBreaker {
  const breaker = new CircuitBreaker(fn, {
    ...defaultOptions,
    ...options,
    name,
  });

  // Event handlers
  breaker.on("success", (result: any) => {
    console.log(`[CIRCUIT:${name}] Success`);
  });

  breaker.on("timeout", () => {
    console.warn(`[CIRCUIT:${name}] Timeout`);
  });

  breaker.on("reject", () => {
    console.warn(`[CIRCUIT:${name}] Rejected (circuit open)`);
  });

  breaker.on("open", () => {
    console.error(
      `[CIRCUIT:${name}] Circuit OPENED - requests will be rejected`,
    );
  });

  breaker.on("halfOpen", () => {
    console.info(`[CIRCUIT:${name}] Circuit HALF-OPEN - testing...`);
  });

  breaker.on("close", () => {
    console.info(`[CIRCUIT:${name}] Circuit CLOSED - back to normal`);
  });

  breaker.on("fallback", (result: any) => {
    console.info(`[CIRCUIT:${name}] Fallback executed`);
  });

  return breaker;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PRE-CONFIGURED CIRCUIT BREAKERS
// ═══════════════════════════════════════════════════════════════════════════════

// For external API calls
export const externalApiBreaker = (fn: (...args: any[]) => Promise<any>) =>
  createCircuitBreaker(fn, "external-api", {
    timeout: 15000,
    errorThresholdPercentage: 60,
  });

// For database operations
export const databaseBreaker = (fn: (...args: any[]) => Promise<any>) =>
  createCircuitBreaker(fn, "database", {
    timeout: 5000,
    errorThresholdPercentage: 40,
  });

// For AI/ML operations (longer timeout)
export const aiBreaker = (fn: (...args: any[]) => Promise<any>) =>
  createCircuitBreaker(fn, "ai-service", {
    timeout: 60000, // 60 seconds for AI
    errorThresholdPercentage: 70,
  });

// For Redis operations
export const cacheBreaker = (fn: (...args: any[]) => Promise<any>) =>
  createCircuitBreaker(fn, "cache", {
    timeout: 2000,
    errorThresholdPercentage: 30,
  });

// ═══════════════════════════════════════════════════════════════════════════════
// CIRCUIT STATUS
// ═══════════════════════════════════════════════════════════════════════════════

const circuits: Map<string, CircuitBreaker> = new Map();

export const registerCircuit = (name: string, breaker: CircuitBreaker) => {
  circuits.set(name, breaker);
};

export const getCircuitStatus = () => {
  const status: Record<string, any> = {};
  circuits.forEach((breaker, name) => {
    status[name] = {
      state: breaker.opened
        ? "OPEN"
        : breaker.halfOpen
          ? "HALF-OPEN"
          : "CLOSED",
      stats: breaker.stats,
    };
  });
  return status;
};

export default {
  createCircuitBreaker,
  externalApiBreaker,
  databaseBreaker,
  aiBreaker,
  cacheBreaker,
  registerCircuit,
  getCircuitStatus,
};
