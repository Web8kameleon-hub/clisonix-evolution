// core/types/chat.ts
export type AIProvider = 'openmind' | 'anthropic' | 'openai' | 'local';
export type ThinkingDepth = 'shallow' | 'standard' | 'deep' | 'ultra-deep';
export type ThinkingStrategy = 'analytical' | 'creative' | 'critical' | 'strategic';

export interface UltraMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  provider: AIProvider;
  timestamp: Date;
  metadata: {
    tokens: number;
    latency: number;
    confidence?: number;
    reasoning?: string[];
    cost?: number;
  };
  status: 'sending' | 'delivered' | 'error' | 'cancelled';
}

export interface ChatSession {
  id: string;
  messages: UltraMessage[];
  context: ChatContext;
  metrics: SessionMetrics;
  security: SecurityContext;
}

export interface ChatContext {
  topic: string;
  depth: ThinkingDepth;
  strategy: ThinkingStrategy;
  constraints: string[];
  temperature: number;
}

export interface SessionMetrics {
  totalTokens: number;
  totalCost: number;
  averageLatency: number;
  startTime: Date;
  messageCount: number;
}

export interface SecurityContext {
  isVerified: boolean;
  threatLevel: 'low' | 'medium' | 'high';
  violations: SecurityViolation[];
  lastScan: Date;
}

export interface SecurityViolation {
  type: 'content' | 'rate' | 'injection' | 'privacy';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: Date;
}

export interface ThinkingConfig {
  depth: ThinkingDepth;
  strategy: ThinkingStrategy;
  temperature: number;
  maxTokens?: number;
}
