#!/usr/bin/env bash
set -Eeuo pipefail

WEB_BASE_URL_RAW="${1:-http://127.0.0.1:3000}"
WEB_BASE_URL="$(printf '%s' "${WEB_BASE_URL_RAW}" | tr -d '\r\n' | sed 's/[[:space:]]\+$//')"
NGINX_CONTAINER="${NGINX_CONTAINER:-clisonix-nginx}"
WEB_CONTAINER="${WEB_CONTAINER:-clisonix-web}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ Missing required command: $cmd"
    exit 1
  fi
}

require_cmd docker
require_cmd curl

json_post() {
  local url="$1"
  local payload_file="$2"
  local output_file="$3"

  curl -sS --max-time "${TIMEOUT_SECONDS}" \
    -o "${output_file}" \
    -w 'code=%{http_code} total=%{time_total}s' \
    -H 'Content-Type: application/json' \
    --data @"${payload_file}" \
    "${url}"
}

echo "== [1/6] Docker container status =="
docker ps --filter "name=${WEB_CONTAINER}" --filter "name=${NGINX_CONTAINER}" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo "== [2/6] Nginx syntax =="
docker exec "${NGINX_CONTAINER}" nginx -t

echo "== [3/6] Web health on ${WEB_BASE_URL} =="
curl -fsS --max-time "${TIMEOUT_SECONDS}" -I "${WEB_BASE_URL}" | head -n 1

cat > "${tmp_dir}/ocean.json" <<'JSON'
{"message":"mirmbrema"}
JSON

echo "== [4/6] /api/ocean =="
ocean_result="$(json_post "${WEB_BASE_URL}/api/ocean" "${tmp_dir}/ocean.json" "${tmp_dir}/ocean_response.json")"
echo "${ocean_result}"
head -c 240 "${tmp_dir}/ocean_response.json"; echo

grep -q 'ocean_response\|persona_answer\|response' "${tmp_dir}/ocean_response.json" || {
  echo "❌ /api/ocean response missing expected fields"
  exit 1
}

cat > "${tmp_dir}/ocean_stream.json" <<'JSON'
{"message":"ich spreche deutsch"}
JSON

echo "== [5/6] /api/ocean/stream =="
stream_result="$({
  curl -sS --max-time "${TIMEOUT_SECONDS}" -N \
    -o "${tmp_dir}/ocean_stream.out" \
    -w 'code=%{http_code} total=%{time_total}s' \
    -H 'Content-Type: application/json' \
    -H 'Accept: text/event-stream' \
    --data @"${tmp_dir}/ocean_stream.json" \
    "${WEB_BASE_URL}/api/ocean/stream"
} || true)"
echo "${stream_result}"
head -n 8 "${tmp_dir}/ocean_stream.out" || true

grep -q '^data:' "${tmp_dir}/ocean_stream.out" || {
  echo "❌ /api/ocean/stream did not return SSE data"
  exit 1
}

echo "== [6/6] Success =="
echo "✅ Post-deploy Ocean smoke checks passed"
