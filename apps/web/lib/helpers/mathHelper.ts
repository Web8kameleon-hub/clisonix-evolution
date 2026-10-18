/**
 * MathHelper - Deterministic mathematics without hallucinations
 * Handles: arithmetic, equations, basic algebra
 */

import { Helper, HelperResult } from './types';

// Simple safe arithmetic evaluator
function evaluateArithmetic(expression: string): string | null {
  try {
    // Only allow safe characters
    const sanitized = expression.replace(/[^0-9+\-*/.().\s]/g, '');

    // Prevent code injection via eval
    if (sanitized.includes('import') || sanitized.includes('require')) {
      return null;
    }

    // Use Function constructor with strict scope (safer than eval)
    const fn = new Function('return ' + sanitized);
    const result = fn();

    if (typeof result === 'number' && isFinite(result)) {
      return result.toString();
    }
    return null;
  } catch {
    return null;
  }
}

// Pattern matching for math questions
const MATH_PATTERNS = [
  /^\s*\d+\s*[\+\-\*×\/÷]\s*\d+/,                    // Basic arithmetic
  /sa\s+?esh|sa\s+?bin|sa\s+?do\s+be/i,              // "Sa është"
  /zgjidh\s+(ekuacionin|sistemin)/i,                 // "Zgjidh ekuacionin"
  /rrënja.*?katrore|√/i,                               // Square root
  /integral|derivat|limit/i,                          // Calculus
  /përqindje|%|rritje|ulje/i,                         // Percentages
  /faktor|shumëfish|pjestim/i,                        // Divisibility
];

export const MathHelper: Helper = {
  name: 'MathHelper',

  canHandle(question: string): boolean {
    return MATH_PATTERNS.some((re) => re.test(question));
  },

  async handle(question: string): Promise<HelperResult> {
    // Try simple arithmetic first
    const arithMatch = question.match(/\d+\s*[\+\-\*\/]\s*\d+/);
    if (arithMatch) {
      const result = evaluateArithmetic(arithMatch[0]);
      if (result) {
        return {
          domain: 'math',
          ok: true,
          confidence: 'high',
          answer: `${arithMatch[0]} = ${result}`,
          notes: 'Arithmetic evaluation (deterministic)',
        };
      }
    }

    // Check for percentage/ratio questions
    if (/përqindje|%|rritje|ulje/i.test(question)) {
      return {
        domain: 'math',
        ok: true,
        confidence: 'medium',
        answer: 'Pyetja për përqindje/raport. MathHelper kërkon: numrin bazë, numrin e dytë dhe operacionin (rritje/ulje/raport).',
        notes: 'Duhet detaje numerike specifike për zgjidhje të saktë.',
      };
    }

    // Equations & advanced math
    if (/ekuacion|sistem|formula/i.test(question)) {
      return {
        domain: 'math',
        ok: false,
        confidence: 'low',
        answer: 'MathHelper: Ekuacionet komplekse kërkojnë një motor simbolik (sympy / mathjs). Aktualisht vetëm aritmetika e thjeshtë është e gatshme.',
        notes: 'Përfshi koeficientët dhe shenjat në formatin standard ax+b=c.',
      };
    }

    return {
      domain: 'math',
      ok: false,
      confidence: 'low',
      answer: 'MathHelper: Nuk mund ta identifikova strukturën matematike të pyetjes.',
      notes: 'Përkrahe: aritmetika (27+56), përqindje (20% i 500), raportet (a:b).',
    };
  },
};
