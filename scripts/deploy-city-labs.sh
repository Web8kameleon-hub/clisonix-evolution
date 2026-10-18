#!/usr/bin/env bash
set -euo pipefail

ROOT="${CITY_LABS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_FILE="${CITY_LABS_COMPOSE:-$ROOT/docker-compose.city-labs.yml}"
PROJECT="${CITY_LABS_PROJECT:-clisonix-city-labs}"
REGISTRY_URL="${CITY_LABS_REGISTRY_URL:-http://127.0.0.1:9130}"
WAIT_SECONDS="${CITY_LABS_WAIT_SECONDS:-120}"
FABRIC_NETWORK="${CLISONIX_FABRIC_NETWORK:-clisonix-swarm}"

cd "$ROOT"

ensure_fabric() {
  if docker network inspect "$FABRIC_NETWORK" >/dev/null 2>&1; then
    return
  fi

  if [[ "$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo inactive)" == "inactive" ]]; then
    echo "==> Initializing single-node Swarm for attachable Clisonix fabric"
    docker swarm init --advertise-addr "$(hostname -I | awk '{print $1}')" >/dev/null
  fi

  echo "==> Creating shared attachable fabric: $FABRIC_NETWORK"
  docker network create --driver overlay --attachable "$FABRIC_NETWORK" >/dev/null
}

ensure_fabric
export CLISONIX_FABRIC_NETWORK="$FABRIC_NETWORK"

echo "==> Validating City Labs compose"
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" config >/tmp/clisonix-city-labs.compose.yml

echo "==> Building shared City Lab image"
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" build

echo "==> Starting City Labs on the shared Clisonix fabric"
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" up -d --remove-orphans

echo "==> Waiting for registry"
deadline=$((SECONDS + WAIT_SECONDS))
until curl -fsS "$REGISTRY_URL/health" >/dev/null 2>&1; do
  if (( SECONDS >= deadline )); then
    echo "ERROR: City Labs registry did not become healthy within ${WAIT_SECONDS}s" >&2
    docker compose -p "$PROJECT" -f "$COMPOSE_FILE" ps || true
    docker compose -p "$PROJECT" -f "$COMPOSE_FILE" logs --tail=100 city-labs-registry || true
    exit 1
  fi
  sleep 2
done

echo "==> Requiring 23/23 live runtimes"
until python3 scripts/city-labs-smoke.py --registry "$REGISTRY_URL"; do
  if (( SECONDS >= deadline )); then
    echo "ERROR: City Labs failed 23/23 health gate" >&2
    docker compose -p "$PROJECT" -f "$COMPOSE_FILE" ps || true
    exit 1
  fi
  sleep 3
done

echo "==> PASS: Clisonix City Labs 23/23 runtime-healthy"
echo "==> Note: analysis-capable is a separate gate and requires real ANALYSIS_UPSTREAM bindings."
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" ps
