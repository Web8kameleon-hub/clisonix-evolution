/**
 * Vitest Global Setup for jsdom environment
 * Ensures proper DOM APIs and browser globals are available
 */
import { vi } from 'vitest'
import '@testing-library/jest-dom'

// Setup DOM globals for jsdom environment
Object.defineProperty(global, 'navigator', {
  value: {
    userAgent: 'Mozilla/5.0 (jsdom)',
    onLine: true
  },
  writable: true
})

Object.defineProperty(global, 'document', {
  value: globalThis.document,
  writable: true
})

Object.defineProperty(global, 'window', {
  value: globalThis.window,
  writable: true
})

// Mock fetch for API calls
global.fetch = vi.fn()

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})