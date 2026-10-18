import type { WebResearchPacket } from "./oceanResearch";

export interface DecisionSupport {
  mode: "responsibility-aware";
  requiresStructuredDecision: boolean;
  situationType: string;
  primaryRisks: string[];
  boundaries: string[];
  recommendedApproach: string[];
  answerStyle: string[];
}

const DECISION_PATTERNS = [
  /\b(decide|decision|should i|what should|best option|recommend|recommended|risk|safe|safely|responsibility|responsible|comply|compliance|legal|law|contract|policy|medical|clinical|finance|financial|investment|security|privacy)\b/i,
  /\b(vendim|vendos|duhet|çfare duhet|cfare duhet|opsioni me i mire|rrezik|sigurt|pergjegjesi|pergjegjshme|ligj|ligjor|mjekesor|shendet|financ|siguri|privatesi|pajtueshmeri)\b/i,
  /\b(entscheidung|soll ich|empfehlen|risiko|sicher|verantwortung|gesetz|rechtlich|medizinisch|finanz|sicherheit|datenschutz|compliance)\b/i,
];

function normalizeQuestion(question: string): string {
  return question.trim().toLowerCase();
}

export function shouldUseDecisionMode(question: string): boolean {
  const normalized = normalizeQuestion(question);
  if (!normalized) return false;
  return DECISION_PATTERNS.some((pattern) => pattern.test(normalized));
}

function detectSituationType(question: string): string {
  const normalized = normalizeQuestion(question);

  if (/medical|health|clinical|patient|mjek|shendet/i.test(normalized)) {
    return "medical-or-health";
  }
  if (/legal|law|contract|court|ligj|gjykat|kontrat/i.test(normalized)) {
    return "legal-or-compliance";
  }
  if (/finance|financial|investment|bank|tax|financ|tatim/i.test(normalized)) {
    return "financial";
  }
  if (/security|privacy|cyber|attack|threat|siguri|privates/i.test(normalized)) {
    return "security-or-privacy";
  }
  if (/strategy|business|market|roi|growth|biznes|treg/i.test(normalized)) {
    return "business-strategy";
  }

  return "general-high-responsibility";
}

function inferRisks(question: string): string[] {
  const normalized = normalizeQuestion(question);
  const risks = new Set<string>();

  if (/medical|health|clinical|patient|mjek|shendet/i.test(normalized)) {
    risks.add("Potential health harm if interpreted as diagnosis or treatment advice");
  }
  if (/legal|law|contract|court|ligj|gjykat|kontrat/i.test(normalized)) {
    risks.add("Jurisdiction-specific legal obligations may apply");
  }
  if (/finance|financial|investment|tax|financ|tatim/i.test(normalized)) {
    risks.add("Financial loss if assumptions are wrong or incomplete");
  }
  if (/security|privacy|cyber|attack|threat|siguri|privates/i.test(normalized)) {
    risks.add("Security or privacy exposure if guidance is implemented carelessly");
  }
  if (/latest|recent|current|today|sot|aktual|news|update/i.test(normalized)) {
    risks.add("Outdated information could lead to poor decisions");
  }

  if (risks.size === 0) {
    risks.add("Context may be incomplete, so assumptions should be checked before acting");
  }

  return Array.from(risks);
}

function inferBoundaries(question: string, researchPacket?: WebResearchPacket | null): string[] {
  const normalized = normalizeQuestion(question);
  const boundaries = new Set<string>([
    "Stay within legal, ethical, and safety boundaries",
    "Separate verified facts from inference and uncertainty",
  ]);

  if (/medical|health|clinical|patient|mjek|shendet/i.test(normalized)) {
    boundaries.add("Do not present the answer as a medical diagnosis or treatment order");
  }
  if (/legal|law|contract|court|ligj|gjykat|kontrat/i.test(normalized)) {
    boundaries.add("Do not present the answer as formal legal advice for a specific jurisdiction");
  }
  if (/finance|financial|investment|tax|financ|tatim/i.test(normalized)) {
    boundaries.add("Do not present the answer as personalized financial advice");
  }
  if (researchPacket?.active) {
    boundaries.add("Use current web evidence carefully and acknowledge possible source limitations");
  }

  return Array.from(boundaries);
}

function inferRecommendedApproach(
  question: string,
  researchPacket?: WebResearchPacket | null,
): string[] {
  const normalized = normalizeQuestion(question);
  const approach = new Set<string>([
    "Clarify the specific goal, constraints, and jurisdiction if relevant",
    "Choose the safest actionable path that remains useful",
  ]);

  if (researchPacket?.active) {
    approach.add("Cross-check the most relevant current sources before final action");
  }
  if (/medical|health|clinical|patient|mjek|shendet/i.test(normalized)) {
    approach.add("Escalate to a qualified clinician for diagnosis, prescription, or urgent symptoms");
  }
  if (/legal|law|contract|court|ligj|gjykat|kontrat/i.test(normalized)) {
    approach.add("Validate final decisions with a qualified local legal or compliance expert");
  }
  if (/finance|financial|investment|tax|financ|tatim/i.test(normalized)) {
    approach.add("Validate assumptions, numbers, and downside scenarios before committing funds");
  }
  if (/security|privacy|cyber|attack|threat|siguri|privates/i.test(normalized)) {
    approach.add("Apply changes in a controlled environment and verify access, logging, and rollback");
  }

  return Array.from(approach);
}

export function buildDecisionSupport(
  question: string,
  researchPacket?: WebResearchPacket | null,
): DecisionSupport | null {
  if (!shouldUseDecisionMode(question)) {
    return null;
  }

  return {
    mode: "responsibility-aware",
    requiresStructuredDecision: true,
    situationType: detectSituationType(question),
    primaryRisks: inferRisks(question),
    boundaries: inferBoundaries(question, researchPacket),
    recommendedApproach: inferRecommendedApproach(question, researchPacket),
    answerStyle: [
      "Direct answer first",
      "Short reasoning second",
      "Explicit risks and boundaries",
      "Practical next step plan",
    ],
  };
}

export function buildDecisionSystemMessage(
  question: string,
  support: DecisionSupport | null,
): string | null {
  if (!support) {
    return null;
  }

  return [
    "Decision-support mode is active.",
    `Question: ${question.trim()}`,
    `Situation type: ${support.situationType}`,
    `Primary risks: ${support.primaryRisks.join(" | ")}`,
    `Boundaries: ${support.boundaries.join(" | ")}`,
    `Recommended approach: ${support.recommendedApproach.join(" | ")}`,
    "Structure the answer naturally but make these elements clear: situation, risks, boundaries, recommended action.",
  ].join("\n");
}
