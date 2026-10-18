# Ocean Release Readiness - 2026-09-10

## Scope
- Ocean operationalization with real bridge activation gates, per-repo connectivity checks, and persisted bridge state.
- User-assist governance with explicit consent lifecycle: approve once, approve 15 minutes, revoke now.
- CI governance rule to enforce single work-branch and single open PR policy.

## Validation Evidence

### Frontend Type Validation
- Command: `npm --prefix apps/web run type-check`
- Result: PASS
- Exit code: 0

### Backend Guardrail Tests
- Command: focused pytest suite for guardrails and fail-closed behavior
- Result: PASS
- Summary: 23 passed, warnings only

### Benchmark and Counter-Benchmark
- Release benchmark artifact: `artifacts/benchmarks/gram-release.json`
- Counter-benchmark artifact: `artifacts/benchmarks/gram-baseline.json`

Release benchmark (`nodes=5000`, `queries=500`):
- Growth median: 4.96095 ms
- Growth p95: 9.94100 ms
- Search median: 13.89730 ms
- Search p95: 18.58150 ms

Counter-benchmark (`nodes=1000`, `queries=100`):
- Growth median: 1.07090 ms
- Growth p95: 1.87770 ms
- Search median: 3.85660 ms
- Search p95: 4.49670 ms

### Ocean Governance and Audit Paths
- Bridge audit trail: `artifacts/ocean-bridge-audit.jsonl`
- Bridge state store: `.runtime/ocean-bridge-state.json`
- Consent state store: `.runtime/ocean-user-assist-consent.json`

## CI Governance Rule (Single Branch + Single PR)
- Guard script: `scripts/guardrails/single_branch_pr_guard.py`
- Workflow: `.github/workflows/single-branch-pr-governance.yml`
- Policy defaults:
  - `DEFAULT_BRANCH=main`
  - `PRIMARY_WORK_BRANCH=fix/hetzner-swarm-rollout`
  - `MAX_OPEN_PRS=1`

Enforced behavior:
- Pull requests must target `main`.
- Pull request head branch must be `fix/hetzner-swarm-rollout`.
- Open PR count for the repository must be at most 1.
- Push events are allowed only on `main` or `fix/hetzner-swarm-rollout`.

Local execution evidence:
- Command: `py scripts/guardrails/single_branch_pr_guard.py`
- Result: PASS (local mode)
- Generated report: `docs/production/canonical/single_branch_pr_guard_report.json`

## Release Recommendation
- Status: READY FOR CONTROLLED RELEASE
- Conditions:
  - Keep policy branch as `fix/hetzner-swarm-rollout` until merge.
  - Do not open a second PR before merging or closing the active PR.
  - Keep consent and bridge health checks fail-closed in all follow-up changes.
