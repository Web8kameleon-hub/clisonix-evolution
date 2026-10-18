/**
 * Ocean Helpers - Consolidated deterministic routing engine
 * Combined from multiple helper modules into a single accessible file
 * This lives in app/lib/ to avoid .gitignore restrictions on lib/
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type Domain = 'math' | 'science' | 'reasoning' | 'language';

export interface HelperResult {
  domain: Domain;
  ok: boolean;
  answer: string;
  notes?: string;
  confidence?: 'high' | 'medium' | 'low';
}

export interface HandleQuestionOptions {
  includeDebug?: boolean;
  maxRetries?: number;
  fallbackToReasoning?: boolean;
}

// ============================================================================
// MATH HELPER
// ============================================================================

function evaluateArithmetic(expression: string): string | null {
  try {
    const sanitized = expression.replace(/[^0-9+\-*/.().\s]/g, '');
    if (sanitized.includes('import') || sanitized.includes('require')) {
      return null;
    }
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

const MATH_PATTERNS = [
  /^\s*\d+\s*[\+\-\*×\/÷]\s*\d+/,
  /sa\s+?esh|sa\s+?bin|sa\s+?do\s+be/i,
  /zgjidh\s+(ekuacionin|sistemin)/i,
  /rrënja.*?katrore|√/i,
  /integral|derivat|limit/i,
  /përqindje|%|rritje|ulje/i,
  /faktor|shumëfish|pjestim/i,
];

