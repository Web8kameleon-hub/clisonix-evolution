<!-- markdownlint-disable MD013 -->

# Clisonix One Capability Audit — 2026-09-10

## Scope

This audit answers five questions with evidence from the current repository, git history, and the observed runtime:

1. Which capabilities already exist locally.
2. Which are already linked to Ocean.
3. Which are currently live in runtime.
4. Which are duplicate, legacy, or documentation-only.
5. Which implementation should remain canonical.

## Method

- Local source inspection
- Git history scan
- Current production container inventory
- No new components created during this audit

## Executive Verdict

Clisonix already contains most of the organs needed for a single system conductor. The main gap is not missing engines. The main gap is the lack of one canonical activation path across:

`discover -> reuse -> connect -> test -> change -> deploy -> verify -> prove`

The strongest reusable building blocks already present are:

- `registry_export.json` plus `core/auto_registry.py`
- `apps/web/app/api/service-discovery/route.ts`
- `clisonix_integration_runner.py`
- `orchestrate_discovery_tests.py`
- `ocean_nanogrid.py` and `ocean_core_adapter.ts`
- `services/intelligence-lab/main.py`
- `packages/gram/*`
- `agent_telemetry.py` and `tracing.py`

The strongest duplication risks are:

- external bridge concepts already referenced in history but not active locally, especially `Cwy`, `OS-CLX`, and `Ultrawebthinkig-v2`
- multiple partially overlapping Ocean integration surfaces
- runtime services that exist in code or compose but are not part of the active production control path

## Evidence Matrix

| Capability | Local Evidence | Ocean-Linked Today | Runtime Live Today | Classification | Canonical Decision |
| --- | --- | --- | --- | --- | --- |
| Capability Registry | `core/auto_registry.py`, `registry_export.json` | Partial | No direct service evidence | Reusable, canonical candidate | Keep `core/auto_registry.py` as canonical registry generator |
| Runtime Discovery | `apps/web/app/api/service-discovery/route.ts`, `orchestrate_discovery_tests.py` | Yes | Partial | Reusable | Keep service-discovery route as public read path, keep orchestrator as verification harness |
| System Graph / Inventory | `registry_export.json`, `CLISONIX_MODULE_MAP.md`, `docs/production/canonical/*inventory*.json` | Partial | Static evidence only | Reusable, fragmented | Keep registry export plus canonical inventories; do not create another inventory format |
| Execution Runner | `clisonix_integration_runner.py` | No direct Ocean routing proved | Not observed live in prod | Partial reusable | Keep as batch execution backbone, not as user-facing API directly |
| Workflow Orchestration | `orchestra/`, runtime container `clisonix-orchestra` | Partial | Yes | Reusable | Keep `orchestra` as orchestration surface |
| Ocean Adapter | `ocean_core_adapter.ts`, `ocean_nanogrid.py`, `ocean-core/ocean_nanogrid.py` | Yes | Partial | Reusable, overlapping | Keep `ocean_nanogrid.py` and `ocean_core_adapter.ts` as canonical adapter pair |
| GRAM / GS26 | `packages/gram/*`, `scripts/benchmark_gram.py`, `apps/web/app/api/ocean/curriculum/route.ts`, `alba_service_5555.py` | Yes | No dedicated `gram` container observed in prod | Exists, partially linked | Keep `packages/gram` as canonical GRAM implementation; activate via compose/runtime instead of re-implementing |
| MALI / Intelligence Lab | `services/intelligence-lab/main.py`, `services/intelligence-lab/control_plane.py`, `services/intelligence-lab/mali_core.py` | Yes | Candidate-only evidence, not canonical prod service | Exists, partially linked | Keep `services/intelligence-lab` as canonical MALI/KLAJDI implementation |
| Telemetry / Tracing | `agent_telemetry.py`, `tracing.py` | Yes | Yes: `clisonix-agent-telemetry`, tracing stack containers observed | Active reusable | Keep current telemetry stack; wire it into proof ledger instead of replacing it |
| OS-CLX Federation | `apps/web/app/api/ocean/ls-status/route.ts`, architecture artifacts, git history | Metadata bridge only | No direct local runtime surfaced | External bridge, not local canonical implementation | Treat as external integration target, not a missing local engine |
| CWY | Git history only, knowledge/profile references only | No | No | External or decoupled history, not active local asset | Do not recreate locally unless explicitly vendored back in |
| Ultrawebthinkig-v2 | Git history plus external-compose references | No | No active runtime evidence in current control path | External or decoupled | Keep as bridge target only until explicitly restored |

## Key Proofs

### 1. Registry already exists

`core/auto_registry.py` already exports `registry_export.json` and `.env.services`.

Observed behavior:

- scans functions, services, endpoints
- emits summary counts
- writes canonical export artifacts

This means a new registry service should not be created before this one is evaluated as the canonical base.

### 2. Ocean already has discovery surfaces

`apps/web/app/api/service-discovery/route.ts` already infers capability sets such as:

- `mali`
- `bridge-connectivity`
- `reasoning`
- `observability`
- `analytics`

This is already a conductor-facing primitive and should be reused.

### 3. GRAM already exists as a real package

`packages/gram/server.py` exposes real GRAM endpoints:

- `GET /health`
- `POST /gram/nodes`
- `POST /gram/search`
- `POST /gram/json`
- `POST /gram/plot`
- `POST /gram/sequence`

`docker-compose.yml` also defines a `gram` service with port `9710` and a dependency on `intelligence-lab`.

This is direct evidence that GRAM is not missing. It is present but not canonically activated in the production path currently observed.

### 4. GS26 is already linked into Ocean-facing behavior

`apps/web/app/api/ocean/curriculum/route.ts` forwards to `/gs26/curriculum/*`.

