/**
 * ReasoningHelper - Complex reasoning fallback to Ocean-core
 * Routes questions that need LLM reasoning to the main Ocean engine
 */

import { Helper, HelperResult } from './types';

export const ReasoningHelper: Helper = {
  name: 'ReasoningHelper',

  canHandle(_question: string): boolean {
    // This is the catch-all helper - always returns true
    // It acts as the last resort fallback
    return true;
  },

  async handle(question: string): Promise<HelperResult> {
    // This helper acknowledges that the question needs reasoning from Ocean-core
    // In a real deployment, this would contact Ocean-core via /api/ocean/stream
    // and stream the response back to the user

    const isPhilosophic = /vetëdije|kestetimi|qëllim|morale|etik|përse|pse pse|fakt|realitet|shpresa/i.test(
      question
    );
    const isComplex = /si|pse|kur|ku|çfarë|kush|cili|cilat|shkak|pasojë|lidhje/i.test(
      question
    );
    const isCreative =
      /shkruaj|krijoni|imagjino|sugjerime|ide|përmbledhje|krahasim|analogji/i.test(
        question
      );

    let confidence: 'high' | 'medium' | 'low' = 'medium';
    let notes = '';

    if (isPhilosophic) {
      confidence = 'medium';
      notes = 'Pyetje filozofike - Ocean-core do të përdorë logjikë dhe argumentim.';
    } else if (isComplex) {
      confidence = 'medium';
      notes = 'Pyetje komplekse - kërkeson analiza shumë-shtresore.';
    } else if (isCreative) {
      confidence = 'low';
      notes = 'Pyetje krijuese - rezultati varet nga modeli LLM të disponueshëm.';
    }

    return {
      domain: 'reasoning',
      ok: true,
      confidence,
      answer: `ReasoningHelper → Ocean-core\n\nPyetja juaj do të trajtohet nga motori kryesor i Ocean-it, i cili përdor logjikë dhe arsyetim:\n\n"${question}"\n\nAgjenti do të harxhojë disa instante komplekse për të arritur në përgjigje të mirë.`,
      notes,
    };
  },
};
