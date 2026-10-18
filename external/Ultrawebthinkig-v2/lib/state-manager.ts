/**
 * Web8 State Manager - AGI-Controlled Application State
 * Replaces Redux-like patterns with functional state management
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Web8
 * @license MIT
 */

import { createMemoryContext, setCacheEntry, getCacheEntry, Web8MemoryContext } from './memory-manager';

interface StateManagerConfig {
  enablePersistence: boolean;
  enableDevTools: boolean;
  enableMiddleware: boolean;
  cacheEnabled: boolean;
  maxHistorySize: number;
}

interface Action {
  type: string;
  payload?: unknown;
  meta?: {
    timestamp: number;
    id: string;
  };
}

interface StateSnapshot {
  state: unknown;
  timestamp: number;
  action: Action;
}

// Web8 State Context
interface Web8StateContext<T> {
  readonly currentState: T;
  readonly config: StateManagerConfig;
  readonly history: readonly StateSnapshot[];
  readonly subscribers: readonly Subscriber[];
  readonly middlewares: readonly Middleware[];
  readonly memoryContext: Web8MemoryContext;
  readonly isDispatching: boolean;
}

type Middleware = (context: Web8StateContext<any>) => (next: Dispatch) => (action: Action) => Web8StateContext<any>;
type Dispatch = (action: Action) => Web8StateContext<any>;
type Subscriber = (state: unknown, prevState: unknown) => void;
type Reducer<T> = (state: T, action: Action) => T;

// Web8 Default State Configuration
const defaultStateConfig: StateManagerConfig = {
  enablePersistence: false,
  enableDevTools: false,
  enableMiddleware: true,
  cacheEnabled: true,
  maxHistorySize: 50
};

// Web8 State Context Factory
function createStateContext<T>(
  initialState: T,
  reducer: Reducer<T>,
  config: Partial<StateManagerConfig> = {}
): Web8StateContext<T> {
  const fullConfig = {
    ...defaultStateConfig,
    ...config
  };

  const memoryContext = createMemoryContext({
    maxCacheSize: 10 * 1024 * 1024, // 10MB
    cleanupInterval: 300000, // 5 minutes
    compressionEnabled: true,
    debugMode: fullConfig.enableDevTools
  });

  return {
    currentState: initialState,
    config: fullConfig,
    history: [],
    subscribers: [],
    middlewares: [],
    memoryContext,
    isDispatching: false
  };
}

// Web8 Action Creation
function createAction(type: string, payload?: unknown): Action {
  return {
    type,
    payload,
    meta: {
      timestamp: Date.now(),
      id: crypto.randomUUID()
    }
  };
}

// Web8 State Subscription
function addSubscriber<T>(
  context: Web8StateContext<T>,
  subscriber: Subscriber
): Web8StateContext<T> {
  return {
    ...context,
    subscribers: [...context.subscribers, subscriber]
  };
}

function removeSubscriber<T>(
  context: Web8StateContext<T>,
  subscriber: Subscriber
): Web8StateContext<T> {
  return {
    ...context,
    subscribers: context.subscribers.filter(s => s !== subscriber)
  };
}

// Web8 Middleware Management
function addMiddleware<T>(
  context: Web8StateContext<T>,
  middleware: Middleware
): Web8StateContext<T> {
  return {
    ...context,
    middlewares: [...context.middlewares, middleware]
  };
}

// Web8 State Dispatch
function dispatchAction<T>(
  context: Web8StateContext<T>,
  reducer: Reducer<T>,
  action: Action
): Web8StateContext<T> {
  if (context.isDispatching) {
    throw new Error('Cannot dispatch action while already dispatching');
  }

  let updatedContext = {
    ...context,
    isDispatching: true
  };

  try {
    const previousState = updatedContext.currentState;
    
    // Apply middleware chain
    let finalAction = action;
    for (const middleware of updatedContext.middlewares) {
      const middlewareResult = middleware(updatedContext);
      // Simplified middleware application for Web8
      finalAction = action; // In real implementation, middleware would transform action
    }

    // Apply reducer
    const newState = reducer(updatedContext.currentState, finalAction);
    
    // Create state snapshot
    const snapshot: StateSnapshot = {
      state: newState,
      timestamp: Date.now(),
      action: finalAction
    };

    // Update history
    const newHistory = [...updatedContext.history, snapshot];
    const trimmedHistory = newHistory.length > updatedContext.config.maxHistorySize
      ? newHistory.slice(-updatedContext.config.maxHistorySize)
      : newHistory;

    // Cache state if enabled
    let newMemoryContext = updatedContext.memoryContext;
    if (updatedContext.config.cacheEnabled) {
      const cacheResult = setCacheEntry(
        newMemoryContext,
        `state_${snapshot.timestamp}`,
        newState
      );
      newMemoryContext = cacheResult;
    }

    // Update context
    updatedContext = {
      ...updatedContext,
      currentState: newState,
      history: trimmedHistory,
      memoryContext: newMemoryContext,
      isDispatching: false
    };

    // Notify subscribers
    updatedContext.subscribers.forEach(subscriber => {
      try {
        subscriber(newState, previousState);
      } catch (error) {
        console.error('Web8 State: Subscriber error:', error);
      }
    });

    // DevTools integration
    if (updatedContext.config.enableDevTools) {
      console.log('🏛️ Web8 State:', {
        action: finalAction.type,
        payload: finalAction.payload,
        previousState,
        newState,
        timestamp: snapshot.timestamp
      });
    }

    return updatedContext;

  } catch (error) {
    console.error('Web8 State: Dispatch error:', error);
    return {
      ...updatedContext,
      isDispatching: false
    };
  }
}

