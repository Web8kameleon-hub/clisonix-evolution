# Operational Runbook v1

Date: 2026-04-22  
Owner: Platform Operations  
Status: Active

## Purpose

This runbook defines the default operating procedure for stabilizing and running production safely.

It is the single operational reference for:

- deploy execution,
- guardrail enforcement,
- health verification,
- incident response,
- rollback.

## Scope and Policy

This runbook follows the stabilization policy in:

- docs/production/FOCUS_SHIFT_OPERATIONAL_STABILIZATION_2026-04-20.md

Non-negotiable rules:

1. No fake data in production paths.
2. No hardcoded secrets.
3. No synthetic healthy states.
4. No HTTP 200 on operational failures.
5. No hidden fallback behavior that masks outages.

## Source of Truth

Primary workflow and controls:

1. .github/workflows/auto-deploy-all-green.yml
2. .github/workflows/deploy-ssh.yml
3. .github/workflows/repo-integrity-guard.yml
4. scripts/guardrails/no_fake_fallback_gate.sh
5. scripts/guardrails/repo_integrity_guard.py
6. scripts/guardrails/routes_history_guard.py

Operational inventories and reports:

1. docs/production/services-health-2026-04-18.md
2. docs/production/route-destination-map.md
3. docs/production/canonical/repo_integrity_guard_report.json
4. docs/production/canonical/routes_history_guard_report.json

## Deploy Lanes

Use this strict lane order.

1. Primary lane: Auto Deploy (All Green)

- Workflow: .github/workflows/auto-deploy-all-green.yml
- Trigger: successful CI workflow run on main, or manual dispatch.
- Purpose: deterministic deploy with health gate.

1. Secondary lane: Deploy via SSH

- Workflow: .github/workflows/deploy-ssh.yml
- Purpose: controlled manual recovery and scoped rebuilds.
- Default scope: rebuild-web.

Do not use ad-hoc server commands as a normal release path.

## Pre-Deploy Checklist

All items must be true before production deploy:

1. Main branch is green in CI.
2. Repo guardrails pass in .github/workflows/repo-integrity-guard.yml.
3. No pending secret policy violations.
4. Target services are explicitly identified.
5. Rollback target commit is known.

Recommended command set (local):

1. git status --short
2. python scripts/guardrails/routes_history_guard.py
3. python scripts/guardrails/repo_integrity_guard.py

## Deploy Procedure

### A) Standard release

1. Trigger Auto Deploy (All Green).
2. Keep service list scoped to changed runtime surfaces.
3. Wait for health gate completion.
4. Record deploy outcome in change log.

### B) Scoped recovery release

1. Trigger Deploy via SSH with the smallest recovery scope.

1. Prefer this order:

- rebuild-web
- rebuild-ocean-core
- rebuild-core
- full-rebuild (last resort)

1. Run post-deploy verification immediately.

## Post-Deploy Verification

Run all checks after every production deployment.

### Service health checks

1. API health endpoint returns healthy.
2. Ocean core health endpoint returns healthy.
3. NanoGrid status endpoint returns non-error.
4. Kloud bridge health endpoint returns non-error.
5. Web root returns HTTP 200.

### Functional checks

1. Zurich deterministic smoke passes if Zurich-related code changed.
2. Critical proxy routes return real upstream responses.
3. No fake/no-demo payload behavior is observed.

### Data integrity checks

1. No impossible metric values (for example >100% cpu or memory) in public status paths.
2. No false "no data" states when upstream is healthy.

## Routes Baseline Control

Routes baseline is mandatory and must not be bypassed.

Current enforced minimums:

1. Next.js route files in history: 268
2. Python route files in history: 237
3. Combined route-related files in history: 505

Guard implementation:

- scripts/guardrails/routes_history_guard.py

Failure handling:

1. If baseline guard fails, deployment is blocked.
2. Diagnose whether failure is caused by accidental route deletion, history truncation, or guard regression.
3. Fix root cause and re-run guard before merge.

## Incident Response Flow

Severity model:

1. Sev-1: public outage, auth failure, payment path outage, or broad module downtime.
2. Sev-2: partial outage with user impact and workaround.
3. Sev-3: isolated degradation without material user impact.

### Mandatory incident sequence

1. Confirm impact and blast radius.
2. Freeze non-stabilization changes.
3. Collect evidence (workflow logs, container states, endpoint responses).
4. Apply smallest safe corrective action.
5. Re-verify health and critical business paths.
6. Publish short incident summary with root cause and prevention action.

## Rollback Procedure

Rollback is preferred over risky live patching during incident windows.

1. Identify last known good commit.
2. Deploy that commit via controlled workflow lane.
3. Verify full post-deploy checklist.
4. Keep incident open until prevention change is merged.

## Weekly Reliability Review

Run this every week:

1. Deploy success rate trend review.
2. Guardrail failure trend review.
3. Service restart burst trend review.
4. Top recurring root causes and closure status.
5. Decision on stabilization exceptions (if any).

## Definition of Operationally Stable

Operations are considered stable when all are true for at least 4 consecutive weeks:

1. Deploy lane is consistently green for normal releases.
2. Critical services recover with runbook execution only.
3. Route and guardrail contracts remain intact.
4. Data correctness regressions do not recur.

## Quick References

1. docs/production/FOCUS_SHIFT_OPERATIONAL_STABILIZATION_2026-04-20.md
2. docs/production/SESSION_HANDOFF_2026-04-17.md
3. docs/production/services-health-2026-04-18.md
4. docs/production/route-destination-map.md
5. docs/DEPLOYMENT.md
