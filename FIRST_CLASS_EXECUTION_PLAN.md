# Clisonix First-Class Execution Plan (Grounded on Real Topology)

## Purpose
This document defines a realistic, execution-first path to make Clisonix a first-class platform using the services and ports that actually run today.

---

## Current Runtime Truth (Source of Truth: docker-compose.yml)

### Core services (verified)
- `clisonix-api` -> `8000`
- `clisonix-jona` -> `7777`
- `clisonix-alda` -> `8063`
- `clisonix-liam` -> `8062`
- `clisonix-intelligence-lab` (KLAJDI + MALI in one service) -> `8098`
- `clisonix-excel-service` -> `8002`
- `clisonix-alba` -> `5555`
- `clisonix-albi` -> `6680`
- `clisonix-albi-user` -> `6681`

### Important clarification
Some discussed ports in strategy drafts (for example separate KLAJDI/MALI split ports) are not the deployed default topology right now. Treat `docker-compose.yml` as canonical until intentional migration is completed.

---

## Immediate Goals
1. Stabilize API contracts between frontend, API proxy, and engines.
2. Remove legacy/imaginary endpoint drift from runtime routing.
3. Add measurable quality gates (health, smoke tests, latency/error budgets).
4. Prepare safe path for EEG device integrations (consumer first, medical later).

---

## 30/60/90 Day Plan

## Phase 1 (Days 0-30): Contract & Runtime Stabilization

### Deliverables
- Canonical service map published and enforced in code/config.
- Endpoint inventory for:
  - Neural synthesis (`/api/jona/*` via API proxy)
  - Intelligence Lab (`/klajdi/*`, `/mali/*`)
  - ALDA/LIAM dependency calls
- Remove or flag legacy fallback ports that are not used in current deployment.
- Add smoke tests for critical user journeys:
  - Start synthesis -> preview audio available
  - Stop synthesis -> export/list works
  - Intelligence endpoint reachable via API route

### Acceptance criteria
- 100% of core services return healthy on `/health`.
- No contract mismatch between web -> api -> engine for top 10 endpoints.
- P95 latency baseline captured for critical endpoints.

---

## Phase 2 (Days 31-60): Observability, Reliability, and Data Quality

### Deliverables
- Unified observability dashboard for:
  - request rate, errors, p95 latency
  - queue/cache health (Redis)
  - engine availability (JONA, ALDA, LIAM, intelligence-lab)
- Error taxonomy + standard response shape for internal service calls.
- Replayable integration test suite (happy path + degraded dependencies).
- Data quality guards for synthesized assets/metadata (dedup, mandatory fields).

### Acceptance criteria
- Error budget defined and tracked weekly.
- Regression test suite runs before deploy and blocks on critical failures.
- Incident runbook for top 5 operational failures.

---

## Phase 3 (Days 61-90): Product Hardening + Device Integration Layer

### Deliverables
- Device adapter layer for EEG/wearables with pluggable connectors.
- Two-lane integration model:
  - Lane A: consumer wellness devices (Muse/OpenBCI style adapters)
  - Lane B: medical-grade integrations behind compliance gates
- Feature flags for adaptive neurofeedback loops.
- Versioned API contracts for partner/device ecosystem.

### Acceptance criteria
- At least one end-to-end device -> analysis -> synthesis demo path is stable.
- Backward-compatible API versioning policy enforced.
- Compliance scope documented (GDPR/HIPAA readiness checklist, not certification claim).

---

## Canonical Routing Policy (Required)
- Only one canonical port per service in production routing.
- Any fallback endpoint must be:
  1) explicitly documented,
  2) health-checked,
  3) observable,
  4) removable by feature flag.
- No hidden localhost fallback in production unless explicitly approved.

---

## Operational Checklist (Weekly)
- Validate all core `/health` endpoints.
- Run smoke tests for synthesis + intelligence flows.
- Verify no new endpoint drift from canonical map.
- Review top errors and p95 regressions.
- Review stale/unused fallbacks and deprecate aggressively.

---

## Suggested Next Implementation Tasks
1. Create `docs/architecture/CANONICAL_SERVICE_MAP.md` from current compose.
2. Patch internal callers to remove ambiguous legacy LIAM/ALDA target fallbacks.
3. Add CI smoke job for synthesis preview + intelligence API availability.
4. Add `DEPLOYMENT_READINESS.md` gate checklist used before each production rollout.

---

## Notes
- This plan intentionally prioritizes reliability and contract correctness before adding new modules.
- Build on verified runtime truth first, then scale architecture.
