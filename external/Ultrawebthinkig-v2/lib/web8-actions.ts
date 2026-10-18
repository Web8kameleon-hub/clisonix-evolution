/**
 * Web8 Actions - Pure API Functions (NO Server Actions)
 * Replaces Next.js "use server" with Web8 functional architecture
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Web8
 */

import * as React from 'react';

// Web8 Types - Pure interfaces
interface Web8FormData {
  readonly action: string;
  readonly payload: Record<string, unknown>;
  readonly timestamp: number;
  readonly agentId?: string;
}

interface Web8Response<T = unknown> {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: string;
  readonly timestamp: number;
  readonly processingTime: number;
}

interface Web8Config {
  readonly endpoint: string;
  readonly timeout: number;
  readonly retries: number;
  readonly headers: Record<string, string>;
}

// Web8 Default Configuration
function createWeb8Config(overrides: Partial<Web8Config> = {}): Web8Config {
  return {
    endpoint: '/api/web8',
    timeout: 5000,
    retries: 3,
    headers: {
      'Content-Type': 'application/json',
      'X-Web8-Client': 'true',
      'X-Web8-Version': '8.0.0'
    },
    ...overrides
  } as const;
}

// Web8 Core API Function (Replaces Server Actions)
async function web8ApiCall<T = unknown>(
  action: string,
  payload: Record<string, unknown> = {},
  config: Partial<Web8Config> = {}
): Promise<Web8Response<T>> {
  const startTime = Date.now();
  const fullConfig = createWeb8Config(config);
  
  const requestData: Web8FormData = {
    action,
    payload,
    timestamp: startTime,
    agentId: crypto.randomUUID?.() || Math.random().toString(36)
  };
  
  try {
    const response = await fetch(`${fullConfig.endpoint}/${action}`, {
      method: 'POST',
      headers: fullConfig.headers,
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(fullConfig.timeout)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    return {
      success: true,
      data,
      timestamp: Date.now(),
      processingTime: Date.now() - startTime
    };
    
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now(),
      processingTime: Date.now() - startTime
    };
  }
}

// Web8 Specific Actions (Replaces all Server Actions)

/**
 * Save form data - Replaces "use server" form actions
 */
async function saveFormData(formData: Record<string, unknown>) {
  return web8ApiCall('save', formData);
}

/**
 * Load configuration - Replaces server-side data fetching
 */
async function loadConfig(configType: string) {
  return web8ApiCall('config/load', { type: configType });
}

/**
 * AGI Request - Replaces server-side AI processing
 */
async function askAGI(prompt: string, context?: Record<string, unknown>) {
  return web8ApiCall('agi/ask', { prompt, context });
}

/**
 * Handle form submission with Web8 pattern
 */
async function handleFormSubmit(
  event: Event,
  action: string,
  onSuccess?: (data: unknown) => void,
  onError?: (error: string) => void
) {
  event.preventDefault();
  
  const form = event.target as HTMLFormElement;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());
  
  const response = await web8ApiCall(action, data);
  
  if (response.success) {
    onSuccess?.(response.data);
  } else {
    onError?.(response.error || 'Unknown error');
  }
}

/**
 * Web8 React Hook Pattern (Replaces useFormStatus, etc.)
 */
function useWeb8Action<T = unknown>(action: string) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [data, setData] = React.useState<T | null>(null);
  
  const execute = React.useCallback(async (payload: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    
    const response = await web8ApiCall<T>(action, payload);
    
    if (response.success) {
      setData(response.data || null);
    } else {
      setError(response.error || 'Unknown error');
    }
    
    setLoading(false);
    return response;
  }, [action]);
  
  return { execute, loading, error, data };
}

// Web8 Dynamic Exports - NO Server Actions, Pure Functions
export {
  web8ApiCall,
  createWeb8Config,
  saveFormData,
  loadConfig,
  askAGI,
  handleFormSubmit,
  useWeb8Action
};

export type {
  Web8FormData,
  Web8Response,
  Web8Config
};
