#!/usr/bin/env bash
set -Eeuo pipefail

OCEAN_BASE_URL="${1:-http://127.0.0.1:8030}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"
WARMUP_COUNT="${WARMUP_COUNT:-5}"
EXPECTED_FIREWALL_ACTION="${EXPECTED_FIREWALL_ACTION:-block}"
WARMUP_TEXT="${WARMUP_TEXT:-baseline resonance sample}"
ATTACK_TEXT="${ATTACK_TEXT:-???????????????????????????????????????????????? probe}"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[XLC_SECURITY_SMOKE] Missing command: $cmd"
    exit 1
  fi
}

require_cmd curl
require_cmd python3

assert_http_code() {
  local got="$1"
  local expected="$2"
  local label="$3"
  if [[ "$got" != "$expected" ]]; then
    echo "[XLC_SECURITY_SMOKE] FAIL ${label}: expected ${expected}, got ${got}"
    exit 1
  fi
}

write_stream_payload() {
  local text="$1"
  local file="$2"
  cat > "$file" <<JSON
{"text":"${text}","commands":["START","RESET","MODE"],"threshold":0.9999999999999999,"max_tokens":64}
JSON
}

post_stream() {
  local payload_file="$1"
  local out_file="$2"
  curl -sS --max-time "${TIMEOUT_SECONDS}" \
    -o "${out_file}" \
    -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -H 'Accept: text/event-stream' \
    --data @"${payload_file}" \
    "${OCEAN_BASE_URL}/xlc/route/stream"
}

echo "== [1/4] Warm baseline on /xlc/route/stream =="
for iteration in $(seq 1 "${WARMUP_COUNT}"); do
  payload_file="${TMP_DIR}/warmup_${iteration}.json"
  output_file="${TMP_DIR}/warmup_${iteration}.out"
  write_stream_payload "${WARMUP_TEXT}" "${payload_file}"
  http_code="$(post_stream "${payload_file}" "${output_file}")"
  assert_http_code "${http_code}" "200" "warmup stream ${iteration}"
  grep -q '"phase": "security"' "${output_file}" || {
    echo "[XLC_SECURITY_SMOKE] FAIL missing security phase during warmup ${iteration}"
    cat "${output_file}"
    exit 1
  }
done

echo "== [2/4] Verify live profile for xlc.route.stream =="
profile_code="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${TMP_DIR}/profile.json" -w '%{http_code}' "${OCEAN_BASE_URL}/xlc/security/profiles/xlc.route.stream")"
assert_http_code "${profile_code}" "200" "stream security profile"
python3 - "${TMP_DIR}/profile.json" "${WARMUP_COUNT}" <<'PY'
import json
import sys

path = sys.argv[1]
expected = int(sys.argv[2])
with open(path, 'r', encoding='utf-8') as handle:
    payload = json.load(handle)
profile = payload.get('profile') or {}
samples = int(profile.get('samples') or 0)
if samples < expected:
    raise SystemExit(f"[XLC_SECURITY_SMOKE] FAIL expected >= {expected} samples, got {samples}")
print(f"[XLC_SECURITY_SMOKE] profile samples={samples} dominant_route={profile.get('dominant_route')}")
PY

echo "== [3/4] Trigger firewall action with attack probe =="
write_stream_payload "${ATTACK_TEXT}" "${TMP_DIR}/attack.json"
attack_code="$(post_stream "${TMP_DIR}/attack.json" "${TMP_DIR}/attack.out")"
assert_http_code "${attack_code}" "200" "attack stream"
python3 - "${TMP_DIR}/attack.out" "${EXPECTED_FIREWALL_ACTION}" <<'PY'
import json
import re
import sys

path = sys.argv[1]
expected_action = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    content = handle.read()

events = []
for raw in re.findall(r'data: (.+?)(?:\n\n|$)', content, re.DOTALL):
    raw = raw.strip()
    if not raw or raw == '[DONE]':
        continue
    events.append(json.loads(raw))

phases = [event.get('phase') for event in events]
if 'security' not in phases:
    raise SystemExit('[XLC_SECURITY_SMOKE] FAIL missing security phase in attack stream')
if 'firewall_action' not in phases:
    raise SystemExit('[XLC_SECURITY_SMOKE] FAIL missing firewall_action phase in attack stream')

firewall_event = next(event for event in events if event.get('phase') == 'firewall_action')
if firewall_event.get('action') != expected_action:
    raise SystemExit(
        f"[XLC_SECURITY_SMOKE] FAIL expected firewall action {expected_action}, got {firewall_event.get('action')}"
    )

if expected_action == 'block':
    complete_event = next((event for event in events if event.get('phase') == 'complete'), None)
    if not complete_event or complete_event.get('reason') != 'blocked_by_xlc_firewall':
        raise SystemExit('[XLC_SECURITY_SMOKE] FAIL missing blocked_by_xlc_firewall completion reason')

print(
    f"[XLC_SECURITY_SMOKE] firewall action={firewall_event.get('action')} severity={firewall_event.get('severity')}"
)
PY

echo "== [4/4] PASS =="
echo "[XLC_SECURITY_SMOKE] PASS ${OCEAN_BASE_URL}"
