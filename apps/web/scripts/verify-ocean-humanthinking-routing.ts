import fs from "node:fs";
import path from "node:path";
import { detectProcessingMode } from "../lib/oceanComplexity.ts";
import { buildHumanThinkingSystemPrompt } from "../lib/oceanHumanThinking.ts";

const root = path.resolve(import.meta.dirname, "..");
const read = (relative: string) => fs.readFileSync(path.join(root, relative), "utf8");
const route = read("app/api/ocean/route.ts");
const stream = read("app/api/ocean/stream/route.ts");

let passed = 0;
const failures: string[] = [];
function check(name: string, condition: boolean) {
  if (condition) passed += 1;
  else failures.push(name);
}

const deepCases = [
  "deepthink",
  "deep think about this architecture",
  "give me a plan",
  "clear plan for deployment",
  "action plan for recovery",
  "roadmap for Ocean",
  "më jep një plan",
  "plan të qartë për prodhim",
  "plan te qarte per prodhim",
  "plan veprimi",
  "gib mir einen klaren plan",
  "klaren plan",
  "aktionsplan",
  "fahrplan",
  "analyze the architecture",
  "security risk analysis",
  "legal compliance analysis",
  "research evidence",
  "pse kjo arkitekturë dështon",
  "analizë e thellë e sistemit",
];
for (const input of deepCases) {
  check(`deep: ${input}`, detectProcessingMode(input).mode === "deep");
}

const fastCases = [
  "hello",
  "hi",
  "ok",
  "thanks",
  "ping",
  "status",
  "2+2",
  "po",
  "jo",
  "test",
];
for (const input of fastCases) {
  check(`fast: ${input}`, detectProcessingMode(input).mode === "fast");
}

check("explicit fast remains fast", detectProcessingMode("deepthink", "fast").mode === "fast");
check("explicit deep remains deep", detectProcessingMode("hello", "deep").mode === "deep");
check("unsupported balanced request follows canonical detector", detectProcessingMode("hello", "balanced").mode === "fast");

const sqPrompt = buildHumanThinkingSystemPrompt("sq");
check("SQ prompt has adaptive depth", sqPrompt.includes("Përshtat gjatësinë dhe thellësinë"));
check("SQ prompt has no 2-4 sentence cap", !sqPrompt.includes("2-4 fjali"));
check("prompt requires grounded reality", sqPrompt.includes("Mos shpik"));
check("prompt requires uncertainty disclosure", sqPrompt.includes("thuaje qartë"));
check("prompt requires evidence hierarchy", sqPrompt.includes("hierarki evidence"));
check("prompt requires limitations", sqPrompt.includes("kufizimet"));

const forbiddenRoute = [
  "wantsFastHumanThinkingPlan",
  "forceHumanThinkingFastPath",
  'reason: "async_processing_required"',
  "confidence: data.confidence || 0.9",
  'if (!oceanResponse && resolvedProcessingMode !== "fast")',
];
for (const token of forbiddenRoute) check(`route forbids ${token}`, !route.includes(token));

const forbiddenStream = [
  "wantsFastHumanThinkingPlan",
  "forceHumanThinkingFastPath",
  "QWEN_CHAT_FALLBACK_MODEL",
  "shouldUseQwenAfterClxFailure",
  "FAST_TEXT_MODEL_FALLBACK",
  "OCEAN_QWEN_FALLBACK_MODEL",
  "OPENMIND_MODEL",
  "llama3.1:8b",
  "switching fallback chat model",
  'reason: "async_processing_required"',
];
for (const token of forbiddenStream) check(`stream forbids ${token}`, !stream.includes(token));

check("route uses complexity detector", route.includes("detectProcessingMode("));
check("route deep mode is preserved", route.includes('highDepthRequested\n      ? "deep"\n      : complexity.mode'));
check("route confidence is optional", route.includes("confidence?: number"));
check("route confidence only accepts number", route.includes('typeof data.confidence === "number"'));
check("stream uses complexity detector", stream.includes("detectProcessingMode("));
check("stream preserves configured model", stream.includes("process.env.OCEAN_STREAM_MODEL"));
check("stream preserves WWWMMM mapping", stream.includes('"nbd-wwwmmm:latest"'));
check("stream preserves CLX direct path", stream.includes("CLX_AGENT_URL") && stream.includes("shouldBypassToClx"));
check("stream preserves Ocean upstream path", stream.includes("buildUpstreamCandidates") && stream.includes("/api/v1/chat/stream"));
check("stream unlimited token sentinel remains", stream.includes("OCEAN_STREAM_DEFAULT_MAX_TOKENS"));

const expectedMinimum = 55;
const total = passed + failures.length;
if (total < expectedMinimum) {
  throw new Error(`Test matrix too small: ${total}; expected at least ${expectedMinimum}`);
}
if (failures.length) {
  console.error(`FAIL ${passed}/${total}`);
  for (const failure of failures) console.error(` - ${failure}`);
  process.exit(1);
}
console.log(`PASS ${passed}/${total} Ocean HumanThinking routing regression checks`);
