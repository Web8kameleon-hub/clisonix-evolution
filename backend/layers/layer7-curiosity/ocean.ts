import { signalPush, nodeInfo } from "../_shared/signal";

const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL || "http://clisonix-ocean-core:8030";

export interface CuriosityQuery {
  question: string;
  domain: string;
  priority: "low" | "normal" | "high" | "urgent";
  timestamp: string;
  status: "exploring" | "completed" | "archived";
  insights?: string[];
  related_queries?: string[];
}

export interface ExplorationResult {
  answer?: string;
  confidence: number;
  sources: string[];
  follow_up_questions: string[];
  philosophical_depth: number;
}

let explorations: CuriosityQuery[] = [];
let isExploring = false;

export function initCuriosityEngine() {
  explorations = [];
  console.log("[Curiosity Ocean] Deep exploration engine initialized");

  // Start background curiosity process
  setInterval(backgroundExploration, 30000); // Every 30 seconds
}

export async function askCuriosity(
  query: CuriosityQuery,
): Promise<ExplorationResult> {
  // Add to explorations queue
  explorations.push(query);

  // Keep only last 1000 explorations
  if (explorations.length > 1000) {
    explorations = explorations.slice(-1000);
  }

  // Real Ocean Core response (0 fake answers)
  const ocean = await queryOceanCore(query.question);

  const result: ExplorationResult = {
    confidence: ocean.confidence,
    sources: ocean.sources,
    follow_up_questions: generateFollowUpQuestions(query.question),
    philosophical_depth: calculatePhilosophicalDepth(query.question),
    answer: ocean.answer,
  };

  // Mark query as completed
  query.status = "completed";
  query.insights = extractInsights(result);

  return result;
}

export function getExplorations(): CuriosityQuery[] {
  return explorations.slice(); // Return copy
}

async function generateCuriousAnswer(
  question: string,
  domain: string,
): Promise<string> {
  const ocean = await queryOceanCore(question);
  return ocean.answer;
}

async function queryOceanCore(
  question: string,
): Promise<{ answer: string; confidence: number; sources: string[] }> {
  const language = detectLanguageFromText(question);

  const response = await fetch(`${OCEAN_CORE_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: question,
      language,
      messages: [{ role: "user", content: question }],
    }),
  });

  if (!response.ok) {
    throw new Error(`Ocean Core error ${response.status}`);
  }

  const payload = await response.json();
  const answer = String(payload?.response || payload?.answer || "").trim();
  const sources = Array.isArray(payload?.sources)
    ? payload.sources.map((s: unknown) => String(s))
    : ["ocean-core"];
  const confidenceRaw = Number(payload?.confidence);
  const confidence = Number.isFinite(confidenceRaw) ? confidenceRaw : 0.82;

  if (!answer) {
    throw new Error("Ocean Core returned an empty response");
  }

  return {
    answer,
    confidence,
    sources,
  };
}

function generateFollowUpQuestions(originalQuestion: string): string[] {
  const normalized = originalQuestion.trim();
  const followUps = [
    `Can you expand this with concrete examples related to: ${normalized}?`,
    "What evidence supports this answer?",
    "What are practical next steps?",
  ];

  return followUps;
}

function calculatePhilosophicalDepth(question: string): number {
  // Simple heuristic for philosophical depth
  const deepWords = [
    "consciousness",
    "meaning",
    "existence",
    "reality",
    "being",
    "mind",
    "soul",
    "purpose",
  ];
  const wordCount = deepWords.filter((word) =>
    question.toLowerCase().includes(word),
  ).length;
  return Math.min(10, Math.max(1, wordCount * 2 + 2));
}

function extractInsights(result: ExplorationResult): string[] {
  const answer = (result.answer || "").trim();
  if (!answer) {
    return [];
  }
  const chunks = answer
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, 3);
  return chunks.length ? chunks : [answer.slice(0, 180)];
}

function detectLanguageFromText(text: string): string {
  const t = text.toLowerCase();
  if (/[\u4e00-\u9fff]/.test(text)) return "zh";
  if (/[\u3040-\u30ff]/.test(text)) return "ja";
  if (/[\uac00-\ud7af]/.test(text)) return "ko";
  if (/[\u0370-\u03ff]/.test(text)) return "el";
  if (/[\u0590-\u05ff]/.test(text)) return "he";
  if (/[\u0600-\u06ff]/.test(text)) return "ar";
  if (/\b(guten|hallo|danke|bitte|tschüss|wie|ist)\b/i.test(t)) return "de";
  if (
    /\b(përshëndetje|pershendetje|mirëdita|faleminderit|çfarë|është)\b/i.test(t)
  )
    return "sq";
  if (/\b(hola|gracias|buenos|adiós|cómo)\b/i.test(t)) return "es";
  if (/\b(bonjour|merci|salut|comment)\b/i.test(t)) return "fr";
  if (/\b(ciao|grazie|buongiorno|come)\b/i.test(t)) return "it";
  if (/\b(merhaba|teşekkür|nasılsın)\b/i.test(t)) return "tr";
  return "en";
}

async function backgroundExploration() {
  if (isExploring) return;

  isExploring = true;

  try {
    // Generate spontaneous curiosity
    const spontaneousQuestions = [
      "What is the relationship between complexity and consciousness?",
      "How do emergent properties arise from simple interactions?",
      "What role does information integration play in awareness?",
      "How might artificial systems develop genuine understanding?"
    ];

    if (Math.random() < 0.1) { // 10% chance every 30 seconds
      const question = spontaneousQuestions[Math.floor(Math.random() * spontaneousQuestions.length)];

      try {
        await askCuriosity({
          question,
          domain: "philosophy",
          priority: "low",
          timestamp: new Date().toISOString(),
          status: "exploring",
        });
      } catch (error) {
        console.warn(
          "[Curiosity Ocean] Background exploration skipped:",
          error,
        );
      }
    }
  } finally {
    isExploring = false;
  }
}
