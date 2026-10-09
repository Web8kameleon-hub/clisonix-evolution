# How to Use Clisonix — Quick Guide

This short guide distills the repository documentation into the minimal steps to get started, integrate, and run the platform.

1) Overview
- Clisonix is a production-ready AI platform for neuroscience, real-time EEG/audio processing, and intelligent web apps.
- Key engines: ASI Trinity (ALBA, ALBI, JONA); SDKs provided for Python and TypeScript.

2) 5-minute Quick Start (developer)
- Prereqs: Node.js 14+/Python 3.8+, Docker (optional).
- Install deps: `pip install -r requirements.txt` or `npm install` in `apps/web`.
- Start backend (dev): `python start_server.py` or `uvicorn app.master:app --reload`.
- Visit: `http://localhost:8000` and API docs at `/docs` (dev).

3) Using the SDKs
- Python: copy `clisonix_sdk.py`, instantiate `ClisonixClient(base_url, token)`.
- TypeScript: import `clisonix_sdk.ts`, `new ClisonixClient({ baseUrl })`.
- Authentication: use JWT (web apps) or `X-API-Key` for server-to-server.
- Examples: health checks, `ask()`, upload EEG/audio, start/stop streams.

4) Postman & API testing
- Import `clisonix-postman-collection.json` and `clisonix-environment-production.json`.
- Set `base_url` and run `GET /health` then the Auth -> Login flow to populate `auth_token`.

5) Deploy & Production notes
- Use `docker-compose.yml` for multi-service deployment or follow `DEPLOYMENT_*` guides in repo.
- Use `.secrets` or secrets manager for STRIPE/SEPA/PAYPAL keys — never commit secrets.

6) Monitoring & Operations
- Grafana and Prometheus dashboards are included; credentials listed in `CLISONIX_USER_GUIDE.md` for dev setups.
- Health endpoints: `/health`, `/status`, `/api/v1/info`.

7) Security (must-read)
- Read `SECURITY.md` before running in production. Use Docker secrets, rotate keys, enable pre-commit secret scanning.

8) Where to read more (essential docs)
- `README.md` — project overview and quick start.
- `INDEX.md` / `MANIFEST.md` — file map and delivery manifest.
- `SDK-README.md` — full SDK usage and examples.
- `OPENAPI-COMPLETE-GUIDE.md` & `openapi.yaml` — API spec and implementation guide.

If you want, I can:
- produce a one-page English homepage microcopy (short bullets) and update the hero copy further, or
- generate a full user-facing `GETTING_STARTED.md` with copyable commands and Postman steps.

---
Generated from repository docs on request.
