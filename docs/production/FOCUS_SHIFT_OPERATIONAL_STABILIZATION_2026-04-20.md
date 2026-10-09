# Focus Shift Memo: From Abstract Build to Operational Stabilization

Date: 2026-04-20
Owner: Platform Operations
Status: Active

## Executive Decision

We are formally changing delivery focus from abstract feature expansion to operational stabilization.

This means:
- Reliability before novelty.
- Deterministic deploy behavior before new surface area.
- Incident reduction before architecture growth.
- Live-data correctness before UX enhancements.

## Why This Shift Is Required Now

Recent production signals show the main risk is no longer "missing features" but "operational instability under load and during deploy windows".

Observed patterns:
- Retry storms and process churn during partial outages.
- File descriptor pressure (too many open files) and timer overlap risk.
- Health gate race windows after compose restarts.
- Customer-facing "no data" states caused by strict payload assumptions, not true upstream outage.

Conclusion:
- The highest ROI path is stabilizing run-time behavior, deploy determinism, and data-path robustness.

## Scope Guardrails (Immediate)

In scope:
- Runtime hardening.
- Health gates and deploy reliability.
- Incident prevention controls.
- Real-data contract normalization.
- Runbooks, recovery scripts, and verification automation.

Out of scope (until stabilization gates pass):
- New modules.
- New containers/services.
- Broad refactors without incident-linked outcome.
- Cosmetic changes not tied to reliability or correctness.

## Non-Negotiable Principles

1. No fake data in production paths.
2. No hardcoded secrets.
3. No synthetic healthy claims without real checks.
4. No HTTP 200 for operational failures.
5. No hidden fallback behavior that masks outage semantics.

## Operating Model

### Delivery Priority Order

1. Availability and recovery.
2. Data correctness and telemetry integrity.
3. Security and access hardening.
4. Performance consistency.
5. Feature work.

### Change Acceptance Criteria

A production change is accepted only if it does all of the following:
- Reduces a known incident class OR closes a measurable reliability gap.
- Adds or updates a verification path (health check, smoke check, runbook, or alarm).
- Preserves no-fake-data policy behavior.
- Is rollback-safe.

## Deploy Policy: Auto Deploy (All Green)

Workflow: [.github/workflows/auto-deploy-all-green.yml](.github/workflows/auto-deploy-all-green.yml)

Current role:
- Primary controlled deployment lane for main.
- Enforces preflight and remote health-gated restart flow.

### Required Behavior

- Preflight must validate deployment-critical files and compose structure.
- SSH authentication must be validated before remote actions.
- Deploy must rebuild/restart only intended services.
- Health gates must fail closed and print actionable logs.
- Run summary must always capture trigger, services, compose file, and result.

### Stabilization Notes

- Keep health checks endpoint-accurate per service.
- Avoid race-prone assumptions during cold start windows.
- Prefer deterministic retry windows over aggressive restart loops.
- Keep concurrency predictable for main deploy lane.

## SLO and KPI Baseline (Stabilization Phase)

Initial operational targets for this phase:
- Deploy success rate >= 98% (rolling 14 days).
- Mean time to detect (MTTD) < 2 minutes for critical service health failure.
- Mean time to recover (MTTR) < 15 minutes for mapped incidents.
- False "No data" UI states reduced to zero for healthy upstream scenarios.
- Unplanned container restart bursts reduced by at least 70% from current baseline.

## Workstreams (30 / 60 / 90 Days)

### Day 0-30: Stop the bleed

- Enforce conservative retry/backoff and lock-based anti-overlap where needed.
- Stabilize deploy health gates for all critical services in the default deploy set.
- Eliminate schema-fragile aggregation paths in proxy endpoints.
- Publish first-class incident and recovery runbooks for top recurring failures.

Deliverable:
- Fewer failed deploys, fewer false negatives, fewer manual firefights.

### Day 31-60: Harden and instrument

- Add trend visibility for deploy outcomes and health gate failures.
- Add explicit runbook links in deploy summaries.
- Close top 3 repeated incident causes with permanent controls.
- Expand endpoint-level smoke checks for post-deploy validation.

Deliverable:
- Deterministic deploy and faster on-call decisions.

### Day 61-90: Institutionalize reliability

- Lock reliability acceptance checks into CI/CD governance.
- Define service-specific operational budgets (error budget and restart budget).
- Freeze exception path for non-stabilization work unless approved by ops owner.
- Publish reliability scorecard and weekly risk review.

Deliverable:
- Stability-first becomes default operating behavior, not an emergency mode.

## Roles and Ownership

- Platform Ops: deployment gate, runtime hardening, rollback policy.
- API Owners: health endpoint truthfulness and data contract robustness.
- Frontend Owners: display logic must represent real upstream state (no fabricated activity).
- Incident Lead (rotating): postmortem quality, prevention actions, closure tracking.

## Definition of Done for This Focus Shift

This shift is successful when all are true:
- Deploy lane is predictably green for normal releases.
- Critical services recover without operator improvisation.
- Data visibility errors from schema mismatch are closed.
- Reliability metrics show sustained improvement over at least 4 consecutive weeks.
- New work intake follows stabilization guardrails by default.

## Decision Log Entry

Decision ID: OPS-FOCUS-SHIFT-2026-04-20

Decision:
- Prioritize operational stabilization over abstract expansion until stabilization KPIs are met.

Review cadence:
- Weekly reliability review.
- Formal reassessment at Day 30, Day 60, and Day 90.

## Immediate Next Actions

1. Keep this memo as the authoritative policy anchor for current quarter operations.
2. Link this memo from handoff and deployment runbook documents.
3. Require any production PR to state explicit stabilization impact.
4. Reject changes that increase operational risk without compensating controls.

## Appendix A: Auto Deploy (All Green) Run Context

Reference run:
- Workflow: Auto Deploy (All Green)
- Run label provided: #292
- Workflow file: [.github/workflows/auto-deploy-all-green.yml](.github/workflows/auto-deploy-all-green.yml)

Operational interpretation:
- This workflow already reflects the right direction: preflight + controlled SSH auth + remote deploy + health gate.
- The stabilization shift does not replace this workflow; it tightens and operationalizes it.
- Every deploy signal from this lane must be treated as an operational quality signal, not just CI status.

Required practice from this point:
- If deploy fails, we do incident-level diagnosis before any feature continuation.
- If deploy passes but data correctness fails, release is considered incomplete.
- If health gates are flaky, the gate logic is a priority bug and must be hardened first.
