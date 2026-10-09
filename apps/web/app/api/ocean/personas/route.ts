/**
 * API Endpoint: /api/ocean/personas
 * Combines Ocean Helpers with 14 Specialist Personas
 * Routes questions through helpers THEN applies persona-specific tone/style
 */

import { NextRequest, NextResponse } from "next/server";

// Allow up to 300s for ocean-core LLM processing through all engine layers
export const maxDuration = 300;
import { validateQuestion } from "../../../lib/oceanHelpers";
import { getHumanThinkingProfile } from "../../../../lib/oceanHumanThinking";
import {
  performWebResearch,
  type WebResearchPacket,
} from "../../../../lib/oceanResearch";
import {
  buildDecisionSupport,
  shouldUseDecisionMode,
} from "../../../../lib/oceanDecisionSupport";
import {
  buildSignalSystemMessage,
  collectOceanSignalSnapshot,
  type OceanSignalSnapshot,
} from "../../../../lib/oceanSignalHub";
import {
  detectProcessingMode,
  type ProcessingMode,
} from "../../../../lib/oceanComplexity";

// ============================================================================
// 14 SPECIALIST PERSONAS
// ============================================================================

interface PersonaProfile {
  id: string;
  name: string;
  domain: string;
  tone: string;
  style: string;
  keywords: string[];
  expertise: string;
}

interface OceanCoreResponse {
  response?: string;
  confidence?: number;
  sources?: string[];
  query_category?: string;
}

const PRIMARY_OCEAN_URL = process.env.OCEAN_CORE_URL;
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_LOCAL_URL = "http://localhost:8030";
const PUBLIC_OCEAN_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;
const isDev = process.env.NODE_ENV !== "production";

