# Clisonix Release Gate Checklist

Use this checklist before every production deployment. If one mandatory gate fails, the release is blocked.

## 1. Security Gate (Mandatory)

- [ ] No hardcoded secrets in tracked files (`docker-compose*.yml`, app configs, scripts)
- [ ] Required secrets are set in environment/secret manager (`POSTGRES_PASSWORD`, `MONGO_ROOT_PASSWORD`, `NEO4J_PASSWORD`, `MINIO_ROOT_PASSWORD`, `GRAFANA_ADMIN_PASSWORD`)
- [ ] Secret scan executed successfully
- [ ] TLS certificates valid for target domain

## 2. Health Gate (Mandatory)

- [ ] Core services report healthy: API, ALBA, ALBI, JONA, Redis, PostgreSQL
- [ ] Dependency-aware health checks pass (service + required dependency reachability)
- [ ] No service returns fake healthy status when a dependency is down

## 3. Contract Gate (Mandatory)

- [ ] Service ports and URLs match the source of truth in `docker-compose.yml`
- [ ] Documentation reflects current production ports (notably ALBI on `6680`)
- [ ] Public API changes are versioned and documented

## 4. Observability Gate (Mandatory)

- [ ] Metrics scraped successfully in Prometheus
- [ ] Dashboards load for API + core agents
- [ ] Alert rules enabled for availability, latency, and error rate
- [ ] SLO thresholds defined and attached to owning team

## 5. Runtime Segmentation Gate (Mandatory)

- [ ] Production deployment excludes research-only services by default
- [ ] Research services run only via explicit profile selection (e.g., `--profile research`)
- [ ] Production compose command does not include research profile unless explicitly approved

## 6. Smoke Test Gate (Mandatory)

- [ ] `GET /health` and `GET /status` pass on public and core internal services
- [ ] End-to-end request path succeeds: web -> api -> core dependency
- [ ] Billing/auth critical paths tested in target environment

## 7. Rollback Gate (Mandatory)

- [ ] Previous stable image/tag is available
- [ ] Rollback command verified
- [ ] On-call owner assigned for release window

## Recommended Commands

```bash
# Validate compose after env injection
pwsh -ExecutionPolicy Bypass -File .\scripts\preflight-env.ps1 -EnvFile .env.production

# Validate compose after env injection (explicit)
docker compose --env-file .env.production config

# Start only default (non-research) services
docker compose --env-file .env.production up -d

# Verify health quickly
docker compose ps
```

## Exit Criteria

Release is approved only when all mandatory gates are checked and signed by deployment owner.
