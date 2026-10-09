# Clisonix Env Usage Standard

This file defines a single env strategy to eliminate env-file confusion.

## 1. Canonical Env Files

- Production runtime env: `.env.production`
- Production template: `.env.production.template`
- Compose selector variable: `CLISONIX_ENV_FILE=.env.production`

Do not use `.env`, `.env.unified`, `.env.sample`, `.env.template` for production deployment.

## 2. Canonical Deploy Flow

1. Copy template to runtime file.
2. Fill real values from secret manager.
3. Run preflight env validation.
4. Deploy with explicit env-file.

```powershell
Copy-Item .env.production.template .env.production
powershell -ExecutionPolicy Bypass -File .\scripts\preflight-env.ps1 -EnvFile .env.production
docker compose --env-file .env.production up -d
```

```bash
cp .env.production.template .env.production
bash ./scripts/preflight-env.sh .env.production
docker compose --env-file .env.production up -d
```

## Required Variables (Current Compose)

- `POSTGRES_PASSWORD`
- `MONGO_ROOT_PASSWORD`
- `NEO4J_PASSWORD`
- `MINIO_ROOT_PASSWORD`
- `GRAFANA_ADMIN_PASSWORD`
- `KITCHEN_RUN_API_KEY`

## Rules

- Never commit `.env.production`
- Never put real secrets in templates
- Always use `--env-file .env.production` in production commands
- Keep `CLISONIX_ENV_FILE` aligned with `.env.production`
