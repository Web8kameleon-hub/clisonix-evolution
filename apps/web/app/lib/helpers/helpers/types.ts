/**
 * Ocean Helper Types & Interfaces
 * Deterministic routing layer for Ocean-core
 */

export type Domain = 'math' | 'science' | 'reasoning' | 'language';

export interface HelperResult {
  domain: Domain;
  ok: boolean;
  answer: string;
  notes?: string;
  confidence?: 'high' | 'medium' | 'low';
}

export interface Helper {
  name: string;
  canHandle: (question: string) => boolean;
  handle: (question: string) => Promise<HelperResult>;
}

export interface HandleQuestionOptions {
  includeDebug?: boolean;
  maxRetries?: number;
  fallbackToReasoning?: boolean;
}
