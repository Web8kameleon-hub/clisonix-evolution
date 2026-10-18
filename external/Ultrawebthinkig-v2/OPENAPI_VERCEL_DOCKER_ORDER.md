# OpenAPI + Vercel Frontend + Docker Backend (Absolute Order)

## 1) Generate canonical internal API catalog

```powershell
node scripts/generate-openapi.mjs
```

Output: `openapi/internal-openapi.json`

## 2) Expose OpenAPI from frontend runtime

- Endpoint: `GET /api/openapi`
- Convenience alias: `GET /openapi.json` (configured in `vercel.json` rewrite)

## 3) Deploy frontend to Vercel

- `vercel.json` keeps frontend on Vercel.
- Backend traffic goes through rewrite:
  - `/backend/:path*` -> `https://api.ultraweb.ai/:path*`

## 4) Run backend as Docker microservices

```powershell
docker compose -f docker-compose.backend.yml up -d --build
```

Services:

- `backend-api` on `:8080`
- `ultracom` on `:8000`
- `redis` on `:6379`
- `postgres` on `:5432`

## 5) Required environment variables

- `BACKEND_PROXY_URL` (for local Next rewrite target, defaults to `http://127.0.0.1:8080`)
- `POSTGRES_PASSWORD` (for docker compose)
- Optional:
  - `OLLAMA_URL`
  - `CORS_ORIGINS`
  - `MANAGER_ROUTE_SENSOR`
  - `MANAGER_ROUTE_ANALYTICS`
  - `MANAGER_ROUTE_NEWS`

## 6) Frontend runtime routing standard

- Internal APIs: `/api/...`
- Backend microservices: `/backend/...`
- Do not hardcode `localhost` in UI runtime paths.
