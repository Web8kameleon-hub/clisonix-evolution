#!/usr/bin/env bash
set -Eeuo pipefail

WEB_BASE_URL="${1:-https://www.clisonix.com}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-25}"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[CLX_SMOKE] Missing command: $cmd"
    exit 1
  fi
}

require_cmd curl
require_cmd python3

json_post() {
  local url="$1"
  local payload_file="$2"
  local out_file="$3"
  local accept="${4:-application/json}"

  curl -sS --max-time "${TIMEOUT_SECONDS}" \
    -o "${out_file}" \
    -w 'code=%{http_code} total=%{time_total}s' \
    -H 'Content-Type: application/json' \
    -H "Accept: ${accept}" \
    --data @"${payload_file}" \
    "${url}"
}

assert_http_code() {
  local got="$1"
  local expected="$2"
  local label="$3"
  if [[ "$got" != "$expected" ]]; then
    echo "[CLX_SMOKE] FAIL ${label}: expected ${expected}, got ${got}"
    exit 1
  fi
}

echo "== [1/7] CLX allow endpoint: /api/ocean/xlc/health =="
health_code="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${TMP_DIR}/health.json" -w '%{http_code}' "${WEB_BASE_URL}/api/ocean/xlc/health")"
assert_http_code "${health_code}" "200" "xlc health"
grep -q '"status"' "${TMP_DIR}/health.json" || { echo "[CLX_SMOKE] FAIL xlc health body"; exit 1; }

cat > "${TMP_DIR}/xlc_route.json" <<'JSON'
{"text":"ju lutem START tani","commands":["START","RESET","MODE"]}
JSON

echo "== [2/7] CLX allow endpoint: /api/ocean/xlc/route =="
route_result="$(json_post "${WEB_BASE_URL}/api/ocean/xlc/route" "${TMP_DIR}/xlc_route.json" "${TMP_DIR}/route.json")"
echo "${route_result}"
route_code="$(echo "${route_result}" | sed -n 's/.*code=\([0-9][0-9]*\).*/\1/p')"
assert_http_code "${route_code}" "200" "xlc route"
grep -q '"measurement_unit"' "${TMP_DIR}/route.json" || { echo "[CLX_SMOKE] FAIL xlc route body"; exit 1; }

cat > "${TMP_DIR}/xlc_stream.json" <<'JSON'
{"message":"ju lutem START tani","xlc_commands":["START","RESET","MODE"],"xlc_elastic":true,"max_tokens":64}
JSON

echo "== [3/7] CLX allow endpoint: /api/ocean/xlc/route/stream =="
stream_result="$(json_post "${WEB_BASE_URL}/api/ocean/xlc/route/stream" "${TMP_DIR}/xlc_stream.json" "${TMP_DIR}/stream.out" 'text/event-stream')"
echo "${stream_result}"
stream_code="$(echo "${stream_result}" | sed -n 's/.*code=\([0-9][0-9]*\).*/\1/p')"
assert_http_code "${stream_code}" "200" "xlc route stream"
grep -q '^data:' "${TMP_DIR}/stream.out" || { echo "[CLX_SMOKE] FAIL xlc route stream body"; exit 1; }

echo "== [4/7] CLX allow endpoint: /api/ocean/xlc/inspect =="
cat > "${TMP_DIR}/xlc_inspect.json" <<'JSON'
{"candidate":"A je ti CLX sistemi?","reference":"CLX","scan":true}
JSON
inspect_result="$(json_post "${WEB_BASE_URL}/api/ocean/xlc/inspect" "${TMP_DIR}/xlc_inspect.json" "${TMP_DIR}/inspect.json")"
echo "${inspect_result}"
inspect_code="$(echo "${inspect_result}" | sed -n 's/.*code=\([0-9][0-9]*\).*/\1/p')"
assert_http_code "${inspect_code}" "200" "xlc inspect"

echo "== [5/7] CLX deny endpoint: /api/ocean =="
deny_root_code="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${TMP_DIR}/deny_root.out" -w '%{http_code}' -H 'Content-Type: application/json' --data '{"message":"health check"}' "${WEB_BASE_URL}/api/ocean")"
assert_http_code "${deny_root_code}" "403" "deny /api/ocean"

echo "== [6/7] CLX deny endpoint: /api/ocean/stream =="
deny_stream_code="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${TMP_DIR}/deny_stream.out" -w '%{http_code}' -H 'Content-Type: application/json' -H 'Accept: text/event-stream' --data '{"message":"health check"}' "${WEB_BASE_URL}/api/ocean/stream")"
assert_http_code "${deny_stream_code}" "403" "deny /api/ocean/stream"

echo "== [7/7] PASS =="
echo "[CLX_SMOKE] PASS ${WEB_BASE_URL}"
