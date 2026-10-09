#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/opt/clisonix-cloud"
COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="/root/clisonix-backups"
HEALTH_URL="http://localhost:8030/health"
RETRIES=3
SLEEP_SECONDS=10

echo "[OceanDeploy] Starting ocean-core deployment"
cd "$ROOT_DIR"
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/docker-compose.yml.$TIMESTAMP"
cp "$COMPOSE_FILE" "$BACKUP_FILE"
echo "[OceanDeploy] Backup saved: $BACKUP_FILE"

if ! docker compose -f "$COMPOSE_FILE" up -d --build ocean-core; then
  echo "[OceanDeploy] Deploy command failed. Rolling back compose file"
  cp "$BACKUP_FILE" "$COMPOSE_FILE"
  docker compose -f "$COMPOSE_FILE" up -d ocean-core
  exit 1
fi

for attempt in $(seq 1 "$RETRIES"); do
  if curl -fsS "$HEALTH_URL" >/dev/null; then
    echo "[OceanDeploy] Health check passed on attempt $attempt"
    exit 0
  fi
  echo "[OceanDeploy] Health check failed ($attempt/$RETRIES), waiting ${SLEEP_SECONDS}s..."
  sleep "$SLEEP_SECONDS"
done

echo "[OceanDeploy] Health checks failed after $RETRIES attempts. Rolling back."
cp "$BACKUP_FILE" "$COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" up -d ocean-core
exit 1
