import React from 'react';
/**
 * EuroWeb Named Export Utilities
 * Pure TypeScript utility functions with named exports only
 * 
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 * @version 8.0.0
 * @license MIT
 */

/**
 * Configuration object për Web8 platform
 */
export const WEB8_CONFIG = {
  platform: 'EuroWeb',
  version: '8.0.0',
  stack: ['TypeScript', 'CSS Modules', 'CVA', 'Framer Motion', 'Yarn Berry'],
  exports: 'named-only',
  architecture: 'modular-industrial'
} as const;

/**
 * Utility për logging me named export
 */
export function logWeb8Status(message: string): void {
  }

/**
 * Type-safe utility për CSS class management
 */
export function combineClasses(...classes: (string | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Utility për format dates
 */
export function formatTimestamp(date: Date): string {
  return date.toISOString().replace('T', ' ').slice(0, 19);
}

/**
 * Generate unique ID 
 */
export function generateId(prefix: string = 'web8'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Environment checker
 */
export function isDevelopment(): boolean {
  return process.env.NODE_ENV === 'development';
}

export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production';
}

/**
 * Web8 Performance Tracking - Functional Pattern
 */
interface Web8PerformanceContext {
  readonly startTime: number;
  readonly label: string;
}

function startPerformanceTracking(label: string): Web8PerformanceContext {
  return {
    startTime: performance.now(),
    label
  };
}

function stopPerformanceTracking(context: Web8PerformanceContext): number {
  const duration = performance.now() - context.startTime;
  logWeb8Status(`${context.label} completed in ${duration.toFixed(2)}ms`);
  return duration;
}

// Helper function for quick performance measurement
function measurePerformance<T>(label: string, fn: () => T): T {
  const context = startPerformanceTracking(label);
  const result = fn();
  stopPerformanceTracking(context);
  return result;
}

/**
 * Type utilities për named exports
 */
export type Web8Component<T = {}> = React.FC<T>;
export type Web8Config = typeof WEB8_CONFIG;
export type ClassNames = string | undefined | null;

// Export Web8 performance functions and types
export {
  startPerformanceTracking,
  stopPerformanceTracking,
  measurePerformance
};

export type { Web8PerformanceContext };

/**
 * Constants për theming
 */
export const THEME_COLORS = {
  primary: '#3b82f6',
  secondary: '#6366f1', 
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  background: '#0f172a',
  surface: '#1e293b',
  text: '#f1f5f9',
  textMuted: '#94a3b8'
} as const;

/**
 * Animation presets për framer-motion
 */
export const MOTION_PRESETS = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.3 }
  },
  slideUp: {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  },
  stagger: {
    animate: {
      transition: { staggerChildren: 0.1 }
    }
  }
} as const;
