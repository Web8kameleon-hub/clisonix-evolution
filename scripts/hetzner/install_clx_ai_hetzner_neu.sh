#!/usr/bin/env bash
set -Eeuo pipefail

# Install and activate CLX AI stack on Hetzner host.
# Usage:
#   bash scripts/hetzner/install_clx_ai_hetzner_neu.sh [/opt/clisonix-cloud]

PROJECT_DIR="${1:-/opt/clisonix-cloud}"
ENV_FILE="${CLISONIX_ENV_FILE:-.env.production}"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[CLX_INSTALL] Missing command: $cmd"
    exit 1
  fi
}

require_cmd docker
require_cmd git
require_cmd curl

if [ ! -d "$PROJECT_DIR" ]; then
  echo "[CLX_INSTALL] Project directory not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "[CLX_INSTALL] Project: $PROJECT_DIR"
echo "[CLX_INSTALL] Pull latest source"
git fetch --all --prune
git checkout main
git pull --ff-only origin main

echo "[CLX_INSTALL] Build CLX AI containers"
docker compose --env-file "$ENV_FILE" build clx-agent api ocean-core

echo "[CLX_INSTALL] Start CLX AI services"
docker compose --env-file "$ENV_FILE" up -d clx-agent reporting api ocean-core

echo "[CLX_INSTALL] Wait for health checks"
sleep 4

check_http() {
  local url="$1"
  local label="$2"
  local code
  code="$(curl -sS -o /tmp/clx_install_check.out -w '%{http_code}' "$url" || true)"
  if [ "$code" != "200" ]; then
    echo "[CLX_INSTALL] FAIL $label ($url) -> HTTP $code"
    cat /tmp/clx_install_check.out || true
    exit 1
  fi
  echo "[CLX_INSTALL] OK $label"
}

check_http "http://127.0.0.1:7778/health" "clx-agent health"
check_http "http://127.0.0.1:8001/health" "reporting health"
check_http "http://127.0.0.1:8000/api/reporting/health" "api reporting proxy health"

echo "[CLX_INSTALL] Container status"
docker compose --env-file "$ENV_FILE" ps clx-agent reporting api ocean-core

echo "[CLX_INSTALL] DONE"