// Web8 State Selectors
function selectState<T>(context: Web8StateContext<T>): T {
  return context.currentState;
}

function selectStateSlice<T, K extends keyof T>(
  context: Web8StateContext<T>,
  key: K
): T[K] {
  return context.currentState[key];
}

// Web8 State History
function getStateHistory<T>(context: Web8StateContext<T>): readonly StateSnapshot[] {
  return context.history;
}

function getLastAction<T>(context: Web8StateContext<T>): Action | null {
  const lastSnapshot = context.history[context.history.length - 1];
  return lastSnapshot ? lastSnapshot.action : null;
}

// Web8 State Time Travel
function revertToSnapshot<T>(
  context: Web8StateContext<T>,
  snapshotIndex: number
): Web8StateContext<T> {
  if (snapshotIndex < 0 || snapshotIndex >= context.history.length) {
    throw new Error('Invalid snapshot index');
  }

  const targetSnapshot = context.history[snapshotIndex];
  if (!targetSnapshot) {
    throw new Error('Snapshot not found');
  }
  
  return {
    ...context,
    currentState: targetSnapshot.state as T,
    history: context.history.slice(0, snapshotIndex + 1)
  };
}

// Web8 State Persistence
function saveStateToPersistence<T>(
  context: Web8StateContext<T>,
  key: string = 'web8_state'
): void {
  if (!context.config.enablePersistence) {
    return;
  }

  try {
    const stateData = {
      state: context.currentState,
      timestamp: Date.now(),
      history: context.history.slice(-10) // Save last 10 snapshots
    };
    
    localStorage.setItem(key, JSON.stringify(stateData));
    
    if (context.config.enableDevTools) {
      console.log('🏛️ Web8 State: Saved to persistence');
    }
  } catch (error) {
    console.error('Web8 State: Persistence save error:', error);
  }
}

function loadStateFromPersistence<T>(
  defaultState: T,
  key: string = 'web8_state'
): { state: T; history: StateSnapshot[] } {
  try {
    const stored = localStorage.getItem(key);
    if (!stored) {
      return { state: defaultState, history: [] };
    }

    const stateData = JSON.parse(stored);
    return {
      state: stateData.state || defaultState,
      history: stateData.history || []
    };
  } catch (error) {
    console.error('Web8 State: Persistence load error:', error);
    return { state: defaultState, history: [] };
  }
}

// Web8 State Analytics
function analyzeStateUsage<T>(context: Web8StateContext<T>): {
  totalActions: number;
  actionTypes: Record<string, number>;
  averageStateSize: number;
  memoryUsage: number;
} {
  const actionTypes: Record<string, number> = {};
  
  context.history.forEach(snapshot => {
    const type = snapshot.action.type;
    actionTypes[type] = (actionTypes[type] || 0) + 1;
  });

  const averageStateSize = context.history.length > 0
    ? context.history.reduce((sum, snapshot) => {
        return sum + JSON.stringify(snapshot.state).length;
      }, 0) / context.history.length
    : 0;

  return {
    totalActions: context.history.length,
    actionTypes,
    averageStateSize,
    memoryUsage: JSON.stringify(context.currentState).length
  };
}

// Web8 Built-in Middleware
const loggingMiddleware: Middleware = (context) => (next) => (action) => {
  console.group(`🏛️ Web8 State Action: ${action.type}`);
  console.log('Payload:', action.payload);
  console.log('Previous State:', context.currentState);
  
  const result = next(action);
  
  console.log('New State:', result.currentState);
  console.groupEnd();
  
  return result;
};

const performanceMiddleware: Middleware = (context) => (next) => (action) => {
  const startTime = performance.now();
  const result = next(action);
  const endTime = performance.now();
  
  if (context.config.enableDevTools) {
    console.log(`🏛️ Web8 State Performance: ${action.type} took ${(endTime - startTime).toFixed(2)}ms`);
  }
  
  return result;
};

// Web8 Functional Exports
export {
  createStateContext,
  createAction,
  addSubscriber,
  removeSubscriber,
  addMiddleware,
  dispatchAction,
  selectState,
  selectStateSlice,
  getStateHistory,
  getLastAction,
  revertToSnapshot,
  saveStateToPersistence,
  loadStateFromPersistence,
  analyzeStateUsage,
  loggingMiddleware,
  performanceMiddleware
};

export type {
  Web8StateContext,
  StateManagerConfig,
  Action,
  StateSnapshot,
  Middleware,
  Dispatch,
  Subscriber,
  Reducer
};
