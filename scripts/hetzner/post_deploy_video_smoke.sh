#!/usr/bin/env bash
set -Eeuo pipefail

WEB_BASE_URL_RAW="${1:-http://127.0.0.1:3000}"
WEB_BASE_URL="$(printf '%s' "${WEB_BASE_URL_RAW}" | tr -d '\r\n' | sed 's/[[:space:]]\+$//')"
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

require_cmd curl
require_cmd sed

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

echo "== [1/3] Video generate on ${WEB_BASE_URL} =="
cat > "${tmp_dir}/video_generate.json" <<'JSON'
{"topic":"CI smoke test video generation","duration":30,"style":"documentary"}
JSON

generate_result="$(json_post "${WEB_BASE_URL}/api/video/generate" "${tmp_dir}/video_generate.json" "${tmp_dir}/video_generate_response.json")"
echo "${generate_result}"
cat "${tmp_dir}/video_generate_response.json"; echo

grep -q 'code=200' <<<"${generate_result}" || {
  echo "❌ /api/video/generate did not return HTTP 200"
  exit 1
}

job_id="$(sed -n 's/.*"job_id":"\([^"]*\)".*/\1/p' "${tmp_dir}/video_generate_response.json" | head -n1)"
if [ -z "${job_id}" ]; then
  echo "❌ /api/video/generate response missing job_id"
  exit 1
fi

echo "== [2/3] Video status for job ${job_id} =="
status_code="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${tmp_dir}/video_status_response.json" -w '%{http_code}' "${WEB_BASE_URL}/api/video/status/${job_id}")"
echo "code=${status_code}"
cat "${tmp_dir}/video_status_response.json"; echo

[ "${status_code}" = "200" ] || {
  echo "❌ /api/video/status/${job_id} did not return HTTP 200"
  exit 1
}

grep -q "\"job_id\":\"${job_id}\"" "${tmp_dir}/video_status_response.json" || {
  echo "❌ /api/video/status/${job_id} response missing matching job_id"
  exit 1
}

grep -Eq '"status":"(pending|processing|completed|failed)"' "${tmp_dir}/video_status_response.json" || {
  echo "❌ /api/video/status/${job_id} response missing valid status"
  exit 1
}

echo "== [3/3] Success =="
echo "✅ Post-deploy video generate -> status smoke checks passed"