const mathHelper = {
  canHandle(question: string): boolean {
    return MATH_PATTERNS.some((re) => re.test(question));
  },
  async handle(question: string): Promise<HelperResult> {
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

    if (/përqindje|%|rritje|ulje/i.test(question)) {
      return {
        domain: 'math',
        ok: true,
        confidence: 'medium',
        answer: 'Pyetja për përqindje/raport. MathHelper kërkon: numrin bazë, numrin e dytë dhe operacionin (rritje/ulje/raport).',
        notes: 'Duhet detaje numerike specifike për zgjidhje të saktë.',
      };
    }

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

// ============================================================================
// SCIENCE HELPER
// ============================================================================

const SCIENCE_KB: Record<string, { definition: string; details?: string }> = {
  atom: {
    definition: 'Atomi është njësia më e vogël e një elementi kimik që ruan vetitë e tij; përbëhet nga protonë, neutronë dhe elektrone.',
    details: 'Protoni dhe neutroni rrezidojnë në bërthamë; elektronet orbitojnë rreth saj.',
  },
  ujë: {
    definition: 'Uji (H₂O) është një komponim kimik i përbërë nga dy atome hidrogjeni dhe një atom oksigjeni.',
    details: 'Uji është zgjidhës universal, përgjegjës për të gjithë jetën në Tokë.',
  },
  gravitet: {
    definition: 'Graviteti është forca tërheqëse mes objekteve me masë; mban trupat në tokë dhe planetët në orbitë rreth Diellit.',
    details: 'Formula Njutoniane: F = G × (m₁ × m₂) / r².',
  },
  fotosinteza: {
    definition: 'Fotosinteza është procesi me të cilin bimët, algjet dhe disa baktere përdorin dritën Dielli, ujin dhe CO₂ për të prodhuar glukozë dhe oksigjen.',
    details: '6 CO₂ + 6 H₂O + drita → C₆H₁₂O₆ + 6 O₂.',
  },
  adn: {
    definition: 'ADN (acid deoksiribonukleik) është molekula që mban informacionin gjenetik të të gjithë organizmave të ndryshëm.',
    details: 'ADN përbëhet nga dy zinxhirë të lidhur, me baza: adeninë, timinën, guaninën dhe citosinën.',
  },
  elektrit: {
    definition: 'Elektriciteti është fenomeni fizik i lidhur me pranisë dhe rrjedhimin e elektroneve.',
    details: 'Tension = Rrymë × Rezistencë (V = I × R).',
  },
  magnetizem: {
    definition: 'Magnetizmi është vetia e disa materialeve që të tërheqin objekte të tjera ferrousha ose të ndërveprojnë me fusha magnetike.',
    details: 'Magnetët kanë pola pozitiv (+) dhe negativ (-); polat e kundërt tërhiqen, polat e njëjtë refuzohen.',
  },
  nxehtësi: {
    definition: 'Nxehtësia është forma e energjisë që transferohet ndërmjet sistemeve (ose brenda një sistemi) për shkak të dallimit të temperaturave.',
    details: 'Transferohet përmes përçueshmërisë, konvekcës ose rrezatimit.',
  },
  entropi: {
    definition: 'Entropia është masë e çrregullimit ose rastësinë në një sistem; rritet gjithmonë sipas ligjit të dytë të termodinamikës.',
    details: 'Në sisteme të izoluara, entropia nuk mund të zvogëlohet asnjëherë.',
  },
};

const SCIENCE_PATTERNS = [
  /atom|molekul|ion|elektron|proton|neutron/i,
  /ujë|uji|h2o|hidrogjen|oksigjeni/i,
  /gravitet|peshë|orkbitë|planet|yll|diell/i,
  /fotosintez|kloroplast|glukozë/i,
  /adn|arn|gene|kromo|mutacion/i,
  /elektrit|rrymë|tension|vat|amper/i,
  /magnetizem|pól magneti|ferromagnetizem/i,
  /nxehtësi|temperaturë|energji|kalori/i,
  /entropi|termodinamik|prill/i,
  /kimik|reaktiv|element|përbërje|formula/i,
  /fizik|mekanik|dinamik|kinematik/i,
];

const scienceHelper = {
  canHandle(question: string): boolean {
    return SCIENCE_PATTERNS.some((re) => re.test(question));
  },
  async handle(question: string): Promise<HelperResult> {
    const q = question.toLowerCase();

    for (const [key, content] of Object.entries(SCIENCE_KB)) {
      const keyNormalized = key.replace(/it$/, '').replace(/it$/, '');
      if (q.includes(key) || q.includes(keyNormalized)) {
        return {
          domain: 'science',
          ok: true,
          confidence: 'high',
          answer: content.definition,
          notes: content.details || undefined,
        };
      }
    }

    const keyWords = Object.keys(SCIENCE_KB);
    const foundKeyword = keyWords.find(
      (k) => q.includes(k) || q.includes(k.replace(/it$/, ''))
    );

    if (foundKeyword) {
      const content = SCIENCE_KB[foundKeyword];
      return {
        domain: 'science',
        ok: true,
        confidence: 'high',
        answer: content.definition,
        notes: content.details || undefined,
      };
    }

    return {
      domain: 'science',
      ok: true,
      confidence: 'low',
      answer: 'ScienceHelper: Njoh këtë lloj pyetjeje shkencore, por nuk kam përkufizim të saktë në bazën e njohurive.',
      notes: 'Kërkesa: zgjerimi i bazazës për më shumë terma shkencorë. Kontakto admin për përditësime.',
    };
  },
};

// ============================================================================
// REASONING HELPER
// ============================================================================

const reasoningHelper = {
  canHandle(_question: string): boolean {
    return true;
  },
  async handle(question: string): Promise<HelperResult> {
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

// ============================================================================
// MAIN ROUTER
// ============================================================================

const HELPERS = [mathHelper, scienceHelper, reasoningHelper];

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

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
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

      if (includeDebug) {
        if (!result.notes) {
          result.notes = '';
        }
        result.notes += `\n[DEBUG] Attempt: ${attempt + 1}/${maxRetries}`;
      }

      return result;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }
  }

  return {
    domain: 'reasoning',
    ok: false,
    answer: `Ocean Router: Gabim teknik gjatë përpunimit të pyetjes. ${lastError?.message || 'Nuk disponihet detale më specifike.'}`,
    confidence: 'low',
    notes: includeDebug ? `Error: ${lastError?.stack}` : undefined,
  };
}

export async function handleBatch(
  questions: string[],
  options: HandleQuestionOptions = {}
): Promise<HelperResult[]> {
  return Promise.all(questions.map((q) => handleQuestion(q, options)));
}

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

export function getHelperRegistry() {
  return {
    count: HELPERS.length,
    helpers: [
      { name: 'MathHelper', type: 'math' },
      { name: 'ScienceHelper', type: 'science' },
      { name: 'ReasoningHelper', type: 'reasoning' },
    ],
    supportedDomains: ['math', 'science', 'reasoning', 'language'],
    timestamp: new Date().toISOString(),
  };
}
