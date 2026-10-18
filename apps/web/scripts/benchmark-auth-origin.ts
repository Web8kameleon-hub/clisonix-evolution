import { performance } from "node:perf_hooks";
import { originMatches } from "../src/lib/security/request-origin.ts";

const iterations = 100_000;
const trusted = [
  "http://clisonix-web:3000",
  "https://www.clisonix.com",
  "https://www.clisonix.com",
];
const started = performance.now();
let accepted = 0;
for (let index = 0; index < iterations; index += 1) {
  if (originMatches("https://www.clisonix.com/sign-up", trusted)) accepted += 1;
}
const elapsedMs = performance.now() - started;
if (accepted !== iterations) throw new Error("origin benchmark correctness failure");
console.log(JSON.stringify({
  iterations,
  accepted,
  elapsed_ms: Number(elapsedMs.toFixed(3)),
  operations_per_second: Math.round(iterations / (elapsedMs / 1000)),
}));
