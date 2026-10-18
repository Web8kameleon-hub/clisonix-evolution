#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/clisonix.com}"
STACK_NAME="${SWARM_STACK_NAME:-clisonix-next}"
NETWORK_NAME="${SWARM_NETWORK:-clisonix-swarm}"
JONA_SERVICE="${STACK_NAME}_jona"
API_SERVICE="${STACK_NAME}_api"

cd "$DEPLOY_PATH"
COMMIT_SHA="$(git rev-parse --short=12 HEAD)"
IMAGE_TAG="clisonix-jona:deploy-${COMMIT_SHA}"

docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 ||
  docker network create --driver overlay --attachable "$NETWORK_NAME"

docker build --file Dockerfile.jona --tag "$IMAGE_TAG" .

if docker service inspect "$JONA_SERVICE" >/dev/null 2>&1; then
  docker service update \
    --image "$IMAGE_TAG" \
    --update-order start-first \
    --update-parallelism 1 \
    --update-failure-action rollback \
    --update-monitor 90s \
    --rollback-order start-first \
    --detach=false \
    "$JONA_SERVICE"
else
  docker service create \
    --name "$JONA_SERVICE" \
    --network "name=${NETWORK_NAME},alias=jona" \
    --mount "type=volume,source=jona-audio,target=/app/data/jona_audio" \
    --constraint "node.role==manager" \
    --restart-condition on-failure \
    --detach=false \
    "$IMAGE_TAG"
fi

for attempt in $(seq 1 45); do
  container_id="$(
    docker service ps "$JONA_SERVICE" \
      --filter desired-state=running \
      --format '{{.ID}}' |
      head -n 1 |
      xargs -r docker inspect --format '{{.Status.ContainerStatus.ContainerID}}'
  )"
  if [[ -n "$container_id" ]] &&
    [[ "$(docker inspect "$container_id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}')" == "healthy" ]]; then
    break
  fi
  if [[ "$attempt" -eq 45 ]]; then
    docker service ps "$JONA_SERVICE" --no-trunc
    exit 1
  fi
  sleep 4
done

if docker inspect clisonix-api >/dev/null 2>&1; then
  docker network connect "$NETWORK_NAME" clisonix-api 2>/dev/null || true
fi

docker service inspect "$API_SERVICE" >/dev/null
docker service update \
  --force \
  --limit-memory 768M \
  --reserve-memory 256M \
  --health-start-period 5m \
  --update-order start-first \
  --update-parallelism 1 \
  --update-failure-action rollback \
  --update-monitor 360s \
  --rollback-order start-first \
  --detach=false \
  "$API_SERVICE"

docker run --rm --network "$NETWORK_NAME" python:3.14-bookworm \
  python -c "import urllib.request; urllib.request.urlopen('http://api:8000/api/jona/health', timeout=20)"

echo "JONA and API Swarm rollout completed with health gating."
