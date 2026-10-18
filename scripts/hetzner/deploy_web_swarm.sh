#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/clisonix.com}"
ENV_FILE="${WEB_DEPLOY_ENV_FILE:-.env}"
STACK_NAME="${SWARM_STACK_NAME:-clisonix-next}"
NETWORK_NAME="${SWARM_NETWORK:-clisonix-swarm}"
SERVICE_NAME="${STACK_NAME}_web"

cd "$DEPLOY_PATH"
COMMIT_SHA="$(git rev-parse --short=12 HEAD)"
IMAGE_TAG="clisonix-web:deploy-${COMMIT_SHA}"

[[ -f "$ENV_FILE" ]] || {
  echo "Missing environment file: $ENV_FILE"
  exit 1
}

read_env() {
  local key="$1"
  local value
  value="$(grep -m1 -E "^${key}=" "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  printf '%s' "$value"
}

AUTH_SECRET="${AUTH_SECRET:-$(read_env AUTH_SECRET)}"
NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-$(read_env NEXTAUTH_SECRET)}"
AUTH_SECRET="${AUTH_SECRET:-$NEXTAUTH_SECRET}"
NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-$AUTH_SECRET}"
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY:-$(read_env NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)}"
STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY:-$(read_env STRIPE_PUBLISHABLE_KEY)}"
NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID="${NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID:-$(read_env NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID)}"
[[ -n "$AUTH_SECRET" && -n "$NEXTAUTH_SECRET" ]] || {
  echo "AUTH_SECRET or NEXTAUTH_SECRET is required"
  exit 1
}

docker service inspect "$SERVICE_NAME" >/dev/null

docker build \
  --file apps/web/Dockerfile \
  --tag "$IMAGE_TAG" \
  --build-arg "NEXT_PUBLIC_AUTH_PROVIDER=clisonix" \
  --build-arg "NEXT_PUBLIC_API_BASE=/api" \
  --build-arg "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY:-${STRIPE_PUBLISHABLE_KEY:-}}" \
  --build-arg "NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID=${NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID:-}" \
  --build-arg "AUTH_SECRET=${AUTH_SECRET}" \
  --build-arg "NEXTAUTH_SECRET=${NEXTAUTH_SECRET}" \
  apps/web

docker service update \
  --image "$IMAGE_TAG" \
  --env-add "API_INTERNAL_URL=http://api:8000" \
  --env-add "OCEAN_CORE_URL=http://${STACK_NAME}_ocean-core:8030" \
  --env-add "OCEAN_INTERNAL_URL=http://${STACK_NAME}_ocean-core:8030" \
  --update-order start-first \
  --update-parallelism 1 \
  --update-failure-action rollback \
  --update-monitor 120s \
  --rollback-order start-first \
  --detach=false \
  "$SERVICE_NAME"

for attempt in $(seq 1 60); do
  update_state="$(docker service inspect "$SERVICE_NAME" --format '{{if .UpdateStatus}}{{.UpdateStatus.State}}{{else}}completed{{end}}')"
  if [[ "$update_state" == "completed" ]]; then
    break
  fi
  if [[ "$update_state" == "rollback_completed" || "$update_state" == "paused" ]]; then
    echo "Web service update failed: $update_state"
    exit 1
  fi
  if [[ "$attempt" -eq 60 ]]; then
    echo "Web service update did not complete: $update_state"
    exit 1
  fi
  sleep 2
done

for path in /api/health-check /sign-in /sign-up /zurich /modules/curiosity-ocean; do
  docker run --rm --network "$NETWORK_NAME" python:3.14-bookworm \
    python -c "import urllib.request; urllib.request.urlopen('http://web:3000${path}', timeout=20)"
done

if docker inspect clisonix-web >/dev/null 2>&1; then
  docker rm -f clisonix-web
fi

if docker inspect clisonix-nginx >/dev/null 2>&1; then
  docker exec clisonix-nginx nginx -t
  docker exec clisonix-nginx nginx -s reload
fi

echo "Web Swarm rollout completed with start-first health gating."
