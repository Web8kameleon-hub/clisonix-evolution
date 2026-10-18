# Ocean voice conversation / telemetry separation — 2026-09-24

## Issue
Voice conversation text was duplicated into HTTP response headers. The transport layer must not expose transcript or assistant response text as telemetry.

## Documentation
The Ocean voice backend and web proxy no longer emit or forward conversation-text headers. The Curiosity Ocean UI no longer depends on those headers. Operational timing, detected language and selected voice remain transport telemetry. Vision configuration accepts the existing CLXI_VISION_MODEL deployment contract without introducing a hardcoded model fallback.

## Tests
Release Evidence, Runtime Capability Truth Audit, Single Branch PR Governance, repository integrity, security and deployment workflows remain authoritative. Repository search must return no active X-Transcript-B64 or X-Response-Text-B64 references after the change.

## Edge cases
Unicode conversation content is no longer serialized into HTTP headers, eliminating the latin-1 header failure path. Missing conversation metadata cannot produce fabricated UI text. Model availability remains fail-closed.

## Benchmark
No latency or throughput claim is introduced by this change. Existing benchmark gates remain authoritative.

## Rollback
Revert the voice metadata separation commits through Git history. Do not force-reset main and do not restore conversation text to transport headers.
