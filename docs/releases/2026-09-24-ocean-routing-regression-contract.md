# Ocean routing regression contract — 2026-09-24

## Issue
The HumanThinking regression script asserted a `balanced` processing mode even though the canonical `ProcessingMode` type supports only `fast | deep`. This made the production Web build fail TypeScript validation.

## Change
The regression assertion now verifies the actual contract: an unsupported `balanced` request is not promoted to a nonexistent mode and the canonical detector classifies the short query as `fast`. Runtime routing code is unchanged.

## Tests
The authoritative gates are the Ocean HumanThinking regression matrix, Web type-check, Web production build, NO_FAKE gates, critical Ocean runtime integration tests, GHCR Web build/smoke and release evidence validation.

## Edge cases
Explicit `fast` and `deep` behavior remains covered. Unknown processing-mode strings continue through normal complexity detection rather than creating an undocumented third mode.

## Benchmark
No performance claim or runtime algorithm change is introduced.

## Rollback
Revert this test-contract commit through Git history; do not force-reset main.
