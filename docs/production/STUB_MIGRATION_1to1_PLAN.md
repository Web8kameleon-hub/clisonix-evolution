# Clisonix Stub → Real Services Migration (1:1)

## Objective
Replace all placeholder/stub services (`docker-stubs/service_stub.py` and inline `python -c` demo APIs) with real production microservices: dedicated repo path, Dockerfile, business API, observability, tests, readiness/liveness.

## Hard Rules
- No fake endpoints in production.
- Every service must expose: `/health`, `/status`, and at least one real business endpoint.
- Each service must include:
  - `Dockerfile`
  - `requirements.txt` or `package.json`
  - structured logs
  - readiness + liveness checks
  - minimal integration test
- Deploy all services on single network: `clisonix-cloud_default`.

## Current Placeholder Inventory (from docker-compose.75-services.yml)

### A) Direct stubs (`docker-stubs/service_stub.py`) — 12 services
1. `alba`
2. `asi`
3. `alphabet-layers`
4. `liam`
5. `alda`
6. `alba-idle`
7. `blerina`
8. `cycle-engine`
9. `agiem`
10. `reporting`
11. `quantum`
12. `agent-telemetry`

### B) Inline demo FastAPI (`python -c "...FastAPI..."`) — 34 services
- `datasource-*` group
- `lab-*` group
- several support services (`cognitive-engine`, `adaptive-router`, `health-monitor`)

## Priority Batches (approved order)

### Batch 1 — Critical Control Plane (Week 1)
1. `agent-telemetry`
2. `reporting`
3. `cycle-engine`
4. `agiem`

**Acceptance**
- Real telemetry ingestion endpoint with persisted events.
- Real reporting pipeline (not health-only).
- End-to-end trace from `ocean-core` to telemetry/reporting.

### Batch 2 — Datasource Services (Week 2)
- `datasource-europe`, `datasource-americas`, `datasource-asia`, `datasource-india`, `datasource-africa`, `datasource-oceania`, `datasource-central-asia`, `datasource-antarctica`

**Acceptance**
- Each source has real upstream connectors + retry/circuit-breaker.
- `/sources` returns live provider status, not static booleans.

### Batch 3 — Lab Services (Week 3-4)
- All `lab-*` services (23 total)

**Acceptance**
- Each lab has a real domain API contract and business function.
- No inline `python -c` execution in compose.

### Batch 4 — Persona/AI Satellite Services (Week 5)
- `alba`, `asi`, `alphabet-layers`, `liam`, `alda`, `alba-idle`, `blerina`, `quantum`

**Acceptance**
- Real AI routing/processing behavior.
- Measurable throughput and error metrics.

## Implementation Template (for each service)
1. Create folder: `services/<service-name>/`
2. Add:
   - `main.py` (or app entry)
   - `Dockerfile`
   - `requirements.txt`
   - `tests/test_smoke.py`
3. Define contracts:
   - `GET /health`
   - `GET /status`
   - `POST /api/v1/<business-action>`
4. Add observability:
   - request id, latency, error rate
   - basic counters and logs
5. Replace compose command:
   - remove `docker-stubs/service_stub.py`
   - remove inline `python -c`
   - use real image build context

## Deployment Strategy
- Blue/green per batch.
- 10% traffic canary for first 30 minutes.
- Auto-rollback if:
  - 5xx > 2%
  - P95 latency > 2x baseline
  - health check fail > 3 consecutive intervals

## Done Criteria
A service is considered migrated only if:
- No stub code path exists.
- Integration tests pass in CI.
- Service appears healthy in production for 24h.
- Ocean integration endpoint confirms connectivity when applicable.
