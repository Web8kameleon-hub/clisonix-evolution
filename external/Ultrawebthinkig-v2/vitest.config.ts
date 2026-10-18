/**
 * Vitest Configuration - Web8 Industrial Testing
 * REAL API testing, ZERO DOM simulation, ZERO jsdom
 * Pure TypeScript + Real fetch + Real components
 */

import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom', // Enable jsdom for DOM testing with real data
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/*.js', // NO .js files allowed
      '**/*jest*', // NO jest files
      '**/*chunk*', // NO chunk files
      '**/*jsdom*' // NO jsdom files
    ],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test/',
        '**/*.js', // NO .js coverage
        '**/*jest*',
        '**/*chunk*'
      ]
    },
    // Pure TypeScript performance
    isolate: true,
    pool: 'threads',
    maxConcurrency: 8
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '.'),
      '@/components': resolve(__dirname, './components'),
      '@/lib': resolve(__dirname, './lib'),
      '@/utils': resolve(__dirname, './utils')
    }
  },
  // Web8 Industrial Optimization - NO artificial DOM dependencies
  optimizeDeps: {
    include: [
      'vitest' // ONLY vitest for real testing
    ],
    exclude: [
      'jest', // FORBIDDEN - no Jest
      'jsdom', // FORBIDDEN - no artificial DOM
      '@testing-library/react', // FORBIDDEN - no DOM simulation
      '@testing-library/jest-dom', // FORBIDDEN - no fake DOM
      'chunks', // FORBIDDEN - no chunks
      'useState' // FORBIDDEN - no React hooks in tests
    ]
  }
});
