# Adopter Harmonic Secure Guide

Purpose: give future teams a single safe procedure to adopt Clisonix WWWMMM/NDB/Stigma/Nanogrid technology without destabilizing production.

## Who Should Use This Guide
- Internal platform teams
- New service owners
- Partner teams integrating with Clisonix policy fabric

## Core Adoption Rules
1. Adopt in phases only; never use big-bang replacement.
2. Keep compatibility mode active until validated by SLO and incident window.
3. Treat telemetry quality as a release blocker.
4. Apply no-fake-data policy in every integration path.

## Pre-Adoption Checklist
1. Service has health and status endpoints.
2. Service has trace id propagation.
3. Rollback path tested in staging.
4. Route risk level assigned (low, medium, high).
5. Owner and on-call rotation defined.

## Harmonized Integration Contract

### Required Runtime Fields
- node_id
- endpoint
- action
- stigma_level
- ndb_score
- ndb_delta
- ndb_threshold
- tide
- outcome
- timestamp_ms
- correlation_id

### Required Decision States
- allow
- monitor
- throttle
- block

### Required Safety States
- high_risk true or false
- fallback_active true or false

## Security and Reliability Baselines
1. Real errors only; no fake success responses.
2. No silent null or None returns in error handlers.
3. Hardcoded secret scanning must pass before rollout.
4. Health checks must probe real dependencies.

## Standard Adoption Flow

### Step A - Shadow
- Enable telemetry only.
- Validate data completeness and schema correctness.

### Step B - Advisory
- Enable recommendation mode.
- Measure mismatch against current policy.

### Step C - Hybrid
- Enforce for low-risk canary routes only.
- Auto-rollback if SLO thresholds are crossed.

### Step D - Default
- Promote to resonance-first for validated route groups.
- Keep fallback path and test it each release.

## SLO Gates (Minimum)
1. Availability gate: no unacceptable regression.
2. Latency gate: p95 within service envelope.
3. Safety gate: false-block and false-allow within target.
4. Data gate: telemetry completeness above target.

## Rollback Procedure (Mandatory)
1. Toggle NDB_GLOBAL_KILL_SWITCH.
2. Re-route decisions to legacy engine.
3. Keep telemetry running for root cause evidence.
4. Open incident report with timeline and metrics.
5. Re-enable only after corrective action and review approval.

## Evidence Pack for Every Adoption
1. Route list and risk classification.
2. Before and after SLO snapshots.
3. Drift trend summary for rollout window.
4. Incident and rollback log, even if zero incidents.
5. Sign-off from engineering, security, and product owner.

## Anti-Patterns (Do Not Do)
1. Enforcing on high-risk routes before canary success.
2. Disabling fallback to simplify architecture.
3. Tuning thresholds without change log.
4. Shipping with missing telemetry fields.

## Handover Template
1. Service name and owner.
2. Phase reached.
3. Enabled flags.
4. Current thresholds.
5. Rollback command and owner.
6. Open risks and next review date.

## Final Adoption Success Criteria
1. New model improves decision quality without harming uptime.
2. Operations can explain every block/throttle decision from telemetry.
3. Recovery is fast and tested.
4. Documentation is complete for next adopters.
