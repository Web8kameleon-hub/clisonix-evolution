# GEX44 Clean Deploy With Ultra Confirmations

## Scope

- Target host: `178.63.89.121`
- Goal: clean production deployment with real services only
- Critical APIs: auth, billing, paywall, ocean curiosity
- Compose file: `docker-compose.unified.yml`

## Rule Zero

- Do not enable mock/fallback demo behavior for production validation.
- If any dependency is missing, return failure and stop deployment.
- Never mark deployment successful without passing all confirmations.

## Phase 0: Identity And Access Confirmation

Run from local workstation:

```bash
ssh -o StrictHostKeyChecking=accept-new root@178.63.89.121 "hostname; whoami; hostname -I"
```

Expected:

- `whoami` is `root`
- host is reachable
- primary IP includes `178.63.89.121`

## Phase 1: Base OS And Runtime

On server:

```bash
apt update
apt install -y git curl ca-certificates docker.io docker-compose-plugin jq
systemctl enable --now docker
docker --version
docker compose version
```

Expected:

- Docker daemon active
- Docker compose plugin available

## Phase 2: Clean Workspace

On server:

```bash
mkdir -p /root/Clisonix-cloud
cd /root/Clisonix-cloud

if [ -d .git ]; then
  git fetch origin
  git checkout main
  git pull --ff-only origin main
else
  git clone https://github.com/Web8kameleon-hub/clisonix.com.git .
fi

git rev-parse --short HEAD
```

Expected:

- repo synced on `main`
- commit hash printed (store for release notes)

## Phase 3: Required Production Secrets Check

Create `.env.production` and verify minimum keys exist:

```bash
cd /root/Clisonix-cloud
cp -n .env.example .env.production || true

required_vars=(
  "STRIPE_SECRET_KEY"
  "STRIPE_WEBHOOK_SECRET"
  "NEXTAUTH_SECRET"
  "NEXT_PUBLIC_API_URL"
  "INTERNAL_API_KEY"
)

missing=0
for v in "${required_vars[@]}"; do
  if ! grep -q "^${v}=" .env.production; then
    echo "MISSING:${v}"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "STOP: missing required env vars"
  exit 1
fi
```

Expected:

- no `MISSING:*` output
- no empty critical values

## Phase 4: Compose Validation And Build

On server:

```bash
cd /root/Clisonix-cloud
docker compose -f docker-compose.unified.yml --env-file .env.production config >/tmp/compose.validated.yaml
docker compose -f docker-compose.unified.yml --env-file .env.production build web api ocean-core user-management blog-paywall
```

Expected:

- `config` command exits 0
- image build exits 0

## Phase 5: Clean Start (Critical Services)

On server:

```bash
cd /root/Clisonix-cloud
docker compose -f docker-compose.unified.yml --env-file .env.production up -d postgres redis web api ocean-core user-management blog-paywall
docker compose -f docker-compose.unified.yml ps
```

Expected:

- containers running
- no crash loop (`restarting`, `exited`, `dead`)

## Phase 6: Ultra Regular Runtime Confirmations

Run every check and fail fast on first hard error.

### 6.1 Core health

```bash
curl -fsS http://127.0.0.1:3000/api/ocean
curl -fsS http://127.0.0.1:8030/api/v1/status
curl -fsS http://127.0.0.1:8020/health
```

Expected:

- valid JSON responses
- no 5xx

### 6.2 Ocean Curiosity functional

```bash
curl -fsS -X POST http://127.0.0.1:3000/api/ocean \
  -H "Content-Type: application/json" \
  -d '{"message":"health check curiosity","stream":false}' | jq .
```

Expected:

- HTTP `200`
- JSON includes `ocean_response`

### 6.3 Billing plans (Stripe-backed)

```bash
curl -i -sS http://127.0.0.1:3000/api/billing/plans
```

Expected:

- `200` with plan list if Stripe configured
- `503` with explicit config error if Stripe key missing

### 6.4 Paywall service direct

```bash
curl -fsS http://127.0.0.1:8020/api/tiers | jq .
curl -fsS -X POST http://127.0.0.1:8020/api/access/check \
  -H "Content-Type: application/json" \
  -d '{"article_id":"eeg-signal-processing-deep-dive","user_token":"free@example.com"}' | jq .
```

Expected:

- tier matrix returned
- access decision returned

### 6.5 Auth flow smoke (backend auth gateway)

```bash
curl -i -sS -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"test@example.com","password":"invalid"}'
```

Expected:

- controlled auth response (`401/403/422`) but not crash

## Phase 7: Evidence Capture

On server:

```bash
mkdir -p /root/deploy-evidence
docker compose -f /root/Clisonix-cloud/docker-compose.unified.yml --env-file /root/Clisonix-cloud/.env.production ps > /root/deploy-evidence/compose-ps.txt
docker compose -f /root/Clisonix-cloud/docker-compose.unified.yml --env-file /root/Clisonix-cloud/.env.production logs --tail=150 web api ocean-core user-management blog-paywall > /root/deploy-evidence/critical-logs.txt
```

Expected:

- `compose-ps.txt` and `critical-logs.txt` available

## Phase 8: Release Gate

Deployment is accepted only if all are true:

- all Phase 6 checks passed
- no crash loop in critical services
- billing/paywall/auth endpoints return deterministic status
- evidence files generated

If any gate fails:

- do not announce success
- keep service private
- fix root cause and rerun from Phase 4
