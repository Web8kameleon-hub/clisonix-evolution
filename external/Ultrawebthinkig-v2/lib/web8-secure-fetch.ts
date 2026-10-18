/**
 * Web8 Secure Fetch - Proactive Polling Architecture
 * Pure TypeScript + AGI Control + Signature Verification
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Web8
 */

import * as crypto from 'crypto';

// Web8 Types - Proactive Polling Configuration
export interface Web8SecureFetchConfig {
  readonly endpoint: string;
  readonly interval: number;
  readonly web8AuthToken: string;
  readonly apiKey: string;
  readonly maxRetries: number;
  readonly timeout: number;
  readonly validator?: (data: unknown) => boolean;
  readonly agiControlled: boolean;
}

export interface Web8FetchResult<T = unknown> {
  readonly success: boolean;
  readonly data?: T;
  readonly signature: string;
  readonly timestamp: number;
  readonly verified: boolean;
  readonly error?: string;
}

// Web8 Signature Generation
function generateWeb8Signature(
  data: string,
  secret: string,
  timestamp: number
): string {
  const payload = `${timestamp}.${data}`;
  return crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
}

// Web8 Signature Verification
function verifyWeb8Signature(
  data: string,
  signature: string,
  secret: string,
  timestamp: number,
  tolerance: number = 300000 // 5 minutes
): boolean {
  const now = Date.now();
  
  // Check timestamp tolerance
  if (Math.abs(now - timestamp) > tolerance) {
    return false;
  }
  
  const expectedSignature = generateWeb8Signature(data, secret, timestamp);
  
  // Use timing-safe comparison
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}

// Web8 Secure Fetch Function
async function web8SecureFetch<T = unknown>(
  config: Web8SecureFetchConfig
): Promise<Web8FetchResult<T>> {
  const timestamp = Date.now();
  const requestId = crypto.randomUUID();
  
  try {
    // Generate request signature
    const requestData = JSON.stringify({ requestId, timestamp });
    const signature = generateWeb8Signature(requestData, config.web8AuthToken, timestamp);
    
    const headers = {
      'Content-Type': 'application/json',
      'X-Web8-Timestamp': timestamp.toString(),
      'X-Web8-Signature': `v1=${signature}`,
      'X-Web8-Request-ID': requestId,
      'Authorization': `Bearer ${config.apiKey}`,
      'User-Agent': 'Web8-SecureFetch/8.0.0'
    };
    
    const response = await fetch(config.endpoint, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(config.timeout)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const responseData = await response.text();
    const responseTimestamp = parseInt(response.headers.get('X-Web8-Timestamp') || '0');
    const responseSignature = response.headers.get('X-Web8-Signature')?.replace('v1=', '') || '';
    
    // Verify response signature
    const verified = verifyWeb8Signature(
      responseData,
      responseSignature,
      config.web8AuthToken,
      responseTimestamp
    );
    
    if (!verified) {
      throw new Error('Web8 signature verification failed');
    }
    
    const parsedData = JSON.parse(responseData);
    
    // Optional custom validation
    if (config.validator && !config.validator(parsedData)) {
      throw new Error('Web8 custom validation failed');
    }
    
    return {
      success: true,
      data: parsedData,
      signature: responseSignature,
      timestamp: responseTimestamp,
      verified: true
    };
    
  } catch (error) {
    return {
      success: false,
      signature: '',
      timestamp,
      verified: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

// Web8 Polling Scheduler
class Web8Scheduler {
  private intervals = new Map<string, NodeJS.Timeout>();
  private configs = new Map<string, Web8SecureFetchConfig>();
  private results = new Map<string, Web8FetchResult>();
  
  // Start polling for an endpoint
  startPolling(id: string, config: Web8SecureFetchConfig): void {
    // Stop existing polling if any
    this.stopPolling(id);
    
    this.configs.set(id, config);
    
    const poll = async () => {
      console.log(`🔄 Web8 Polling: ${config.endpoint}`);
      const result = await web8SecureFetch(config);
      
      this.results.set(id, result);
      
      if (result.success) {
        console.log(`✅ Web8 Fetch Success: ${id}`);
        // Process data if needed
        if (config.agiControlled) {
          // AGI can decide what to do with this data
          console.log('🧠 AGI Processing:', result.data);
        }
      } else {
        console.error(`❌ Web8 Fetch Failed: ${id}`, result.error);
      }
    };
    
    // Initial poll
    poll();
    
    // Schedule recurring polls
    const interval = setInterval(poll, config.interval);
    this.intervals.set(id, interval);
    
    console.log(`🚀 Web8 Polling started: ${id} (interval: ${config.interval}ms)`);
  }
  
  // Stop polling for an endpoint
  stopPolling(id: string): void {
    const interval = this.intervals.get(id);
    if (interval) {
      clearInterval(interval);
      this.intervals.delete(id);
      console.log(`⏹️ Web8 Polling stopped: ${id}`);
    }
  }
  
  // Get last result
  getLastResult(id: string): Web8FetchResult | undefined {
    return this.results.get(id);
  }
  
  // Stop all polling
  stopAll(): void {
    for (const id of this.intervals.keys()) {
      this.stopPolling(id);
    }
  }
}

// Web8 Global Scheduler Instance
export const web8Scheduler = new Web8Scheduler();

// Web8 Quick Setup Functions
export function pollGitHubUpdates() {
  web8Scheduler.startPolling('github', {
    endpoint: 'https://api.github.com/repos/owner/repo/releases/latest',
    interval: 300000, // 5 minutes
    web8AuthToken: process.env.GITHUB_TOKEN || '',
    apiKey: process.env.GITHUB_TOKEN || '',
    maxRetries: 3,
    timeout: 10000,
    agiControlled: true
  });
}

export function pollSlackUpdates() {
  web8Scheduler.startPolling('slack', {
    endpoint: 'https://slack.com/api/conversations.history',
    interval: 60000, // 1 minute
    web8AuthToken: process.env.SLACK_BOT_TOKEN || '',
    apiKey: process.env.SLACK_BOT_TOKEN || '',
    maxRetries: 3,
    timeout: 5000,
    agiControlled: true
  });
}

// Web8 Dynamic Exports
export {
  web8SecureFetch,
  generateWeb8Signature,
  verifyWeb8Signature,
  Web8Scheduler
};

export type {
  Web8SecureFetchConfig,
  Web8FetchResult
};
