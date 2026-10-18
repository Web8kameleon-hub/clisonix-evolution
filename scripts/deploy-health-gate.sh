#!/usr/bin/env bash
set -euo pipefail

WEB_HEALTH_URL="${WEB_HEALTH_URL:-http://127.0.0.1:3000/api/health-check}"
API_HEALTH_URL="${API_HEALTH_URL:-http://127.0.0.1:8000/health}"
OCEAN_HEALTH_URL="${OCEAN_HEALTH_URL:-http://127.0.0.1:8030/health}"
CHECK_RETRIES="${CHECK_RETRIES:-20}"
CHECK_SLEEP_SECONDS="${CHECK_SLEEP_SECONDS:-3}"

check_url() {
  local name="$1"
  local url="$2"
  local ok=0

  for _ in $(seq 1 "$CHECK_RETRIES"); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)"
    if [[ "$code" == "200" ]]; then
      ok=1
      break
    fi
    sleep "$CHECK_SLEEP_SECONDS"
  done

  if [[ "$ok" -ne 1 ]]; then
    echo "[health-gate] FAIL: $name -> $url"
    return 1
  fi

  echo "[health-gate] OK: $name -> $url"
}

check_url "web" "$WEB_HEALTH_URL"
check_url "api" "$API_HEALTH_URL"
check_url "ocean-core" "$OCEAN_HEALTH_URL"

echo "[health-gate] All core services are healthy"
