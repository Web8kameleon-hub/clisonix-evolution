# Clisonix Cloud Transition Plan (1-4)

Purpose: migrate Clisonix-cloud gradually to WWWMMM + NDB + Stigma + Nanogrid with minimal risk and no big-bang rewrites.

## Scope
- In scope: runtime classification, telemetry, policy engine, rollout controls, observability, rollback.
- Out of scope: full replacement of compute hardware primitives.

## Design Principle
Resonance-first as decision model, compatibility-first as operations model.

## Phase 1 - Shadow Mode (No Production Impact)
Duration: 2-4 weeks

### Goal
Collect NDB/Stigma/Tide telemetry in parallel with current stack, without changing production decisions.

### Work Items
1. Add a sidecar evaluator in API path that computes ndb_score, ndb_delta, tide, stigma_level.
2. Keep current decision engine as single source of truth.
3. Persist event records with endpoint, action, score, outcome, and correlation id.
4. Publish dashboards for false-positive potential and drift trend.

### Entry Criteria
- Existing endpoints stable and monitored.
- Feature flags available per route.

### Exit Criteria
- 14 days stable telemetry with no ingestion gaps.
- Baseline quality report approved by engineering and security.

### Guardrails
- No blocking decisions by new model.
- Kill switch available at route and service level.

## Phase 2 - Advisory Mode (Recommendation Only)
Duration: 2-3 weeks

### Goal
Generate policy recommendations (allow/monitor/throttle/block) while current engine still decides.

### Work Items
1. Enable recommendation outputs from new policy layer.
2. Compare recommendation vs current decision and log mismatch classes.
3. Add mismatch review workflow in daily ops routine.
4. Tune thresholds using real route-level behavior.

### Exit Criteria
- Recommendation agreement above target for low-risk routes.
- No increase in error budget burn.

### Guardrails
- Recommendation cannot auto-enforce.
- Any threshold change requires change log and owner approval.

## Phase 3 - Hybrid Enforcement (Controlled Canary)
Duration: 3-5 weeks

### Goal
Allow new model to enforce on selected low-risk routes through canary rollout.

### Work Items
1. Select low-risk route set and assign route owners.
2. Rollout progression: 5% -> 20% -> 50% traffic.
3. Keep fallback to legacy decision engine for each step.
4. Add automated rollback based on SLO breach.

### Exit Criteria
- P95 latency and 5xx rate remain within agreed thresholds.
- No severe false block incidents for agreed observation window.

### Guardrails
- Hard rollback trigger on availability drop.
- Mandatory incident postmortem for every rollback.

## Phase 4 - Resonance-First Default (Compatibility Layer Retained)
Duration: 4-8 weeks

### Goal
Set WWWMMM/NDB/Stigma/Nanogrid policy as default for chosen domains, keeping legacy compatibility path.

### Work Items
1. Promote new model to primary policy path for validated route groups.
2. Retain legacy path as compatibility and recovery layer.
3. Move tuning and audit into standard release workflow.
4. Freeze interface contracts for downstream teams.

### Exit Criteria
- New model handles majority of validated route groups.
- Legacy fallback remains operational and tested.
- Audit package generated for legal/compliance review.

### Guardrails
- Never remove fallback before 2 full release cycles.
- Keep no-fake-data and real-error policy gate mandatory.

## Cross-Phase SLO Policy
1. Availability: no regression beyond approved error budget.
2. Latency: p95 must stay within agreed envelope per route class.
3. Safety: false-block and false-allow tracked as first-class metrics.
4. Recovery: rollback path tested weekly.

## Required Feature Flags
- NDB_SHADOW_ENABLED
- NDB_ADVISORY_ENABLED
- NDB_HYBRID_ENFORCE_ENABLED
- NDB_RESONANCE_DEFAULT_ENABLED
- NDB_GLOBAL_KILL_SWITCH

## Weekly Governance Cadence
1. Engineering review: thresholds, drift, incidents.
2. Security review: anomaly classes and risk posture.
3. Product review: user-impact and route coverage.
4. Legal/compliance note: evidence and trace completeness.

## Definition of Done (Final)
1. Transition completed without service breakage.
2. New decision model measurable and auditable.
3. Compatibility fallback preserved and tested.
4. Operational runbooks updated and adopted by all route owners.
