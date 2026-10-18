# Technology Stack

## Canonical web runtime

- Next.js 16.2.3, React 18.3.1, TypeScript, App Router: `apps/web/package.json:40-48`.
- Zustand is already installed: `apps/web/package.json:49`; no new client state package is required.
- Zod is already available for manifest/result validation: `apps/web/package.json:71`.
- The canonical web build is `apps/web`: root `package.json:12-28` and `docker-compose.yml:698-754`.
- The separate `frontend` tree is not part of the active Compose or root web scripts and is excluded from the migration boundary.

## Canonical API runtime

- FastAPI, Uvicorn, Pydantic 2, SQLAlchemy, psycopg, Alembic, httpx, Redis client dependencies: `apps/api/requirements.txt:1-17`.
- PostgreSQL and Redis are already required by the deployed API: `docker-compose.yml:588-600`.
- Ocean and multimodal services use FastAPI/Pydantic/httpx: `ocean-core/ocean_multimodal.py:19-21`.

## Existing protocol support

- JSON and SSE are active in the browser/Ocean path: `apps/web/app/api/ocean/stream/route.ts:359-369`.
- CBOR is active in the document proxy and Ocean hub: `apps/web/app/api/ocean/document/route.ts:66-70`; `apps/api/ocean_central_hub.py:29-35`.
- Multipart file transfer is active in the document proxy: `apps/web/app/api/ocean/document/route.ts:211-240`.
- HTTP provider calls are implemented with `fetch`/httpx.

## Blockers that the Action Fabric must remove

1. `apps/web/app/api/service-discovery/route.ts:160-220` infers capabilities from service names instead of consuming declared manifests.
2. `apps/web/app/api/service-discovery/route.ts:641-670` returns a successful compose/catalog response while the live registry is unavailable.
3. `services/internal_agi/module_registry.py:142-203` initializes modules as active with default health rather than verified health.
4. `ocean-core/ocean_multimodal.py:439-453` reports every pipeline online without probing Ollama/models.
5. `apps/api/main.py:2212-2227` labels the API operational independently of dependency state.
6. `apps/web/components/LiveChatTools.tsx:30-76` contains fabricated default tools/activity; it is also not imported by another TSX file.
7. `apps/api/main.py:4042-4054` returns completed ASI execution text without executing an agent.
8. Action requests accept/forward caller-controlled `user_id` or `X-User-ID`: `apps/web/app/modules/curiosity-ocean/page.tsx:1032-1036`; `apps/web/app/api/ocean/document/route.ts:150-160`.
9. The backend discovery router imports `get_registry` from `main`, but `apps/api/main.py` defines no such symbol and does not include that router: `apps/api/routes/service_discovery.py:18-24`.

## Dependency rule

Action Fabric core may use the existing API/web dependencies. ML and document/Excel dependencies remain inside provider services and are never pulled into the control plane.

