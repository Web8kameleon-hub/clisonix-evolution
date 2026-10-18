# Data Model

## Existing source entities

| Entity | Source | Key fields | Persistence |
|---|---|---|---|
| `KnownService` | `apps/web/app/api/service-discovery/route.ts:24` | id, url, category, capabilities, health, runtime, source | Request-local catalog/Compose parse |
| Service registration | `services/registry.py:65` | name, host, port, url, model, capabilities, metadata, heartbeat, expiry | Firestore or process-local memory |
| `ClisonixModule` | `services/internal_agi/module_registry.py:66` | id, type, endpoint, capabilities, status, dependencies, health | Process-local memory |
| Agent registration | `saas_services_orchestrator_v3.py:118` | name, type, version, capabilities, endpoints, max instances | Process-local memory |
| `EngineRequest` / `EngineResponse` | `core/engines/contract.py:115`; `core/engines/contract.py:156` | engine, mode, messages, context; text, tokens, latency, success/error | Not persisted |
| `UserSession` / `DataStream` | `apps/api/ocean_central_hub.py:160`; `apps/api/ocean_central_hub.py:93` | user/session, streams, priority, buffer | Process-local memory |
| `LabResult` | `hybrid_saas_platform/labs/lab_executor.py:30` | status, timing, tests, output, errors | Returned in response |
| `Artifact` | `hybrid_saas_platform/labs/lab_executor.py:70` | artifact id/type/name/content/metadata/created_at | Returned in response |
| `AnalysisResult` | `ocean-core/ocean_multimodal.py:76` | mode, confidence, timing, output, reasoning, errors | Returned in response |

## Missing persistent model

No source entity forms a durable chain from authenticated principal to capability version, authorization decision, execution state, provider attempt, event stream, and artifact provenance.

## Required target entities

These are target contracts, not claims about current persistence:

- `CapabilityManifest`: immutable versioned declaration and input/output JSON Schemas.
- `ProviderRegistration`: provider endpoint, manifest version, deployment source, and last verified health.
- `ActionExecution`: principal, tenant, capability/version, input reference, status, timestamps, correlation/trace IDs.
- `AuthorizationDecision`: requested scopes, policy result, reason, approver when required.
- `ExecutionEvent`: monotonic sequence, stage, severity, real payload reference, timestamp.
- `ArtifactRecord`: execution ID, media type, storage URI, checksum, size, schema, retention metadata.
- `ProviderAttempt`: provider, request/response status, latency, retry number, terminal error.

## Relationships

- One manifest version has many provider registrations.
- One action execution selects exactly one manifest version and may have multiple provider attempts.
- One action execution has ordered execution events and zero or more artifact records.
- Every action execution has one authorization decision before provider dispatch.
- Artifact content stays in the existing storage/provider boundary; the control plane stores metadata and a reference, not fabricated content.

