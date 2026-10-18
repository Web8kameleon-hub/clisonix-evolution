# WWWMMM / NDB / NanoGrid NO_FAKE correction — 2026-09-24

## Issue
Legacy NDB middleware claimed real scoring while deriving scores from request length/IP hashes and demonstration policy rules. That path could not be used as evidence for WWWMMM/NDB production decisions.

## Change
- Shadow NDB measurements now come from the configured real NanoGrid status endpoint.
- Required NanoGrid fields are ndb_score, ndb_delta and tide; missing/unreachable runtime fails closed with HTTP 503 when NDB mode is enabled.
- Advisory, hybrid and resonance-default modes reuse the same measured source.
- Placeholder route defaults were removed.
- Hybrid canary selection is deterministic via SHA-256 rather than Python process-randomized hash.
- Events identify their source as nanogrid-runtime.
- Conversation/body content is not persisted as NDB telemetry.

## Tests and gates
CI/release gates remain authoritative. Required follow-up runtime validation is NanoGrid availability plus real WWWMMM/Ocean integration; no PASS is claimed by this document.

## Edge cases
Disabled feature flags preserve the underlying application path. Invalid stigma headers normalize to level 2. Missing runtime measurements fail closed rather than inventing scores.

## Benchmark
No latency or throughput claim is introduced. Runtime NanoGrid lookup adds an external measurement request only when an NDB middleware mode is enabled.

## Rollback
Revert these commits through Git history. Do not force-reset main.


## Deployment scope correction
The auto-deploy classifier now recognizes changes limited to the NDB middleware files. Such changes no longer fall through to the unrelated full-stack Swarm deployment, which previously required ULTRA_MS_POSTGRES_PASSWORD even though the NDB middleware change did not modify Ultra-MS/Postgres.

There is currently no verified standalone production deploy target for these root-level NDB middleware modules. The scoped path therefore synchronizes the repository and performs Python syntax validation, but deliberately does not claim that the middleware is active in production. A future runtime activation must identify the canonical consuming service and prove NanoGrid readiness/inference before enabling the NDB feature flags.

### Validation
The first run of the corrected classifier completed Auto Deploy + Auto Release successfully and the Security Transition CI/CD completed successfully. Release Evidence correctly rejected the workflow-only code change because this evidence file had not changed in that commit; this update closes that evidence requirement. No NDB production-runtime PASS is claimed.