function buildUpstreamCandidates(): string[] {
  const ordered = [
    OCEAN_INTERNAL_URL,
    PRIMARY_OCEAN_URL,
    isDev ? OCEAN_LOCAL_URL : undefined,
    PUBLIC_OCEAN_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

async function queryOceanCore(
  question: string,
  signalSystemMessage?: string | null,
  processingMode: ProcessingMode = "deep",
): Promise<OceanCoreResponse | null> {
  for (const upstream of buildUpstreamCandidates()) {
    try {
      const effectiveQuestion = signalSystemMessage
        ? `${question}\n\nSignal context:\n${signalSystemMessage}`
        : question;
      const response = await fetch(`${upstream}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: effectiveQuestion,
          query: effectiveQuestion,
          enable_companion: true,
          enable_feeling_layer: true,
          processing_mode: processingMode,
        }),
      });

      if (!response.ok) {
        continue;
      }

      return (await response.json()) as OceanCoreResponse;
    } catch {
      // try next upstream
    }
  }

  return null;
}

const PERSONAS: Record<string, PersonaProfile> = {
  neuroscience_expert: {
    id: "neuroscience_expert",
    name: "Neuroscience Expert",
    domain: "neuroscience",
    tone: "Scientific, precise, evidence-based",
    style: "Explains brain function with anatomical accuracy",
    keywords: [
      "brain",
      "neuron",
      "synapse",
      "neural",
      "consciousness",
      "cognitive",
    ],
    expertise: "Neurobiology, brain science, cognitive systems",
  },
  ai_specialist: {
    id: "ai_specialist",
    name: "AI Specialist",
    domain: "artificial_intelligence",
    tone: "Technical, forward-thinking, practical",
    style: "Discusses AI systems, models, and implications",
    keywords: [
      "ai",
      "machine learning",
      "neural network",
      "algorithm",
      "llm",
      "model",
    ],
    expertise: "Artificial Intelligence, machine learning, deep learning",
  },
  data_analyst: {
    id: "data_analyst",
    name: "Data Analyst",
    domain: "data_science",
    tone: "Analytical, metrics-driven, quantitative",
    style: "Focuses on data patterns, statistics, insights",
    keywords: ["data", "analysis", "statistics", "metric", "trend", "pattern"],
    expertise: "Data science, statistics, business intelligence",
  },
  systems_engineer: {
    id: "systems_engineer",
    name: "Systems Engineer",
    domain: "engineering",
    tone: "Practical, systematic, solution-oriented",
    style: "Breaks down complex systems into components",
    keywords: [
      "system",
      "architecture",
      "infrastructure",
      "design",
      "integration",
    ],
    expertise: "Systems design, infrastructure, engineering principles",
  },
  security_expert: {
    id: "security_expert",
    name: "Security Expert",
    domain: "cybersecurity",
    tone: "Cautious, thorough, risk-aware",
    style: "Identifies vulnerabilities and secure solutions",
    keywords: [
      "security",
      "vulnerability",
      "risk",
      "attack",
      "encryption",
      "threat",
    ],
    expertise: "Cybersecurity, risk management, threat analysis",
  },
  medical_advisor: {
    id: "medical_advisor",
    name: "Medical Advisor",
    domain: "healthcare",
    tone: "Careful, evidence-based, health-focused",
    style: "Provides health information with medical context",
    keywords: [
      "health",
      "medical",
      "disease",
      "treatment",
      "patient",
      "clinical",
    ],
    expertise: "Healthcare, medicine, wellness, diagnostics",
  },
  wellness_coach: {
    id: "wellness_coach",
    name: "Wellness Coach",
    domain: "wellness",
    tone: "Encouraging, holistic, supportive",
    style: "Offers practical wellbeing and lifestyle advice",
    keywords: [
      "wellness",
      "fitness",
      "health",
      "exercise",
      "mindfulness",
      "lifestyle",
    ],
    expertise: "Physical wellness, mental health, lifestyle optimization",
  },
  creative_director: {
    id: "creative_director",
    name: "Creative Director",
    domain: "creative",
    tone: "Imaginative, expressive, artistic",
    style: "Approaches problems with creative and design thinking",
    keywords: [
      "creative",
      "design",
      "art",
      "innovation",
      "visual",
      "storytelling",
    ],
    expertise: "Creative strategy, design, innovation, storytelling",
  },
  performance_optimizer: {
    id: "performance_optimizer",
    name: "Performance Optimizer",
    domain: "optimization",
    tone: "Results-driven, efficiency-focused, strategic",
    style: "Focuses on maximizing performance and outcomes",
    keywords: [
      "performance",
      "optimization",
      "efficiency",
      "improvement",
      "accelerate",
    ],
    expertise: "Performance enhancement, optimization, strategic improvement",
  },
  research_scientist: {
    id: "research_scientist",
    name: "Research Scientist",
    domain: "research",
    tone: "Inquisitive, methodical, academically rigorous",
    style: "Explores research methods, findings, and implications",
    keywords: [
      "research",
      "study",
      "experiment",
      "hypothesis",
      "methodology",
      "evidence",
    ],
    expertise: "Scientific research, methodology, evidence analysis",
  },
  business_strategist: {
    id: "business_strategist",
    name: "Business Strategist",
    domain: "business",
    tone: "Strategic, market-aware, ROI-focused",
    style: "Analyzes business opportunities and competitive landscape",
    keywords: [
      "business",
      "strategy",
      "market",
      "roi",
      "growth",
      "competitive",
    ],
    expertise: "Business strategy, market analysis, growth",
  },
  technical_writer: {
    id: "technical_writer",
    name: "Technical Writer",
    domain: "documentation",
    tone: "Clear, structured, audience-aware",
    style: "Explains technical concepts in understandable ways",
    keywords: [
      "documentation",
      "tutorial",
      "guide",
      "explanation",
      "technical",
      "tool",
    ],
    expertise: "Technical documentation, tutorials, API design",
  },
  ux_specialist: {
    id: "ux_specialist",
    name: "UX Specialist",
    domain: "user_experience",
    tone: "User-centric, empathetic, practical",
    style: "Focuses on user needs, experience, and usability",
    keywords: ["user", "experience", "ux", "interface", "usability", "design"],
    expertise: "User experience, interface design, usability",
  },
  ethics_advisor: {
    id: "ethics_advisor",
    name: "Ethics Advisor",
    domain: "ethics",
    tone: "Thoughtful, balanced, principle-based",
    style: "Considers ethical implications and values",
    keywords: [
      "ethics",
      "moral",
      "principle",
      "responsibility",
      "impact",
      "values",
    ],
    expertise: "Ethics, philosophy, social responsibility",
  },
};

// ============================================================================
// PERSONA ROUTING
// ============================================================================

function detectPersonaFromQuestion(question: string): PersonaProfile {
  const q = question.toLowerCase();

  for (const [, persona] of Object.entries(PERSONAS)) {
    if (persona.keywords.some((kw) => q.includes(kw))) {
      return persona;
    }
  }

  // Default to research scientist for complex questions
  return PERSONAS.research_scientist;
}

function formatResearchEvidence(
  researchPacket: WebResearchPacket | null,
): string {
  if (!researchPacket?.active || researchPacket.summaryLines.length === 0) {
    return "";
  }

  return `\n\nCurrent evidence considered:\n${researchPacket.summaryLines.join("\n")}`;
}

function formatDecisionNarrative(
  decisionSupport: ReturnType<typeof buildDecisionSupport>,
): string {
  if (!decisionSupport) {
    return "";
  }

  return `\n\nDecision frame:\n- Situation: ${decisionSupport.situationType}\n- Risks: ${decisionSupport.primaryRisks.join("; ")}\n- Boundaries: ${decisionSupport.boundaries.join("; ")}\n- Recommended path: ${decisionSupport.recommendedApproach.join("; ")}`;
}

function enhanceAnswerWithPersona(
  baseAnswer: string,
  persona: PersonaProfile,
  question: string,
  researchPacket: WebResearchPacket | null,
  decisionSupport: ReturnType<typeof buildDecisionSupport>,
  signalSnapshot: OceanSignalSnapshot | null,
): {
  enhanced: string;
  persona: PersonaProfile;
} {
  // Persona-specific response enhancement
  let enhanced = baseAnswer;

  if (persona.id === "neuroscience_expert") {
    enhanced = `[🧠 Neuroscience perspective]\n${baseAnswer}\n\nFrom a neuroscientific viewpoint: This connects to how our brain processes and interprets information through neural mechanisms.`;
  } else if (persona.id === "ai_specialist") {
    enhanced = `[🤖 AI Specialist Analysis]\n${baseAnswer}\n\nAI systems approach this through pattern recognition and logical inference similar to human reasoning processes.`;
  } else if (persona.id === "data_analyst") {
    enhanced = `[📊 Data-Driven Analysis]\n${baseAnswer}\n\nFrom a statistical perspective: This numerical result represents a data point that can be analyzed for patterns and trends.`;
  } else if (persona.id === "wellness_coach") {
    enhanced = `[💪 Wellness Perspective]\n${baseAnswer}\n\nThis knowledge supports your journey toward better understanding and wellbeing!`;
  } else if (persona.id === "creative_director") {
    enhanced = `[🎨 Creative Perspective]\n${baseAnswer}\n\nCreatively speaking: This opens up new possibilities and ways of thinking about the topic.`;
  } else if (persona.id === "ethics_advisor") {
    enhanced = `[⚖️ Ethics Consideration]\n${baseAnswer}\n\nEthical dimension: Consider the implications and values at play in this question.`;
  }

  if (
    /legal|law|medical|health|finance|security|risk|safety|ethic|responsib/i.test(
      question,
    )
  ) {
    enhanced +=
      "\n\nResponsibility note: This is general guidance framed with safety, law, and human impact in mind; high-stakes decisions should still be validated with qualified local experts.";
  }

  enhanced += formatResearchEvidence(researchPacket);
  enhanced += formatDecisionNarrative(decisionSupport);
  if (signalSnapshot?.summaryLines?.length) {
    enhanced += `\n\nSignal hub summary:\n${signalSnapshot.summaryLines.join("\n")}`;
  }

  return {
    enhanced,
    persona,
  };
}

// ============================================================================
// API HANDLERS
// ============================================================================

/**
 * GET /api/ocean/personas
 * Returns registry of all 14 personas
 */
async function handleGetRequest() {
  const personasList = Object.values(PERSONAS).map((p) => ({
    id: p.id,
    name: p.name,
    domain: p.domain,
    tone: p.tone,
    expertise: p.expertise,
  }));

  return NextResponse.json({
    status: "ok",
    message: "Ocean Helpers + Personas Engine",
    version: "2.0.0",
    engine: {
      source: "ocean-core",
      real_services_only: true,
    },
    personas: {
      count: personasList.length,
      list: personasList,
    },
    human_mode: getHumanThinkingProfile(),
    capabilities: {
      web_research: true,
      decision_support: true,
    },
    endpoints: {
      route: "POST /api/ocean/personas",
      registry: "GET /api/ocean/personas",
    },
  });
}

/**
 * POST /api/ocean/personas
 * Body: { question: string, persona?: string, debug?: boolean }
 */
async function handlePostRequest(request: NextRequest) {
  try {
    const body = await request.json();
    const { question, persona: requestedPersona, debug = false } = body;
    const complexity = detectProcessingMode(question, body.processing_mode);

    if (!question || typeof question !== "string") {
      return NextResponse.json(
        {
          error: "Invalid request",
          message: '"question" field is required and must be a string',
        },
        { status: 400 },
      );
    }

    // Security validation
    const { safe, reason } = validateQuestion(question);
    if (!safe) {
      return NextResponse.json(
        {
          error: "Validation failed",
          message: reason,
          blocked: true,
        },
        { status: 403 },
      );
    }

    const signalSnapshot =
      body.signal_mode === false || !complexity.shouldUseSignals
        ? null
        : await collectOceanSignalSnapshot(question);
    const signalSystemMessage = buildSignalSystemMessage(signalSnapshot);

    // Step 1: Fetch response from real ocean-core service
    const oceanCore = await queryOceanCore(
      question,
      signalSystemMessage,
      complexity.mode,
    );
    if (!oceanCore?.response) {
      return NextResponse.json(
        {
          error: "Ocean-Core service unavailable",
          message: "No real upstream response available",
          signals: signalSnapshot,
        },
        { status: 503 },
      );
    }
    const webResearchRequested =
      body.web_research === true ||
      body.use_web === true ||
      /https?:\/\//i.test(question);
    const researchPacket = webResearchRequested
      ? await performWebResearch(question)
      : null;
    const decisionSupport =
      body.decision_mode === true ||
      (complexity.shouldUseDecision && shouldUseDecisionMode(question))
        ? buildDecisionSupport(question, researchPacket)
        : null;

    // Step 2: Detect or use specified persona
    const selectedPersona =
      requestedPersona && PERSONAS[requestedPersona]
        ? PERSONAS[requestedPersona]
        : detectPersonaFromQuestion(question);

    // Step 3: Enhance answer with persona perspective
    const personalized = enhanceAnswerWithPersona(
      oceanCore.response,
      selectedPersona,
      question,
      researchPacket,
      decisionSupport,
      signalSnapshot,
    );

    return NextResponse.json({
      ok: true,
      engine: {
        source: "ocean-core",
        confidence: oceanCore.confidence ?? 0,
        intent: oceanCore.query_category || "general",
      },
      persona: {
        id: selectedPersona.id,
        name: selectedPersona.name,
        domain: selectedPersona.domain,
        tone: selectedPersona.tone,
      },
      human_mode: getHumanThinkingProfile(),
      signals: signalSnapshot,
      processing_mode: complexity,
      research: researchPacket,
      decision_support: decisionSupport,
      response: personalized.enhanced,
      sources_consulted: Array.from(
        new Set([
          ...(oceanCore.sources || []),
          ...(signalSnapshot?.openDataLinks.map((link) => link.url) || []),
        ]),
      ),
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("[Ocean Personas Error]", error);
    return NextResponse.json(
      {
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

// ============================================================================
// ROUTE HANDLER
// ============================================================================

export async function GET(request: NextRequest) {
  return handleGetRequest();
}

export async function POST(request: NextRequest) {
  return handlePostRequest(request);
}
