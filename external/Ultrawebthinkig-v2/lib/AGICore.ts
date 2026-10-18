// AGICore - Intelligent state management for Web8
import React from 'react';

export interface AGIMemoryStore {
  ui: {
    activeTab: string;
    scrollPosition: number;
    theme: 'light' | 'dark' | 'nature';
    navigationState: string;
  };
  agi: {
    status: 'ACTIVE' | 'PROCESSING' | 'IDLE';
    lastQuery: string;
    responses: string[];
    brainActive: boolean;
  };
  user: {
    preferences: Record<string, any>;
    history: string[];
    currentTime: string;
  };
}

class AGICore {
  private memory: AGIMemoryStore;
  private listeners: Set<() => void> = new Set();
  private storageKey = 'web8-agi-memory';

  constructor() {
    this.memory = this.loadMemory();
    this.startTimeUpdate();
  }

  // Load memory from localStorage or create default
  private loadMemory(): AGIMemoryStore {
    if (typeof window === 'undefined') {
      return this.getDefaultMemory();
    }

    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsedStored = JSON.parse(stored);
        const defaultMemory = this.getDefaultMemory();
        
        // Deep merge with defaults to ensure all properties exist
        return {
          ui: { ...defaultMemory.ui, ...parsedStored.ui },
          agi: { ...defaultMemory.agi, ...parsedStored.agi },
          user: { ...defaultMemory.user, ...parsedStored.user }
        };
      }
    } catch (error) {
      console.warn('AGICore: Failed to load memory from storage', error);
    }

    return this.getDefaultMemory();
  }

  private getDefaultMemory(): AGIMemoryStore {
    return {
      ui: {
        activeTab: 'agi-dashboard',
        scrollPosition: 0,
        theme: 'nature',
        navigationState: 'hero'
      },
      agi: {
        status: 'ACTIVE',
        lastQuery: '',
        responses: [],
        brainActive: true
      },
      user: {
        preferences: {},
        history: [],
        currentTime: new Date().toISOString()
      }
    };
  }

  // Save memory to localStorage
  private saveMemory(): void {
    if (typeof window === 'undefined') {return;}

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.memory));
    } catch (error) {
      console.warn('AGICore: Failed to save memory to storage', error);
    }
  }

  // Get current memory state
  public getMemory(): Readonly<AGIMemoryStore> {
    return this.memory;
  }

  // Update memory and notify listeners
  public updateMemory(path: string, value: unknown): void {
    const keys = path.split('.');
    let current: unknown = this.memory;

    // Navigate to the parent of the target property
    for (let i = 0; i < keys.length - 1; i++) {
      if (!(keys[i] in current)) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    // Set the value
    current[keys[keys.length - 1]] = value;

    this.saveMemory();
    this.notifyListeners();
  }

  // Subscribe to memory changes
  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener());
  }

  // Start automatic time updates
  private startTimeUpdate(): void {
    if (typeof window === 'undefined') {return;}

    setInterval(() => {
      this.updateMemory('user.currentTime', new Date().toISOString());
    }, 1000);

    // AGI status simulation
    setInterval(() => {
      const currentStatus = this.memory.agi?.status || 'ACTIVE';
      const newStatus = currentStatus === 'ACTIVE' ? 'PROCESSING' : 'ACTIVE';
      this.updateMemory('agi.status', newStatus);
    }, 3000);
  }

  // Utility methods for common operations
  public setActiveTab(tab: string): void {
    this.updateMemory('ui.activeTab', tab);
  }

  public setAGIStatus(status: AGIMemoryStore['agi']['status']): void {
    this.updateMemory('agi.status', status);
  }

  public addAGIResponse(query: string, response: string): void {
    this.updateMemory('agi.lastQuery', query);
    // Safe access to responses array with fallback
    const currentResponses = this.memory.agi?.responses || [];
    const responses = [...currentResponses, response];
    this.updateMemory('agi.responses', responses.slice(-10)); // Keep last 10
  }

  public setNavigationState(state: string): void {
    this.updateMemory('ui.navigationState', state);
  }

  public setTheme(theme: AGIMemoryStore['ui']['theme']): void {
    this.updateMemory('ui.theme', theme);
  }
}

// Global AGI instance
export const agiCore = new AGICore();

// Pure TypeScript AGI memory accessor - NO HOOKS
export function getAGIMemory<T>(selector: (memory: AGIMemoryStore) => T): T {
  return selector(agiCore.getMemory());
}

// AGI memory subscription for manual updates
export function subscribeToAGIMemory(callback: () => void): () => void {
  return agiCore.subscribe(callback);
}

export { AGICore }
