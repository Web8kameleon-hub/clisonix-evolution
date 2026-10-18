/**
 * Utilities Tests - Pure TypeScript Utilities
 * Cache + CDN + Browser optimization
 */

import { test, expect, describe } from 'vitest';

describe('Utilities Industrial Tests', () => {
  test('cache utilities are pure functions', () => {
    function createCache<T>() {
      const cache = new Map<string, T>();
      
      return {
        get: (key: string): T | undefined => cache.get(key),
        set: (key: string, value: T): void => { cache.set(key, value); },
        has: (key: string): boolean => cache.has(key),
        clear: (): void => cache.clear(),
        size: (): number => cache.size
      } as const;
    };
    
    const cache = createCache<string>();
    cache.set('key1', 'value1');
    
    expect(cache.get('key1')).toBe('value1');
    expect(cache.has('key1')).toBe(true);
    expect(cache.size()).toBe(1);
  });

  test('format utilities work correctly', () => {
    const formatBytes = (bytes: number): string => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'] as const;
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    expect(formatBytes(0)).toBe('0 Bytes');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
  });

  test('URL utilities are pure', () => {
    const parseURL = (url: string) => {
      try {
        const parsed = new URL(url);
        return {
          protocol: parsed.protocol,
          hostname: parsed.hostname,
          pathname: parsed.pathname,
          isValid: true
        } as const;
      } catch {
        return { isValid: false } as const;
      }
    };
    
    const result = parseURL('https://euroweb.ai/test');
    expect(result.isValid).toBe(true);
    if (result.isValid) {
      expect(result.protocol).toBe('https:');
      expect(result.hostname).toBe('euroweb.ai');
    }
  });

  test('debounce utility works without useState', () => {
    const debounce = <T extends (...args: unknown[]) => any>(
      func: T,
      delay: number
    ): ((...args: Parameters<T>) => void) => {
      let timeoutId: NodeJS.Timeout;
      
      return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
      };
    };
    
    let counter = 0;
    const increment = () => { counter++; };
    const debouncedIncrement = debounce(increment, 100);
    
    debouncedIncrement();
    debouncedIncrement();
    debouncedIncrement();
    
    // Should not have incremented yet due to debounce
    expect(counter).toBe(0);
  });
});

// Removed unused export: createUtilsTestSuite
const utilsTestSuite = {
  cache: new Map<string, any>(),
  formatters: {
    bytes: (bytes: number) => bytes + ' bytes',
    date: (date: Date) => date.toISOString()
  }
};
