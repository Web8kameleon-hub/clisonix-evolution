// config/openmind.ts
import { AIProvider } from '../core/types/chat';

export interface ProviderConfig {
  name: string;
  description: string;
  icon: string;
  apiKey?: string;
  baseURL?: string;
  enabled: boolean;
  models: string[];
}

export interface OpenMindConfig {
  providers: Record<AIProvider, ProviderConfig>;
  defaultProvider: AIProvider;
  security: {
    maxContentLength: number;
    rateLimit: number;
    threatCheck: boolean;
  };
  performance: {
    timeout: number;
    retryAttempts: number;
    cacheResponses: boolean;
  };
}

export const OPENMIND_CONFIG: OpenMindConfig = {
  providers: {
    openmind: {
      name: 'OpenMind AGI',
      description: 'Advanced Galactic Intelligence with multi-dimensional reasoning',
      icon: '🧠',
      enabled: true,
      models: ['galactic-thinking-v2', 'multi-dimensional-reasoning-v1']
    },
    anthropic: {
      name: 'Anthropic Claude',
      description: 'Constitutional AI with strong safety and reasoning capabilities',
      icon: '🔮',
      enabled: true,
      models: ['claude-3-sonnet', 'claude-3-opus', 'claude-3-haiku']
    },
    openai: {
      name: 'OpenAI GPT',
      description: 'State-of-the-art language model with broad knowledge and capabilities',
      icon: '⚡',
      enabled: true,
      models: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
    },
    local: {
      name: 'Local Models',
      description: 'Privacy-focused local inference with optimized performance',
      icon: '💻',
      enabled: true,
      models: ['llama-3-8b', 'mistral-7b', 'phi-3-mini']
    }
  },
  defaultProvider: 'openmind',
  security: {
    maxContentLength: 10000,
    rateLimit: 100,
    threatCheck: true
  },
  performance: {
    timeout: 30000,
    retryAttempts: 3,
    cacheResponses: true
  }
};
