#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${ROOT_DIR:-/root/Clisonix-cloud}"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env}"
TARGET_URL="${TARGET_URL:-http://127.0.0.1:8019/ask}"
CHECK_NAME="${CHECK_NAME:-Curiosity /ask}"
THRESHOLD_SECONDS="${THRESHOLD_SECONDS:-3.0}"
MAX_TIME_SECONDS="${MAX_TIME_SECONDS:-8}"
STATE_FILE="${STATE_FILE:-/var/tmp/clisonix_curiosity_ask_smoke.state}"
COOLDOWN_SECONDS="${COOLDOWN_SECONDS:-900}"
LOG_PREFIX="[curiosity-ask-smoke]"

if [[ -z "${SLACK_WEBHOOK_URL:-}" && -f "${ENV_FILE}" ]]; then
  SLACK_WEBHOOK_URL="$(grep -E '^SLACK_WEBHOOK_URL=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- || true)"
  SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL%$'\r'}"
fi

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

payload_file="${tmp_dir}/payload.json"
response_file="${tmp_dir}/response.json"
metrics_file="${tmp_dir}/metrics.txt"

if [[ -n "${PAYLOAD_JSON:-}" ]]; then
  printf '%s\n' "${PAYLOAD_JSON}" > "${payload_file}"
elif [[ "${TARGET_URL}" == *"/api/ocean"* ]]; then
  cat > "${payload_file}" <<'JSON'
{"message":"What is the capital of Germany and why is Berlin the political center?","stream":false}
JSON
else
  cat > "${payload_file}" <<'JSON'
{"query":"What is the capital of Germany and why is Berlin the political center?","language":"en","max_sources":5}
JSON
fi

result_line="$(curl -sS --max-time "${MAX_TIME_SECONDS}" \
  -o "${response_file}" \
  -w 'code=%{http_code} total=%{time_total}' \
  -H 'Content-Type: application/json' \
  --data @"${payload_file}" \
  "${TARGET_URL}" || true)"

echo "${result_line}" > "${metrics_file}"

code="$(awk '{for(i=1;i<=NF;i++) if ($i ~ /^code=/) {split($i,a,"="); print a[2]}}' "${metrics_file}")"
total="$(awk '{for(i=1;i<=NF;i++) if ($i ~ /^total=/) {split($i,a,"="); print a[2]}}' "${metrics_file}")"

code="${code:-000}"
total="${total:-999}"

status="ok"
message="HTTP ${code} total=${total}s"

if [[ "${code}" != "200" ]]; then
  status="critical"
  message="HTTP ${code} from ${TARGET_URL}"
elif ! awk -v total="${total}" -v threshold="${THRESHOLD_SECONDS}" 'BEGIN { exit !(total > threshold) }'; then
  :
else
  status="critical"
  message="Latency ${total}s exceeded threshold ${THRESHOLD_SECONDS}s"
fi

timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
previous_status="unknown"
last_alert_epoch="0"

if [[ -f "${STATE_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${STATE_FILE}"
  previous_status="${previous_status:-unknown}"
  last_alert_epoch="${last_alert_epoch:-0}"
fi

now_epoch="$(date +%s)"
should_alert="false"

if [[ "${status}" == "critical" ]]; then
  if [[ "${previous_status}" != "critical" ]]; then
    should_alert="true"
  elif (( now_epoch - last_alert_epoch >= COOLDOWN_SECONDS )); then
    should_alert="true"
  fi
elif [[ "${previous_status}" == "critical" ]]; then
  should_alert="true"
  message="Recovered. HTTP ${code} total=${total}s"
fi

printf 'previous_status=%q
last_alert_epoch=%q
' "${status}" "$([[ "${should_alert}" == "true" ]] && echo "${now_epoch}" || echo "${last_alert_epoch}")" > "${STATE_FILE}"

echo "${LOG_PREFIX} ${timestamp} check=${CHECK_NAME} status=${status} ${message}"

if [[ "${should_alert}" == "true" && -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  severity_emoji="✅"
  if [[ "${status}" == "critical" ]]; then
    severity_emoji="🚨"
  fi

  slack_payload="$(python3 - <<PY
import json
print(json.dumps({
  "text": f"${severity_emoji} ${CHECK_NAME} smoke {message}",
    "blocks": [
    {"type": "header", "text": {"type": "plain_text", "text": f"${severity_emoji} ${CHECK_NAME} smoke", "emoji": True}},
        {"type": "section", "fields": [
      {"type": "mrkdwn", "text": "*Check:*\n${CHECK_NAME}"},
            {"type": "mrkdwn", "text": "*Target:*\n${TARGET_URL}"},
            {"type": "mrkdwn", "text": "*Status:*\n${status}"},
            {"type": "mrkdwn", "text": "*HTTP:*\n${code}"},
            {"type": "mrkdwn", "text": "*Latency:*\n${total}s"},
            {"type": "mrkdwn", "text": "*Threshold:*\n${THRESHOLD_SECONDS}s"},
            {"type": "mrkdwn", "text": "*Time:*\n${timestamp}"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Message:*\n${message}"}},
    ],
}))
PY
)"

  curl -sS -X POST -H 'Content-Type: application/json' --data "${slack_payload}" "${SLACK_WEBHOOK_URL}" >/dev/null || true
fi

if [[ "${status}" == "critical" ]]; then
  exit 1
fi
