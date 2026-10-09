# PC Adoption Runbook - WWWMMM + NDB + Stigma + Nanogrid

Purpose: standardized and safe local adoption path for teams transitioning into Clisonix resonance-first technology.

## Context
This runbook is designed for gradual migration from legacy-heavy processing to the lightweight local stack:
- CLX Hotguard (learning cycle)
- CLX.I (stigma/ndb runtime API)
- Nanogrid (optional local node)

The approach follows compatibility-first operations and avoids disruptive rewrites.

## Prerequisites
1. Windows PowerShell
2. Python 3.13.x
3. Node.js + npm (for web lock verification)
4. Optional: Rust toolchain (cargo) for Nanogrid local node

## Installation (Disk-Conscious)
From repository root:

```powershell
pwsh scripts/install_wwwmmm_ndb_stigma_pc.ps1
```

Safe optional flags:

```powershell
# avoid npm lockfile work during core runtime install
pwsh scripts/install_wwwmmm_ndb_stigma_pc.ps1 -SkipCargoCheck

# include apps/web lockfile validation only when needed
pwsh scripts/install_wwwmmm_ndb_stigma_pc.ps1 -WithWebLockCheck
```

What it installs:
1. Minimal Python runtime packages from `packages/wwwmmm-ndb-stigma-pc/requirements-min.txt`
2. Local editable CLX package from `sdist/clx-ai`
3. Optional `cargo check -p node` under `nanogrid` if Rust is available

## Start Runtime

```powershell
pwsh scripts/start_wwwmmm_ndb_stigma_pc.ps1
```

Conflict-safe variants:

```powershell
# run only CLX.I (nanomicroservice mode)
pwsh scripts/start_wwwmmm_ndb_stigma_pc.ps1 -NoHotguard

# change CLX.I port if local conflict exists
pwsh scripts/start_wwwmmm_ndb_stigma_pc.ps1 -ClxIPort 8093
```

This starts:
1. Hotguard in background (2-minute cycle)
2. CLX.I API in foreground at `http://127.0.0.1:8091`

Optional Nanogrid command:

```powershell
cd nanogrid
cargo run -p node
```

## Health Verification

### CLX.I
```powershell
curl http://127.0.0.1:8091/health
```

### Hotguard artifacts
- `.clx_ops_2min/final_report.json`
- `.clx_ops_2min/cycle_*.json`

### CLX.I telemetry artifacts
- `.clx_i/mirror_events.jsonl`
- `.clx_i/selflearning_events.jsonl`

## Safe Rollout Policy (Local -> Team)
1. Day 1-3: Shadow-only observation
2. Day 4-7: Advisory comparison against existing behavior
3. Week 2: Hybrid use on low-risk tasks
4. Week 3+: Default use with fallback preserved

## Microservice/Nanomicroservice Route Policy (NDB)
1. Every route must run as a service boundary (microservice or nanomicroservice).
2. Avoid isolated route conflicts by enforcing one owner per route group.
3. NDB/Stigma classification runs per service boundary, not as hidden global side effects.
4. Route versioning must be explicit (`/api/v1/...`) to prevent cross-service collisions.
5. Keep CLX.I as the local NDB policy endpoint and consume it through stable HTTP contracts.

## Why the Mini-Crash Happened (and Fix)
1. Script comment headers were malformed in previous revision, so help flags could execute code unexpectedly.
2. Aggressive Python tool upgrades can conflict with heavy local stacks.
3. New scripts now use safe defaults and explicit optional checks.

## Mandatory Safety Controls
1. Keep fallback path to existing stack during transition
2. Keep no-fake-data guardrails active
3. Do not enforce on high-risk routes before canary evidence
4. Keep rollback command documented in each team handover

## Team Handover Checklist
1. Machine profile (CPU/RAM/disk)
2. Installed versions (Python/Node/Rust)
3. Verified health outputs
4. Last known working commands
5. Owner and on-call contact

## Troubleshooting

### Missing CLX import
```powershell
.\.venv\Scripts\python.exe -m pip install -e sdist/clx-ai
```

### CLX.I fails to start
- Verify `.venv` exists
- Verify `fastapi` and `uvicorn` imports
- Check port `8091` not in use

### Nanogrid check skipped
- Install Rust (`cargo`)
- Re-run installer script

## Adoption Success Criteria
1. Local runtime stable for 7 days with no data corruption artifacts
2. Team can run install/start/verify sequence from this runbook only
3. Transition does not degrade existing project availability
4. Metrics and event logs are reproducible across developer PCs
