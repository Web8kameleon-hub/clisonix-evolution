# Ocean multilingual and voice UTF-8 recovery — 2026-09-24

## Issue
Production showed incorrect language behavior for German greetings and voice failures when Unicode text was placed directly in HTTP response headers.

## Documentation
Voice transcript and response metadata now use base64-encoded UTF-8 values in ASCII-safe headers. The browser decodes them back to Unicode. Greeting routing derives language from the greeting before browser hints. Canonical models must be explicitly configured.

## Tests
Existing Ocean multilingual/runtime suites, web build/type-check, NO_FAKE and repository-integrity gates cover this path.

## Edge cases
Unicode metadata no longer depends on latin-1-compatible headers. Missing model configuration fails with 503 and empty model output fails with 502.

## Benchmark
No new latency claim is introduced; existing Ocean benchmark gates remain authoritative.

## Rollback
Revert this commit through Git history; do not force-reset main.
