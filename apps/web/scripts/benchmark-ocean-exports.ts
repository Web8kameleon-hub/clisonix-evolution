import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { createConversationArtifact } from "../app/api/ocean/curiosity/export/export-artifacts.ts";

const messages = Array.from({ length: 1000 }, (_, index) => ({
  role: index % 2 ? "assistant" : "user",
  content: `Message ${index}: ${"validated knowledge ".repeat(20)}`,
}));

const started = performance.now();
const pdf = createConversationArtifact("pdf", messages);
const docx = createConversationArtifact("docx", messages);
const elapsedMs = performance.now() - started;

assert.ok(pdf.bytes.length > 100_000);
assert.ok(docx.bytes.length > 100_000);
assert.ok(elapsedMs < 5_000, `Export benchmark exceeded 5 seconds: ${elapsedMs.toFixed(1)} ms`);
console.log(`Ocean export benchmark: 1000 messages in ${elapsedMs.toFixed(1)} ms; PDF=${pdf.bytes.length}, DOCX=${docx.bytes.length}`);
