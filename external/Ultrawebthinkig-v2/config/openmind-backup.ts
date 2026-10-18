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
  // Primary AI Providers
  providers: {
    openmind: {
      name: 'OpenMind AI',
      url: 'https://openmind.ai',
      apiUrl: 'https://api.openmind.ai/v1',
      description: 'Advanced AI reasoning and creativity',
      icon: '🧠',
      enabled: true,
      priority: 1
    },
    claude: {
      name: 'Anthropic Claude',
      url: 'https://claude.ai',
      apiUrl: 'https://api.anthropic.com/v1',
      description: 'Constitutional AI with strong reasoning',
      icon: '🤖',
      enabled: true,
      priority: 2
    },
    copilot: {
      name: 'GitHub Copilot',
      url: 'https://github.com/features/copilot',
      apiUrl: 'https://api.github.com/copilot',
      description: 'AI pair programmer for developers',
      icon: '👨‍💻',
      enabled: true,
      priority: 3
    },
    deepseek: {
      name: 'DeepSeek AI',
      url: 'https://deepseek.com',
      apiUrl: 'https://api.deepseek.com/v1',
      description: 'Deep reasoning and mathematical AI',
      icon: '🔍',
      enabled: true,
      priority: 4
    },
    openai: {
      name: 'OpenAI GPT',
      url: 'https://openai.com',
      apiUrl: 'https://api.openai.com/v1',
      description: 'ChatGPT and GPT-4 models',
      icon: '✨',
      enabled: true,
      priority: 5
    },
    llamagpt: {
      name: 'LlamaGPT',
      url: 'https://llama.ai',
      apiUrl: 'https://api.llama.ai/v1',
      description: 'Open-source language models',
      icon: '🦙',
      enabled: true,
      priority: 6
    },
    gemini: {
      name: 'Google Gemini',
      url: 'https://gemini.google.com',
      apiUrl: 'https://generativelanguage.googleapis.com/v1',
      description: 'Google\'s multimodal AI',
      icon: '💎',
      enabled: true,
      priority: 7
    },
    perplexity: {
      name: 'Perplexity AI',
      url: 'https://perplexity.ai',
      apiUrl: 'https://api.perplexity.ai',
      description: 'Real-time search and reasoning',
      icon: '🔎',
      enabled: true,
      priority: 8
    }
  },

  // Model Configuration
  models: {
    openmind: ['openmind-latest', 'openmind-reasoning', 'openmind-creative'],
    claude: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
    copilot: ['gpt-4', 'gpt-3.5-turbo'],
    deepseek: ['deepseek-chat', 'deepseek-coder'],
    openai: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo'],
    llamagpt: ['llama-2-70b-chat', 'llama-2-13b-chat', 'llama-2-7b-chat'],
    gemini: ['gemini-pro', 'gemini-pro-vision'],
    perplexity: ['llama-3.1-sonar-large-128k-online', 'llama-3.1-sonar-small-128k-online']
  },

  // Default Settings
  defaults: {
    temperature: 0.7,
    maxTokens: 2048,
    topP: 0.9,
    frequencyPenalty: 0,
    presencePenalty: 0
  },

  // Rate Limiting
  rateLimits: {
    requestsPerMinute: 60,
    requestsPerHour: 1000,
    requestsPerDay: 10000
  },

  // Feature Flags
  features: {
    streaming: true,
    multiModal: true,
    codeGeneration: true,
    webSearch: true,
    imageGeneration: false,
    voiceChat: false
  }
};

export type AIProvider = keyof typeof OPENMIND_CONFIG.providers
export type AIModel = string
