/**
 * Integration Guide - Ocean Helpers with Ocean Stream
 * Shows how to wire helpers into the existing Ocean stream endpoint
 */

import { handleQuestion, validateQuestion } from './oceanRouter';

/**
 * Example: Enhanced Ocean Stream with Helpers
 * Integrate into apps/web/app/api/ocean/stream/route.ts
 */

export async function integrateHelpersIntoOceanStream(userMessage: string) {
  // 1. Validate incoming message
  const { safe, reason } = validateQuestion(userMessage);
  if (!safe) {
    return {
      error: 'Validation failed',
      reason,
      blocked: true,
    };
  }

  // 2. Route through helpers first
  const helperResult = await handleQuestion(userMessage, { includeDebug: false });

  // 3. If helpers can fully answer, return immediately
  if (helperResult.ok && helperResult.domain !== 'reasoning') {
    return {
      source: 'helpers',
      domain: helperResult.domain,
      answer: helperResult.answer,
      notes: helperResult.notes,
      streaming: false,
    };
  }

  // 4. If reasoning-only, fall through to Ocean-core streaming
  // The existing /api/ocean/stream logic takes over
  return {
    source: 'ocean-core',
    handoff: true,
    helperNote: helperResult.answer, // Optional: show why we're deferring
  };
}

/**
 * Example: Middleware for Ocean stream endpoint
 *
 * Add to apps/web/app/api/ocean/stream/route.ts POST handler:
 *
 *   import { integrateHelpersIntoOceanStream } from '@/lib/helpers/integration';
 *
 *   export async function POST(req: NextRequest) {
 *     const { message } = await req.json();
 *
 *     // Try helpers first
 *     const helperResponse = await integrateHelpersIntoOceanStream(message);
 *
 *     if (helperResponse.source === 'helpers' && !helperResponse.streaming) {
 *       // Return single SSE chunk from helper
 *       return new NextResponse(
 *         makeSsePayload(helperResponse.answer) + makeDoneSsePayload(),
 *         { headers: sseHeaders() }
 *       );
 *     }
 *
 *     // Otherwise: continue with existing Ocean-core logic
 *     // ...rest of ocean stream implementation
 *   }
 */

/**
 * Example: Detect question type before routing
 */
export function detectQuestionType(question: string) {
  const types = {
    mathematical: /\d+\s*[\+\-\*\/]|\bsa\s+(është|bin)/i.test(question),
    scientific: /atom|ujë|fotosintez|adn|gravitet|elektrit/i.test(question),
    philosophical: /vetëdije|pse|qëllim|morale|realitet/i.test(question),
    creative: /shkruaj|imagjino|krijoni|përshkruaj/i.test(question),
  };

  return Object.fromEntries(
    Object.entries(types).map(([key, value]) => [key, value])
  );
}

/**
 * Example: Route selection logic
 */
export async function smartRoute(question: string) {
  const types = detectQuestionType(question);

  // If clearly mathematical or scientific, use helpers
  if (types.mathematical || types.scientific) {
    const result = await handleQuestion(question);
    if (result.ok) {
      return { route: 'helper', result };
    }
  }

  // Otherwise, use Ocean-core
  return { route: 'ocean-core' };
}

/**
 * Example: Batch helper + Ocean queries (hybrid approach)
 */
export async function hybridQuery(userQuery: string) {
  // Quick helper response
  const helperStart = Date.now();
  const helperResult = await handleQuestion(userQuery);
  const helperTime = Date.now() - helperStart;

  if (helperResult.ok && helperResult.domain !== 'reasoning') {
    // Helper solved it
    return {
      type: 'helper',
      time_ms: helperTime,
      answer: helperResult.answer,
    };
  }

  // Helper can't solve - also query Ocean-core in parallel
  // This gives users a hybrid response with both perspectives
  return {
    type: 'hybrid',
    helper_note: helperResult.answer,
    helper_time_ms: helperTime,
    ocean_message: userQuery, // Ready to stream from Ocean
  };
}

/**
 * Example: Error recovery with helpers
 * If Ocean-core fails, offer helper fallback
 */
export async function oceanStreamWithHelperFallback(question: string) {
  // Try to stream from Ocean-core
  try {
    // POST /api/ocean/stream logic here
    // If successful, return stream
  } catch (oceanError) {
    console.log('Ocean-core failed, falling back to helpers...');

    // Fallback to helpers
    const helperResult = await handleQuestion(question);
    if (helperResult.ok) {
      return {
        source: 'helper-fallback',
        reason: oceanError instanceof Error ? oceanError.message : 'Ocean unavailable',
        answer: helperResult.answer,
      };
    }

    // Both failed
    throw new Error('Neither Ocean nor Helpers could process the question');
  }
}

/**
 * Metrics: Track helper vs Ocean usage
 */
export class HelperMetrics {
  private static counts = {
    helperHits: 0,
    helperMisses: 0,
    oceanFallbacks: 0,
  };

  static recordHelperHit(domain: string) {
    this.counts.helperHits++;
    console.log(`[Metrics] Helper hit (${domain}): ${this.counts.helperHits} total`);
  }

  static recordHelperMiss(reason: string) {
    this.counts.helperMisses++;
    console.log(`[Metrics] Helper miss (${reason}): ${this.counts.helperMisses} total`);
  }

  static recordOceanFallback() {
    this.counts.oceanFallbacks++;
    console.log(`[Metrics] Ocean fallback: ${this.counts.oceanFallbacks} total`);
  }

  static getStats() {
    const total = this.counts.helperHits + this.counts.helperMisses;
    return {
      ...this.counts,
      total,
      helperSuccessRate: total > 0 ? (this.counts.helperHits / total) * 100 : 0,
    };
  }
}

/**
 * Example: Monitor helper performance
 */
export async function monitoredHandleQuestion(question: string) {
  const result = await handleQuestion(question);

  if (result.ok && result.domain !== 'reasoning') {
    HelperMetrics.recordHelperHit(result.domain);
  } else {
    HelperMetrics.recordHelperMiss(result.domain);
  }

  return result;
}
