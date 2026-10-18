/**
 * Web8 React Hooks - Simplified State Management
 * React hooks for Web8 State with real-time updates
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra + React Integration
 */

import { useState, useCallback, useRef } from 'react';

// Simplified action interface
interface SimpleAction {
  type: string;
  payload?: any;
}

// Global state registry for sharing between components
const globalStates = new Map<string, any>();
const stateSubscribers = new Map<string, Set<(state: any) => void>>();

/**
 * useWeb8State - Primary hook for Web8 state management
 */
export function useWeb8State<T>(
  key: string,
  initialState: T,
  reducer?: (state: T, action: SimpleAction) => T
) {
  // Initialize global state if not exists
  if (!globalStates.has(key)) {
    globalStates.set(key, initialState);
    stateSubscribers.set(key, new Set());
  }

  const [state, setState] = useState<T>(() => globalStates.get(key) || initialState);
  const subscriberRef = useRef<((state: T) => void) | null>(null);

  // Subscribe to global state changes
  if (!subscriberRef.current) {
    subscriberRef.current = (newState: T) => setState(newState);
    stateSubscribers.get(key)?.add(subscriberRef.current);
  }

  // Dispatch action
  const dispatch = useCallback((action: SimpleAction) => {
    const currentState = globalStates.get(key);
    const newState = reducer ? reducer(currentState, action) : currentState;
    
    // Update global state
    globalStates.set(key, newState);
    
    // Notify all subscribers
    stateSubscribers.get(key)?.forEach(subscriber => {
      subscriber(newState);
    });
  }, [key, reducer]);

  // Get current state
  const getState = useCallback(() => {
    return globalStates.get(key) || state;
  }, [key, state]);

  return [state, dispatch, getState] as const;
}

/**
 * useWeb8GlobalState - For global application state
 */
export function useWeb8GlobalState<T>(initialState: T) {
  return useWeb8State('__global__', initialState);
}

/**
 * useWeb8AI - Specialized hook for AI chat state
 */
export interface AIState {
  messages: Array<{
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: number;
  }>;
  isLoading: boolean;
  error: string | null;
  provider: 'openai' | 'ollama' | 'fallback';
}

const initialAIState: AIState = {
  messages: [],
  isLoading: false,
  error: null,
  provider: 'openai'
};

function aiReducer(state: AIState, action: any): AIState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload]
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false
      };
    
    case 'SET_PROVIDER':
      return {
        ...state,
        provider: action.payload
      };
    
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: []
      };
    
    default:
      return state;
  }
}

export function useWeb8AI() {
  const [state, dispatch] = useWeb8State('ai-chat', initialAIState, aiReducer);

  const addMessage = useCallback((content: string, role: 'user' | 'assistant') => {
    dispatch({
      type: 'ADD_MESSAGE',
      payload: {
        id: crypto.randomUUID(),
        content,
        role,
        timestamp: Date.now()
      }
    });
  }, [dispatch]);

  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, [dispatch]);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, [dispatch]);

  const setProvider = useCallback((provider: 'openai' | 'ollama' | 'fallback') => {
    dispatch({ type: 'SET_PROVIDER', payload: provider });
  }, [dispatch]);

  const clearMessages = useCallback(() => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  }, [dispatch]);

  return {
    ...state,
    addMessage,
    setLoading,
    setError,
    setProvider,
    clearMessages
  };
}

/**
 * useWeb8Security - Hook for Guardian security state
 */
export interface SecurityState {
  isActive: boolean;
  threatLevel: 'low' | 'medium' | 'high';
  blockedRequests: number;
  lastScan: number | null;
  violations: string[];
}

const initialSecurityState: SecurityState = {
  isActive: true,
  threatLevel: 'low',
  blockedRequests: 0,
  lastScan: null,
  violations: []
};

function securityReducer(state: SecurityState, action: any): SecurityState {
  switch (action.type) {
    case 'UPDATE_THREAT_LEVEL':
      return {
        ...state,
        threatLevel: action.payload
      };
    
    case 'BLOCK_REQUEST':
      return {
        ...state,
        blockedRequests: state.blockedRequests + 1,
        violations: [...state.violations, action.payload]
      };
    
    case 'UPDATE_SCAN':
      return {
        ...state,
        lastScan: Date.now()
      };
    
    default:
      return state;
  }
}

export function useWeb8Security() {
  const [state, dispatch] = useWeb8State('security', initialSecurityState, securityReducer);

  const updateThreatLevel = useCallback((level: 'low' | 'medium' | 'high') => {
    dispatch({ type: 'UPDATE_THREAT_LEVEL', payload: level });
  }, [dispatch]);

  const reportBlockedRequest = useCallback((violation: string) => {
    dispatch({ type: 'BLOCK_REQUEST', payload: violation });
  }, [dispatch]);

  const updateLastScan = useCallback(() => {
    dispatch({ type: 'UPDATE_SCAN' });
  }, [dispatch]);

  return {
    ...state,
    updateThreatLevel,
    reportBlockedRequest,
    updateLastScan
  };
}

/**
 * useWeb8Performance - Hook for performance monitoring
 */
export interface PerformanceState {
  responseTime: number;
  memoryUsage: number;
  activeConnections: number;
  errorRate: number;
}

const initialPerformanceState: PerformanceState = {
  responseTime: 0,
  memoryUsage: 0,
  activeConnections: 0,
  errorRate: 0
};

export function useWeb8Performance() {
  const [state, dispatch] = useWeb8State('performance', initialPerformanceState);

  const updateMetrics = useCallback((metrics: Partial<PerformanceState>) => {
    dispatch({ type: 'UPDATE_METRICS', payload: metrics });
  }, [dispatch]);

  return {
    ...state,
    updateMetrics
  };
}
