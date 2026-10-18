# Project Structure

## Project type

Federated AI platform monorepo with a canonical Next.js product shell, a FastAPI gateway, independently deployed AI/laboratory services, and Docker Compose as the active local deployment inventory.

## Runtime boundary relevant to CLX Action Fabric

| Layer | Active location | Evidence | Action Fabric responsibility |
|---|---|---|---|
| Product shell | `apps/web` | `package.json:12`; `docker-compose.yml:698` | Prompt/attachment input, action selection, approvals, progress, artifact rendering |
| Browser-facing gateway | `apps/web/app/api` | `apps/web/app/api/ocean/stream/route.ts:369` | Authenticate the principal, translate browser requests, preserve streaming errors |
| Platform API | `apps/api/main.py` | `docker-compose.yml:573`; `apps/api/main.py:1026` | Host the compatibility router and connect deployed services |
| AI runtime | `ocean-core` | `docker-compose.yml:253` | Chat, document, vision, audio, and reasoning providers |
| Multimodal provider | `ocean-core/ocean_multimodal.py` | `docker-compose.yml:484`; `ocean-core/ocean_multimodal.py:459` | Provider adapter candidate; not the capability registry |
| Laboratory runtime | `hybrid_saas_platform/labs` through Ocean hub | `apps/api/ocean_central_hub.py:198` | Existing lab execution and artifact production |
| Deployment inventory | `docker-compose.yml` | `docker-compose.yml:253`; `docker-compose.yml:573`; `docker-compose.yml:698` | Declared topology only; it is not proof that a capability is healthy |

## Functional domains

- Conversation and multimodal interaction: `apps/web/app/modules/curiosity-ocean`, `apps/web/app/api/ocean`, `ocean-core`.
- Service and capability discovery prototypes: `core/auto_registry.py`, `services/registry.py`, `services/internal_agi/module_registry.py`, `apps/web/app/api/service-discovery/route.ts`.
- Execution prototypes: `apps/api/main.py`, `apps/api/ocean_central_hub.py`, `saas_services_orchestrator_v3.py`.
- Artifact production: `hybrid_saas_platform/labs/lab_executor.py`; document ingestion responses exposed by Ocean.
- Identity: browser-side auth abstraction in `apps/web`; action routes currently forward caller-controlled user identifiers.
- Operations: Docker Compose health checks, service-specific `/health` endpoints, Prometheus/Grafana components.

## Structural finding

The repository already contains the product input surface, provider runtimes, service catalogs, execution methods, and artifact-shaped outputs. They are not joined by one manifest, principal, execution ledger, or result envelope. The Action Fabric is therefore a contract-and-control-plane consolidation, not a new engine.

