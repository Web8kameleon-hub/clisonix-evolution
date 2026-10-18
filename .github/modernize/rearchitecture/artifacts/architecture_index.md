# CLX Action Fabric Architecture Index

This index is not the full implementation contract. Before changing a unit, implementation agents must read every exact artifact path listed for that unit and filter the global tables as instructed.

## Implementation Guide

### curiosity_ocean_workspace

- Read `units/curiosity_ocean_workspace/behavior.yaml` for current prompt, attachment, streaming, and rendering behavior.
- Read `units/curiosity_ocean_workspace/bindings.yaml` for the canonical Next.js route and auth binding.
- Read `units/curiosity_ocean_workspace/unit_decomposition.yaml` for candidate component cuts only.
- Filter `wire_contracts.yaml` and `cross_unit_state.yaml` for `curiosity_ocean_workspace`.
- Completion evidence: authenticated action selection, multi-attachment queue, real progress/error display, and artifact metadata retained by execution ID.

### web_service_discovery

- Read `units/web_service_discovery/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts/state/seams for `web_service_discovery` or `apps/web/app/api/service-discovery/route.ts`.
- Completion evidence: no inferred executable capabilities, no success-shaped live fallback, schema validation, and 404/503 semantics verified.

### web_ocean_stream

- Read `units/web_ocean_stream/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts/state/seams for `web_ocean_stream` and the SSE seam.
- Completion evidence: existing token streaming preserved, typed ordered events added, upstream failure/cancel/empty-body cases observed without fabricated tokens.

### web_ocean_document

- Read `units/web_ocean_document/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts/state/seams for `web_ocean_document` and document attachment/artifact rows.
- Completion evidence: verified principal, tenant-owned attachment, checksum, provider status preservation, and queryable artifact metadata.

### api_ocean_action_surface

- Read `units/api_ocean_action_surface/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts/state/seams for `api_ocean_action_surface` and `apps/api/main.py`.
- Completion evidence: Action Fabric router mounted, labs dispatched through authorization/audit, synthetic ASI completion removed, and dependency-aware health.

### ocean_multimodal_api

- Read `units/ocean_multimodal_api/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts/state/seams for `ocean_multimodal_api`.
- Completion evidence: manifest adapter passes each mode, invalid input is 422, Ollama/model outage is unavailable, and output/confidence is never invented.

### saas_orchestrator_prototype

- Read `units/saas_orchestrator_prototype/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global contracts for `saas_orchestrator_prototype`.
- Completion evidence: no new production dependency on this prototype; useful request/correlation fields are represented in the new contract; arbitrary proxying is excluded.

### auto_registry_cli

- Read `units/auto_registry_cli/behavior.yaml`, `bindings.yaml`, and `unit_decomposition.yaml`.
- Filter global rows for `auto_registry_cli` or `core/auto_registry.py`.
- Completion evidence: retained only as an inventory importer; static source parsing never marks a provider healthy or executable.

## Concrete delivery slices

### Slice 0 — Truth gate

- Remove fabricated tool/activity defaults from the executable UX path.
- Remove synthetic `completed` ASI results.
- Separate deployment inventory, registration lease, and verified health.
- Acceptance: no data returns 204/404/503 as appropriate; no unavailable provider appears executable.

### Slice 1 — One manifest and authoritative registry

- Define the versioned capability manifest with ID, version, provider, transport, input/output schemas, scopes, approval policy, idempotency, timeout, health probe, and result renderer hints.
- Register only two real capabilities first: Ocean document scan and one existing validation lab.
- Acceptance: both manifests validate, failed health makes them unavailable, and the web gateway has one authoritative discovery endpoint.

### Slice 2 — Principal, permission, and audit

- Resolve the user/tenant from the server auth session; discard caller identity headers.
- Persist authorization decision and append-only audit events before dispatch.
- Acceptance: unauthorized dispatch never reaches a provider; every allowed/denied action has principal, capability version, trace ID, reason, and timestamp.

### Slice 3 — Durable execution runtime

- Create execution, provider-attempt, event, and artifact metadata records.
- Dispatch through provider adapters with deadlines and idempotency rules.
- Acceptance: queued/running/completed/failed/cancelled survive process restart; retries cannot duplicate a confirmed artifact.

### Slice 4 — Existing Curiosity Ocean as the motor surface

- Evolve `InputComposer` instead of creating another dashboard or repository.
- Add multi-attachment registration, explicit/automatic capability selection, approval panel, event progress, and schema-driven result rendering.
- Acceptance: prompt + document -> discovery -> authorization -> real document scan -> progress -> artifact, entirely from the existing canonical page.

### Slice 5 — Laboratory vertical path

- Add the validation lab adapter without moving ML/Excel dependencies into the control plane.
- Acceptance: prompt or explicit action -> manifest -> permission -> lab -> real LabResult/artifact -> renderer; provider failure remains failed.

### Slice 6 — OS-CLX federation

- Move/host the authoritative registry, router, policy, and ledger in OS-CLX after that repository is audited.
- Keep `clisonix.com` as product shell/BFF/provider integration using the frozen wire contracts in this artifact set.
- Acceptance: clisonix.com contains no second authoritative registry and continues both vertical paths through OS-CLX.

## Stop conditions

- Do not add another engine, repository, dashboard, or inferred capability.
- Do not proceed to a third capability until the two vertical paths pass real outage, authorization, restart, cancellation, and artifact provenance checks.

