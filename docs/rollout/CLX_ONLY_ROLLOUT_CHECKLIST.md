# CLX-Only Rollout Checklist (10% -> 100%)

## 10% - Branch + Baseline

- [ ] Branch active: `feature/clx-only-rollout`
- [ ] Baseline proves XLC path is fast (`/xlc/route`)
- [ ] Baseline proves classic chat path is model-dependent

## 25% - App Guardrail

- [ ] `CLX_ONLY` feature flag wired in app config
- [ ] `/api/v1/chat/stream` requires `xlc_enabled=true` when `CLX_ONLY=true`
- [ ] No fallback to classic LLM path in `CLX_ONLY=true`
- [ ] Error semantics correct (`422` for invalid request, `503` for unavailable engine)

## 40% - Gateway Hard Mode

- [ ] Gateway allowlist includes only:

  - [ ] `/api/ocean/xlc/health`
  - [ ] `/api/ocean/xlc/route`
  - [ ] `/api/ocean/xlc/route/stream`
  - [ ] `/api/ocean/xlc/inspect`

- [ ] Gateway denies all other `/api/ocean/*` routes with `403`

## 60% - SLO Gate

- [ ] Gate script available: `scripts/clx_only_gate.ps1`
- [ ] Gate checks:

  - [ ] p95 `/xlc/route`
  - [ ] p95 `/api/v1/chat/stream` with XLC payload
  - [ ] success-rate

- [ ] Gate thresholds aligned with production targets

## 90% - Live Smoke on Hetzner

- [ ] Smoke script available: `scripts/hetzner/post_deploy_clx_only_smoke.sh`
- [ ] Positive checks return `200` on XLC routes
- [ ] Negative checks return `403` on non-XLC ocean routes
- [ ] Capture output and store in deploy evidence

## 100% - Cutover + Monitoring

- [ ] Set `CLX_ONLY=true` in production env
- [ ] Reload nginx with updated production config
- [ ] Run gate + smoke scripts post-deploy
- [ ] Monitor 24h:

  - [ ] success-rate
  - [ ] p95 latency
  - [ ] error codes (`422/403/503`) distribution

- [ ] Rollback plan ready and tested (`CLX_ONLY=false` + previous nginx config)

## Deploy Commands (Suggested)

```bash
# 1) App guardrail + gateway config deployed
# 2) Enable CLX-only mode
export CLX_ONLY=true

# 3) Run gate from admin host (PowerShell)
./scripts/clx_only_gate.ps1

# 4) Run live smoke on server
bash scripts/hetzner/post_deploy_clx_only_smoke.sh https://www.clisonix.com
```
