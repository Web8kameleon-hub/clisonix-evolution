/**
 * Web8 Performance Testing Suite
 * Replaces Artillery with Pure TypeScript Load Testing
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Web8
 */

import { web8ApiCall } from '../../lib/web8-actions';

export interface LoadTestConfig {
  readonly concurrent: number;
  readonly duration: number;
  readonly endpoint: string;
  readonly payloadSize: number;
  readonly rampUpTime: number;
}

export interface LoadTestResult {
  readonly totalRequests: number;
  readonly successfulRequests: number;
  readonly failedRequests: number;
  readonly averageResponseTime: number;
  readonly minResponseTime: number;
  readonly maxResponseTime: number;
  readonly requestsPerSecond: number;
  readonly successRate: number;
}

// Web8 Load Test Configuration
const defaultConfig: LoadTestConfig = {
  concurrent: 50,
  duration: 30000, // 30 seconds
  endpoint: '/api/web8/health',
  payloadSize: 1024,
  rampUpTime: 5000 // 5 seconds
};

// Web8 Pure Load Testing Function
async function runWeb8LoadTest(
  config: Partial<LoadTestConfig> = {}
): Promise<LoadTestResult> {
  const fullConfig = { ...defaultConfig, ...config };
  const results: Array<{ success: boolean; responseTime: number; timestamp: number }> = [];
  const startTime = Date.now();
  
  console.log(`🚀 Starting Web8 Load Test: ${fullConfig.concurrent} concurrent users`);
  
  // Ramp up phase
  const rampUpInterval = fullConfig.rampUpTime / fullConfig.concurrent;
  const workers: Promise<void>[] = [];
  
  for (let i = 0; i < fullConfig.concurrent; i++) {
    const delay = i * rampUpInterval;
    
    const worker = new Promise<void>((resolve) => {
      setTimeout(async () => {
        const endTime = Date.now() + fullConfig.duration;
        
        while (Date.now() < endTime) {
          const requestStart = Date.now();
          
          try {
            const response = await web8ApiCall('health-check', {
              payload: 'x'.repeat(fullConfig.payloadSize),
              timestamp: Date.now(),
              workerId: i
            });
            
            results.push({
              success: response.success,
              responseTime: Date.now() - requestStart,
              timestamp: Date.now()
            });
            
          } catch (error) {
            results.push({
              success: false,
              responseTime: Date.now() - requestStart,
              timestamp: Date.now()
            });
          }
          
          // Small delay between requests
          await new Promise(resolve => setTimeout(resolve, 10));
        }
        
        resolve();
      }, delay);
    });
    
    workers.push(worker);
  }
  
  // Wait for all workers to complete
  await Promise.all(workers);
  
  const totalTime = Date.now() - startTime;
  const responseTimes = results.map(r => r.responseTime);
  
  const result: LoadTestResult = {
    totalRequests: results.length,
    successfulRequests: results.filter(r => r.success).length,
    failedRequests: results.filter(r => !r.success).length,
    averageResponseTime: responseTimes.reduce((sum, rt) => sum + rt, 0) / responseTimes.length,
    minResponseTime: Math.min(...responseTimes),
    maxResponseTime: Math.max(...responseTimes),
    requestsPerSecond: (results.length / totalTime) * 1000,
    successRate: results.filter(r => r.success).length / results.length
  };
  
  console.log('📊 Web8 Load Test Results:');
  console.log(`   Total Requests: ${result.totalRequests}`);
  console.log(`   Success Rate: ${(result.successRate * 100).toFixed(2)}%`);
  console.log(`   Avg Response Time: ${result.averageResponseTime.toFixed(2)}ms`);
  console.log(`   Requests/sec: ${result.requestsPerSecond.toFixed(2)}`);
  
  return result;
}

// Web8 Stress Testing Function
async function runWeb8StressTest(): Promise<LoadTestResult> {
  console.log('🔥 Starting Web8 Stress Test...');
  
  return runWeb8LoadTest({
    concurrent: 200,
    duration: 60000, // 1 minute
    payloadSize: 5120, // 5KB
    rampUpTime: 10000 // 10 seconds
  });
}

// Web8 Endurance Testing Function
async function runWeb8EnduranceTest(): Promise<LoadTestResult> {
  console.log('⏰ Starting Web8 Endurance Test...');
  
  return runWeb8LoadTest({
    concurrent: 25,
    duration: 300000, // 5 minutes
    payloadSize: 2048, // 2KB
    rampUpTime: 15000 // 15 seconds
  });
}

// Web8 Performance Validation
function validateWeb8Performance(result: LoadTestResult): boolean {
  const thresholds = {
    minSuccessRate: 0.95, // 95%
    maxAverageResponseTime: 500, // 500ms
    minRequestsPerSecond: 50
  };
  
  const isValid = (
    result.successRate >= thresholds.minSuccessRate &&
    result.averageResponseTime <= thresholds.maxAverageResponseTime &&
    result.requestsPerSecond >= thresholds.minRequestsPerSecond
  );
  
  if (!isValid) {
    console.error('❌ Web8 Performance thresholds not met:');
    console.error(`   Success Rate: ${(result.successRate * 100).toFixed(2)}% (min: ${thresholds.minSuccessRate * 100}%)`);
    console.error(`   Avg Response: ${result.averageResponseTime.toFixed(2)}ms (max: ${thresholds.maxAverageResponseTime}ms)`);
    console.error(`   Requests/sec: ${result.requestsPerSecond.toFixed(2)} (min: ${thresholds.minRequestsPerSecond})`);
  } else {
    console.log('✅ Web8 Performance validation passed!');
  }
  
  return isValid;
}

// CLI Runner
if (import.meta.url === `file://${process.argv[1]}`) {
  const testType = process.argv[2] || 'load';
  
  switch (testType) {
    case 'stress':
      runWeb8StressTest().then(validateWeb8Performance);
      break;
    case 'endurance':
      runWeb8EnduranceTest().then(validateWeb8Performance);
      break;
    default:
      runWeb8LoadTest().then(validateWeb8Performance);
  }
}

// Web8 Dynamic Exports
export {
  runWeb8LoadTest,
  runWeb8StressTest,
  runWeb8EnduranceTest,
  validateWeb8Performance
};

export type {
  LoadTestConfig,
  LoadTestResult
};
