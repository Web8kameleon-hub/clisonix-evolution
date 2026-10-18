'use client';

/**
 * AGI Provider - Core AI Provider System
 * Web8 Industrial Grade AI Provider Management
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra
 */

import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode, ComponentType } from 'react';

// AGI Provider Types
export interface AGIConfig {
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface AGIResponse {
  content: string;
  provider: string;
  timestamp: number;
  tokens?: number;
  processingTime?: number;
}

export interface AGIProviderState {
  isConnected: boolean;
  currentProvider: 'openai' | 'ollama' | 'fallback';
  isProcessing: boolean;
  lastResponse?: AGIResponse;
  error?: string | undefined;
}

// AGI Context
const AGIContext = createContext<{
  state: AGIProviderState;
  sendMessage: (message: string) => Promise<AGIResponse>;
  switchProvider: (provider: 'openai' | 'ollama' | 'fallback') => void;
} | null>(null);

// AGI Provider Component
export function AGIProvider({ 
  children, 
  config = {} 
}: { 
  children: ReactNode;
  config?: AGIConfig;
}) {
  const [state, setState] = useState<AGIProviderState>({
    isConnected: false,
    currentProvider: 'openai',
    isProcessing: false
  });

  useEffect(() => {
    // Initialize AGI connection
    setState(prev => ({ ...prev, isConnected: true }));
  }, []);

  const sendMessage = async (message: string): Promise<AGIResponse> => {
    setState(prev => ({ ...prev, isProcessing: true, error: undefined }));
    
    try {
      const startTime = Date.now();
      
      // Use the existing API route
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message,
          provider: state.currentProvider 
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      const processingTime = Date.now() - startTime;
      
      const agiResponse: AGIResponse = {
        content: data.message || data.response || 'No response',
        provider: data.provider || state.currentProvider,
        timestamp: Date.now(),
        processingTime
      };

      setState(prev => ({ 
        ...prev, 
        isProcessing: false,
        lastResponse: agiResponse,
        currentProvider: data.provider || prev.currentProvider
      }));

      return agiResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({ 
        ...prev, 
        isProcessing: false, 
        error: errorMessage 
      }));
      
      // Return fallback response
      return {
        content: `Error: ${errorMessage}. Using fallback response.`,
        provider: 'fallback',
        timestamp: Date.now()
      };
    }
  };

  const switchProvider = (provider: 'openai' | 'ollama' | 'fallback') => {
    setState(prev => ({ ...prev, currentProvider: provider }));
  };

  return (
    <AGIContext.Provider value={{ state, sendMessage, switchProvider }}>
      {children}
    </AGIContext.Provider>
  );
}

// Custom hook for using AGI
export function useAGI() {
  const context = useContext(AGIContext);
  if (!context) {
    throw new Error('useAGI must be used within an AGIProvider');
  }
  return context;
}

// AGI Provider HOC
export function withAGI<P extends object>(Component: ComponentType<P>) {
  return function AGIWrappedComponent(props: P) {
    return (
      <AGIProvider config={{}}>
        <Component {...props} />
      </AGIProvider>
    );
  };
}
