export type ProcessingMode = "fast" | "deep";

export interface ComplexityProfile {
  mode: ProcessingMode;
  reason: string;
  shouldUseSignals: boolean;
  shouldUseResearch: boolean;
  shouldUseDecision: boolean;
}

const DEEP_PATTERNS = [
  /\b(why|how|analyze|analysis|architecture|design|strategy|compare|trade[- ]?off|root cause|diagnose|optimi[sz]e|research|evidence|cite|legal|medical|financial|security|compliance|risk|regulation|jurisdiction)\b/i,
  /\b(pse|si|analiz(?:e|a)?|arkitektur|strategji|krahaso|rrenje|diagnostik|optimiz|hulumtim|burim|ligj|mjek|financ|siguri|pajtueshmeri|rrezik)\b/i,
  /\b(deepthink|deep think|give me a plan|clear plan|action plan|roadmap|me jep nje plan|më jep një plan|plan te qarte|plan të qartë|plan veprimi|gib mir einen klaren plan|klaren plan|aktionsplan|fahrplan)\b/i,
];

const FAST_PATTERNS = [
  /^(hi|hello|hey|ok|okay|yes|no|thanks|thank you|continue|go ahead|do it|status|ping)$/i,
  /^(pershendetje|tung|ok|po|jo|faleminderit|vazhdo|beje|status|ping)$/i,
];

export function detectProcessingMode(
  question: string,
  requested?: unknown,
): ComplexityProfile {
  const requestedNormalized =
    typeof requested === "string" ? requested.trim().toLowerCase() : "";

  if (requestedNormalized === "fast") {
    return {
      mode: "fast",
      reason: "user-requested-fast",
      shouldUseSignals: false,
      shouldUseResearch: false,
      shouldUseDecision: false,
    };
  }

  if (requestedNormalized === "deep") {
    return {
      mode: "deep",
      reason: "user-requested-deep",
      shouldUseSignals: true,
      shouldUseResearch: true,
      shouldUseDecision: true,
    };
  }

  const clean = question.trim();
  if (!clean) {
    return {
      mode: "fast",
      reason: "empty-or-short",
      shouldUseSignals: false,
      shouldUseResearch: false,
      shouldUseDecision: false,
    };
  }

  const isShort = clean.length <= 80;
  const isFastPattern = FAST_PATTERNS.some((pattern) => pattern.test(clean));
  // JavaScript word boundaries are ASCII-based; normalize Albanian accents
  // before matching phrases ending in ë (for example "plan të qartë").
  const normalized = clean.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const isDeepPattern = DEEP_PATTERNS.some((pattern) => pattern.test(normalized));

  if (isDeepPattern || clean.length > 220) {
    return {
      mode: "deep",
      reason: isDeepPattern ? "deep-pattern" : "long-query",
      shouldUseSignals: true,
      shouldUseResearch: true,
      shouldUseDecision: true,
    };
  }

  if (isShort || isFastPattern) {
    return {
      mode: "fast",
      reason: isFastPattern ? "fast-pattern" : "short-query",
      shouldUseSignals: false,
      shouldUseResearch: false,
      shouldUseDecision: false,
    };
  }

  return {
    mode: "deep",
    reason: "default-balanced",
    shouldUseSignals: true,
    shouldUseResearch: true,
    shouldUseDecision: true,
  };
}
