/**
 * Clisonix Cloud API Client
 * 37 Live Production Endpoints - NO MOCK DATA
 * 
 * @author UltraWebThinking Team
 * @version 1.0.0
 */

const CLISONIX_BASE_URL = process.env.NEXT_PUBLIC_CLISONIX_URL || 'https://clisonix.com';

export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  error?: string;
  timestamp?: string;
}

export interface SystemStatus {
  timestamp: string;
  instance_id: string;
  status: string;
  uptime: string;
  memory: {
    used: number;
    total: number;
  };
  system: {
    cpu_percent: number;
    memory_percent: number;
    memory_total: number;
    disk_percent: number;
    disk_total: number;
    processes: number;
    hostname: string;
    uptime_seconds: number;
  };
  redis: {
    status: string;
    connected_clients?: number;
    used_memory?: number;
  };
  database: {
    status: string;
    connected_clients?: number;
  };
}

export interface OceanChatResponse {
  response: string;
  model: string;
  language: string;
  tokens?: number;
  processing_time_ms?: number;
}

export interface DashboardMetrics {
  total_requests: number;
  active_users: number;
  api_health: string;
  services: Array<{
    name: string;
    status: string;
    latency_ms: number;
  }>;
}

// ============================================
// CORE SYSTEM ENDPOINTS
// ============================================

/**
 * Health ping - Check if API is alive
 */
export async function ping(): Promise<ApiResponse<{ status: string; service: string; timestamp: string }>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/ping`);
  return res.json();
}

/**
 * Get full system status
 */
export async function getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/system-status`);
  return res.json();
}

/**
 * Get API info and endpoint list
 */
export async function getApiInfo(): Promise<ApiResponse<{
  name: string;
  version: string;
  status: string;
  endpoints: Record<string, Record<string, string>>;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api`);
  return res.json();
}

// ============================================
// CURIOSITY OCEAN AI ENDPOINTS
// ============================================

/**
 * Chat with Ocean AI
 */
export async function oceanChat(message: string, language: string = 'en'): Promise<OceanChatResponse> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/ocean`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language })
  });
  return res.json();
}

/**
 * Stream chat with Ocean AI
 */
export async function oceanChatStream(
  message: string, 
  language: string = 'en',
  onChunk: (chunk: string) => void
): Promise<void> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/ocean/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language })
  });

  const reader = res.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) throw new Error('No stream available');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }
}

// ============================================
// INFRASTRUCTURE ENDPOINTS
// ============================================

/**
 * Get ASI Trinity health status
 */
export async function getAsiHealth(): Promise<ApiResponse<{
  status: string;
  components: Array<{ name: string; status: string }>;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/asi/health`);
  return res.json();
}

/**
 * Get full ASI Trinity metrics
 */
export async function getAsiTrinity(): Promise<ApiResponse<{
  trinity: Array<{
    name: string;
    status: string;
    load: number;
    memory: number;
  }>;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/asi/trinity`);
  return res.json();
}

// ============================================
// REPORTING ENDPOINTS
// ============================================

/**
 * Get reporting service health
 */
export async function getReportingHealth(): Promise<ApiResponse<{ status: string }>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/reporting/health`);
  return res.json();
}

/**
 * Get dashboard metrics
 */
export async function getDashboardMetrics(): Promise<ApiResponse<DashboardMetrics>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/reporting/dashboard`);
  return res.json();
}

// ============================================
// VISION & AUDIO ENDPOINTS
// ============================================

/**
 * Process image with Vision AI (LLaVA)
 */
export async function visionAnalyze(imageBase64: string, prompt?: string): Promise<ApiResponse<{
  description: string;
  objects: string[];
  confidence: number;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/vision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64, prompt })
  });
  return res.json();
}

/**
 * Transcribe audio with Faster-Whisper
 */
export async function audioTranscribe(audioBase64: string, language?: string): Promise<ApiResponse<{
  text: string;
  language: string;
  duration_seconds: number;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/audio/transcribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ audio: audioBase64, language })
  });
  return res.json();
}

// ============================================
// ENGINE FLEET ENDPOINTS
// ============================================

/**
 * Get Pulse real-time data
 */
export async function getPulse(): Promise<ApiResponse<{
  heartbeat: number;
  active_connections: number;
  events_per_second: number;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/pulse`);
  return res.json();
}

/**
 * Get Grid computing status
 */
export async function getGrid(): Promise<ApiResponse<{
  nodes: number;
  active_tasks: number;
  compute_power: string;
}>> {
  const res = await fetch(`${CLISONIX_BASE_URL}/api/grid`);
  return res.json();
}

// ============================================
// HOOKS FOR REACT COMPONENTS
// ============================================

import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for real-time system status
 */
export function useSystemStatus(refreshInterval: number = 5000) {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await getSystemStatus();
      if (data.success) {
        setStatus(data.data);
        setError(null);
      } else {
        setError('Failed to fetch status');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, refreshInterval);
    return () => clearInterval(interval);
  }, [refresh, refreshInterval]);

  return { status, loading, error, refresh };
}

/**
 * Hook for Ocean AI chat
 */
export function useOceanChat() {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string, language: string = 'sq') => {
    setLoading(true);
    setError(null);
    setMessages(prev => [...prev, { role: 'user', content: message }]);

    try {
      const response = await oceanChat(message, language);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, loading, error, sendMessage, clearMessages };
}

/**
 * Hook for dashboard metrics
 */
export function useDashboardMetrics(refreshInterval: number = 10000) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await getDashboardMetrics();
      if (data.success) {
        setMetrics(data.data);
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, refreshInterval);
    return () => clearInterval(interval);
  }, [refresh, refreshInterval]);

  return { metrics, loading, error, refresh };
}

// Default export for convenience
export default {
  // Core
  ping,
  getSystemStatus,
  getApiInfo,
  
  // Ocean AI
  oceanChat,
  oceanChatStream,
  
  // Infrastructure
  getAsiHealth,
  getAsiTrinity,
  
  // Reporting
  getReportingHealth,
  getDashboardMetrics,
  
  // Vision & Audio
  visionAnalyze,
  audioTranscribe,
  
  // Engine
  getPulse,
  getGrid,
};