`alba_service_5555.py` contains `AlbaGS26Engine` and explicitly states:

- integrates `GRAM`
- integrates `NodeDBFluid`
- integrates `WWWMMM`
- integrates `Hotguard`

This confirms GS26 is not aspirational only. It is already a named execution fabric in code.

### 5. MALI already exists as a canonical service candidate

`services/intelligence-lab/main.py` is a concrete FastAPI implementation for:

- `/mali/*`
- `/klajdi/*`
- `/mali/project-map`
- `/mali/signals/*`

It also attaches a control plane and publishes shared signal events. This is a strong candidate for the canonical labor intelligence layer.

### 6. Telemetry stack is already live

Production runtime inventory shows live telemetry and observability surfaces such as:

- `clisonix-agent-telemetry`
- `clisonix-jaeger`
- `clisonix-tempo`
- `clisonix-grafana`
- `clisonix-prometheus`

This means `Proof Ledger` should be built by composing existing telemetry, not by inventing a fresh observability subsystem.

### 7. CWY is not a current local runtime asset

Git history shows:

- `a04643b9 Integrate CWY as Git submodule for self-hosted usage`
- `d0e0cc6b restore external/Cwy submodule mapping`
- `482578ef decouple external submodules (Cwy, Ultrawebthinkig-v2) from pipeline`

Current local workspace search found no active `Cwy` files. Therefore:

- CWY should be classified as `external or decoupled history`
- it should not be re-created locally without explicit vendoring or bridge restore

### 8. OS-CLX is currently bridge metadata, not a local active engine

Current evidence for OS-CLX is mainly:

- `apps/web/app/api/ocean/ls-status/route.ts`
- rearchitecture artifacts under `.github/modernize/rearchitecture/artifacts/*`
- git history commits such as `60ab542f Add strict HVMOW adapter for OS-CLX observe API`

That is enough to treat OS-CLX as a federation target, but not enough to treat it as a local capability that needs duplication.

## Git History Highlights

Relevant commits proving earlier work already exists:

- `de6a0cd5` Test Clisonix to OS-CLX HVMOW contract
- `60ab542f` Add strict HVMOW adapter for OS-CLX observe API
- `3cf58d07` add sovereign OS-CLX telemetry ingest v1
- `d1768de3` integrate real labs NanoGrid and GRAM
- `9201759d` add HVO/GS26/GRAM and medicine integration routes
- `2b645fcd` complete tech stack with CWY search and dependency manifest
- `3c965104` add dedicated gram service and runtime mapping
- `a04643b9` integrate CWY as Git submodule
- `482578ef` decouple external submodules (Cwy, Ultrawebthinkig-v2) from pipeline
- `6eb7743d` add Intelligence Lab (KLAJDI+MALI) and User Management services
- `053a6016` streaming with `ocean_nanogrid.py`

These commits are enough to justify a strict reuse-first policy.

## Runtime Snapshot From Current Host

Observed live containers relevant to this audit include:

- `clisonix-next_ocean-core`
- `clisonix-next_api`
- `clisonix-next_kloud-bridge`
- `clisonix-next_web`
- `clisonix-next_billing`
- `clisonix-agent-telemetry`
- `clisonix-orchestra`
- `clisonix-jaeger`
- `clisonix-tempo`
- `clisonix-grafana`
- `clisonix-prometheus`
- `mali-py314-candidate-test-20260830`

Not observed as active canonical runtime services during this audit:

- dedicated `gram` runtime service
- canonical `intelligence-lab` production service under its expected compose identity
- local CWY runtime
- local OS-CLX runtime

## Canonical Activation Decisions

### Reuse immediately

- `core/auto_registry.py`
- `registry_export.json`
- `apps/web/app/api/service-discovery/route.ts`
- `clisonix_integration_runner.py`
- `orchestrate_discovery_tests.py`
- `ocean_nanogrid.py`
- `ocean_core_adapter.ts`
- `services/intelligence-lab/*`
- `packages/gram/*`
- `agent_telemetry.py`
- `tracing.py`

### Keep as bridge metadata, do not duplicate locally

- `OS-CLX`
- `Kloud` external bridge definitions
- `Web8`
- `neuclx`
- `Ultrawebthinkig-v2`
- `Lightning-SPP-3.14`
- `www.neuroconic.eu`

### Treat as external or history-only until explicitly restored

- `Cwy`

## What Is Actually Missing

The audit does **not** prove that a new engine is missing.

What is missing is a single canonical surface that composes the existing parts into one conductor workflow.

Minimal missing layer:

1. one canonical command surface
2. one duplicate guard using registry plus git history
3. one runtime verification gate
4. one action runner that can call the already-existing runner and orchestrator layers
5. one proof ledger that records evidence from current telemetry and validation systems

## Recommended Next Step

Do not build a new engine first.

Build the smallest possible `Clisonix One` shell on top of existing assets in this order:

1. `inspect` -> source inventory from `registry_export.json` and `service-discovery`
2. `runtime` -> live verification from current containers and health endpoints
3. `duplicate-check` -> local candidates plus git history
4. `plan` -> route to existing runner/orchestrator
5. `prove` -> store outcome via telemetry and validation

## Final Classification Summary

- `Exists and should be reused`: registry, discovery, integration runner, orchestrator, Ocean adapter, MALI, GRAM, telemetry
- `Exists but not fully activated in prod`: GRAM service, intelligence-lab canonical runtime, some GS26 execution paths
- `External bridge only`: OS-CLX and several sibling repos
- `History-only or decoupled`: CWY local runtime integration
- `Not justified to create anew`: a second registry, a second GRAM, a second MALI, a second orchestrator, or a fresh telemetry stack

<!-- markdownlint-enable MD013 -->
