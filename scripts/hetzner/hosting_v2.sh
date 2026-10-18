#!/usr/bin/env bash
set -euo pipefail

cd "${DEPLOY_PATH:-/opt/clisonix.com}"
COMPOSE_FILE="${CLISONIX_COMPOSE_FILE:-compose-hosting.yml}"
ENV_FILE="${CLISONIX_ENV_FILE:-.env.production}"
ACTION="${1:-inventory}"
shift || true

python3 scripts/hetzner/hosting_inventory.py --compose "$COMPOSE_FILE"

if [[ "$ACTION" == inventory ]]; then
  exit 0
fi
if [[ "$ACTION" != check && "$ACTION" != deploy ]]; then
  echo "Usage: hosting_v2.sh [inventory|check|deploy SERVICE...]" >&2
  exit 2
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing production environment file: $ENV_FILE" >&2
  exit 1
fi

# Compose interpolates every service, including those outside a selected batch.
# Fail before any deployment when a required production value is absent.
for key in POSTGRES_PASSWORD NODEDB_FLUID_URL ULTRA_MS_POSTGRES_PASSWORD; do
  if ! grep -Eq "^${key}=.+" "$ENV_FILE"; then
    echo "Missing required production value in $ENV_FILE: $key" >&2
    exit 1
  fi
done

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config -q
python3 scripts/guardrails/repo_integrity_guard.py

if [[ "$ACTION" == check ]]; then
  echo "Production hosting configuration is valid."
  exit 0
fi
if [[ "$#" -eq 0 ]]; then
  echo "Specify the services to deploy, or pass all for the full manifest." >&2
  exit 2
fi
if [[ "$1" == all && "$#" -eq 1 ]]; then
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build
else
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build "$@"
fi
python3 scripts/hetzner/hosting_inventory.py --compose "$COMPOSE_FILE"
