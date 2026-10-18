/**
 * Ocean Router - Coordinates all helpers for deterministic question handling
 * Prevents hallucinations by routing to specialized engines before falling back to reasoning
 */

import { Helper, HelperResult, HandleQuestionOptions } from './types';
import { MathHelper } from './mathHelper';
import { ScienceHelper } from './scienceHelper';
import { ReasoningHelper } from './reasoningHelper';

const HELPERS: Helper[] = [
  MathHelper,
  ScienceHelper,
  ReasoningHelper, // Always last (catch-all)
];

/**
 * Main entry point: handles a question by routing to appropriate helper
 */
export async function handleQuestion(
  question: string,
  options: HandleQuestionOptions = {}
): Promise<HelperResult> {
  const {
    includeDebug = false,
    maxRetries = 1,
    fallbackToReasoning = true,
  } = options;

  if (!question || question.trim().length === 0) {
    return {
      domain: 'reasoning',
      ok: false,
      answer: 'Ocean Router: Pyetja është e zbrazët. Ju lutemi jepni një pyetje konkrete.',
      confidence: 'high',
    };
  }

  let lastError: Error | null = null;

  // Attempt to find and use an appropriate helper
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      // Find first helper that claims to handle this question
      const selectedHelper = HELPERS.find((h) => h.canHandle(question));

      if (!selectedHelper) {
        return {
          domain: 'reasoning',
          ok: false,
          answer: 'Ocean Router: Asnjë helper nuk e mori përsipër këtë pyetje.',
          confidence: 'low',
        };
      }

      const result = await selectedHelper.handle(question);

      // Debug info (if requested)
      if (includeDebug) {
        if (!result.notes) {
          result.notes = '';
        }
        result.notes += `\n[DEBUG] Helper: ${selectedHelper.name} | Attempt: ${attempt + 1}/${maxRetries}`;
      }

      return result;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      // Retry on failure
      if (attempt < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, 100)); // Small delay
      }
    }
  }

  // Final fallback: return error state
  return {
    domain: 'reasoning',
    ok: false,
    answer: `Ocean Router: Gabim teknik gjatë përpunimit të pyetjes. ${lastError?.message || 'Nuk disponihet detale më specifike.'}`,
    confidence: 'low',
    notes: includeDebug ? `Error: ${lastError?.stack}` : undefined,
  };
}

/**
 * Batch process multiple questions
 */
export async function handleBatch(
  questions: string[],
  options: HandleQuestionOptions = {}
): Promise<HelperResult[]> {
  return Promise.all(questions.map((q) => handleQuestion(q, options)));
}

/**
 * Stream helper results (integrates with Ocean stream endpoint)
 * Yields results in SSE-compatible format
 */
export async function* handleQuestionStream(
  question: string,
  options: HandleQuestionOptions = {}
) {
  try {
    const result = await handleQuestion(question, options);
    yield result;

    // If ReasoningHelper was selected and fallback is enabled,
    // could yield streaming chunks from Ocean-core here
    if (result.domain === 'reasoning' && result.ok) {
      yield {
        domain: 'reasoning' as const,
        ok: true,
        answer: '[Stream initiated to Ocean-core...]',
        confidence: 'medium' as const,
      };
    }
  } catch (error) {
    yield {
      domain: 'reasoning' as const,
      ok: false,
      answer: `Stream error: ${error instanceof Error ? error.message : String(error)}`,
      confidence: 'low' as const,
    };
  }
}

/**
 * Get diagnostic info about all registered helpers
 */
export function getHelperRegistry() {
  return {
    count: HELPERS.length,
    helpers: HELPERS.map((h) => ({
      name: h.name,
      type: h.name.replace('Helper', '').toLowerCase(),
    })),
    supportedDomains: ['math', 'science', 'reasoning', 'language'],
    timestamp: new Date().toISOString(),
  };
}

/**
 * Validate question safety (prevents injection/jailbreak)
 */
export function validateQuestion(question: string): {
  safe: boolean;
  reason?: string;
} {
  const maxLength = 2000;
  const suspiciousPatterns = [
    /sql|injection|<script|eval|exec|system|shell/i,
    /ignore.*?instructions|bypass|override/i,
  ];

  if (question.length > maxLength) {
    return {
      safe: false,
      reason: `Pyetja tejkalon gjatësinë maksimale (${maxLength} karaktere).`,
    };
  }

  if (suspiciousPatterns.some((p) => p.test(question))) {
    return {
      safe: false,
      reason: 'Pyetja përmban modele të dyshimta. Për arsye sigurie, u refuzua.',
    };
  }

  return { safe: true };
}

/**
 * Integration helper: Convert Ocean stream format to helper format
 */
export function adaptOceanStreamResult(
  oceanResponse: any
): HelperResult {
  return {
    domain: 'reasoning',
    ok: !!oceanResponse.success,
    answer: oceanResponse.answer || oceanResponse.message || 'Nuk u mor përgjigje.',
    confidence: oceanResponse.confidence || 'medium',
    notes: oceanResponse.metadata ? JSON.stringify(oceanResponse.metadata) : undefined,
  };
}
