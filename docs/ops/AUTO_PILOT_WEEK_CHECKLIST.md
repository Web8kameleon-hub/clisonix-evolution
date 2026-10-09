# Clisonix Auto-Pilot Week Checklist (7 Days)

Owner: Ledian
Window: Friday -> Monday
Mode: Observe-only (no code changes)

## 1) Freeze Rules (No Touch)

- No `git push`
- No deploys (`docker compose up --build`, image rebuilds, service recreates)
- No `.env` edits
- No container restarts unless there is a critical outage
- No schema/config migrations

If you notice an issue, log it in the incident note and continue observing.

## 2) Critical Alerts Only

Keep only high-signal alerts enabled:

- Core API down (`clisonix-api` unreachable)
- Ocean Core down (`clisonix-ocean-core` unreachable)
- Restart loop (`>= 3 restarts in 10 min`)
- Error spike (`5xx` above baseline threshold)
- Latency spike (`P95` and `P99` above threshold)
- Memory runaway (continuous growth trend)

Silence low-priority noisy alerts for the week.

## 3) Daily 5-Minute Check (Read-Only)

- Service uptime trend
- Restart count trend
- Error rate trend (`4xx`/`5xx`)
- P95/P99 latency trend
- CPU/RAM trend for `ocean-core`, `api`, `kloud-bridge`
- Pulse/event volume trend

Do not apply fixes during the week unless outage is critical.

## 4) Data to Collect for Monday

- Uptime summary (7-day)
- Top 5 incidents by impact
- Top recurring warnings/errors
- Long-tail latency windows
- Memory drift (possible leak candidates)
- Pulse stability summary (dropouts, jitter, late events)
- Kloud bridge sync stability summary

## 5) Incident Note Template

Use one block per incident:

- Timestamp:
- Service:
- Symptom:
- Severity: `critical` | `high` | `medium` | `low`
- Observed metrics/logs:
- Temporary impact:
- Auto-recovered: `yes/no`
- Proposed fix (for Monday):

## 6) Monday Stabilization Session (30-45 min)

1. Review health dashboards (uptime, errors, latency, memory)
2. Rank incidents by business impact
3. Pick only 1-2 high-impact fixes
4. Create patch plan (smallest safe changes first)
5. Deploy one change at a time with smoke tests

## 7) Exit Criteria for Successful Auto-Pilot Week

- No prolonged core outage
- Error rate within acceptable band
- No uncontrolled memory growth
- Pulse stream remains stable
- Kloud bridge remains synchronized

If all criteria are met, proceed to next phase (algorithm hardening + RISC-V architecture planning).
