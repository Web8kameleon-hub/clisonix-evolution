# Ocean HumanThinking routing recovery — 2026-09-24

## Issue
HumanThinking/deep requests could be diverted into latency-oriented fast/callback paths, and stream routing contained implicit external-model fallback behavior. The deployment selector also treated a combined web + ocean change as a full-stack migration, which caused an unrelated `ULTRA_MS_POSTGRES_PASSWORD` requirement to block deployment.

## Documentation
This release records the routing recovery, NO_FAKE enforcement, fail-closed critical runtime tests, and the deployment-selector correction. Canonical repository and no-fake guardrails remain authoritative.

## Tests
The web regression matrix contains more than 50 targeted HumanThinking/Ocean routing checks and is wired into the zero-regression job. Critical Ocean multilingual and warm/reaction integration suites now fail when required runtime services are unreachable instead of skipping. NO_FAKE policy and fallback gates run in zero-regression.

## Edge cases
Explicit processing modes remain explicit. Missing confidence is not fabricated. CLX failure does not silently switch to Qwen/OpenMind/Llama. WWWMMM alias mapping remains supported. Combined web + ocean changes deploy only those two runtime surfaces instead of forcing unrelated full-stack secret interpolation.

## Benchmark
Existing Ocean export benchmark remains part of zero-regression. No new latency claim is made until the CI/runtime benchmark completes successfully.

## Rollback
Revert this release commit and, if required, revert the HumanThinking recovery chain back to `824cc18d6962f2d6c61682dc511ccab481459f29`. Do not force-reset main; use an auditable revert.
