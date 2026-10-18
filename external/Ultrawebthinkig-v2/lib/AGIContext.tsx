// React Context for inter-component state management
import React, { createContext, ReactNode, useEffect, useState } from 'react';
import { agiCore, getAGIMemory, AGIMemoryStore, subscribeToAGIMemory } from './AGICore';

interface AGIContextValue {
  memory: AGIMemoryStore;
  actions: {
    setActiveTab: (tab: string) => void;
    setAGIStatus: (status: AGIMemoryStore['agi']['status']) => void;
    addAGIResponse: (query: string, response: string) => void;
    setNavigationState: (state: string) => void;
    setTheme: (theme: AGIMemoryStore['ui']['theme']) => void;
    updateScrollPosition: (position: number) => void;
    addToHistory: (item: string) => void;
    setUserPreference: (key: string, value: unknown) => void;
  };
  ui: {
    activateElement: (elementId: string) => void;
    pulseElement: (elementId: string) => void;
    setDynamicStyle: (key: string, value: string) => void;
  };
}

const AGIContext = createContext<AGIContextValue | null>(null);

interface AGIProviderProps {
  children: ReactNode;
}

export function AGIProvider({ children }: AGIProviderProps) {
  const [memory, setMemory] = useState<AGIMemoryStore>(getAGIMemory(state => state));

  useEffect(() => {
    const unsubscribe = subscribeToAGIMemory(() => {
      setMemory(getAGIMemory(state => state));
    });
    return unsubscribe;
  }, []);

  const actions = {
    setActiveTab: (tab: string) => {
      agiCore.setActiveTab(tab);
    },

    setAGIStatus: (status: AGIMemoryStore['agi']['status']) => {
      agiCore.setAGIStatus(status);
    },

    addAGIResponse: (query: string, response: string) => {
      agiCore.addAGIResponse(query, response);
    },

    setNavigationState: (state: string) => {
      agiCore.setNavigationState(state);
    },

    setTheme: (theme: AGIMemoryStore['ui']['theme']) => {
      agiCore.setTheme(theme);
    },

    updateScrollPosition: (position: number) => {
      agiCore.updateMemory('ui.scrollPosition', position);
    },

    addToHistory: (item: string) => {
      const currentHistory = memory.user.history;
      const newHistory = [...currentHistory, item].slice(-50); // Keep last 50
      agiCore.updateMemory('user.history', newHistory);
    },

    setUserPreference: (key: string, value: unknown) => {
      const preferences = { ...memory.user.preferences, [key]: value };
      agiCore.updateMemory('user.preferences', preferences);
    }
  };

  const ui = {
    activateElement: (elementId: string) => {
      // Pure CSS approach - add active class
      const element = document.getElementById(elementId);
      if (element) {
        element.classList.add('active');
      }
    },

    pulseElement: (elementId: string) => {
      // Pure CSS approach - add pulse class
      const element = document.getElementById(elementId);
      if (element) {
        element.classList.add('pulse');
        setTimeout(() => element.classList.remove('pulse'), 1000);
      }
    },

    setDynamicStyle: (key: string, value: string) => {
      // Pure CSS variables approach
      if (typeof document !== 'undefined') {
        document.documentElement.style.setProperty(`--${key}`, value)
      }
    }
  }

  return (
    <AGIContext.Provider value={{ agiCore, memory, ui }}>
      {children}
    </AGIContext.Provider>
  )
}