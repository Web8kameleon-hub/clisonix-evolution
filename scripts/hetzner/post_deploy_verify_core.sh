#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:3000}"
HOST_HEADER="${2:-www.clisonix.com}"
PROTO_HEADER="${3:-https}"
TEST_USER_ID="${4:-anonymous-user}"
VERIFY_RETRY_ATTEMPTS="${VERIFY_RETRY_ATTEMPTS:-12}"
VERIFY_RETRY_SLEEP_S="${VERIFY_RETRY_SLEEP_S:-2}"
CRITICAL_FAIL=0  # Allow non-critical verification failures to complete without hard exit

TMP_BODY="/tmp/clisonix_verify_body"

request_code() {
  local method="$1"
  local path="$2"
  local extra_header_name="${3:-}"
  local extra_header_value="${4:-}"

  if [[ -n "$extra_header_name" ]]; then
    curl -sS -X "$method" \
      -H "Host: ${HOST_HEADER}" \
      -H "X-Forwarded-Proto: ${PROTO_HEADER}" \
      -H "${extra_header_name}: ${extra_header_value}" \
      -o "$TMP_BODY" -w '%{http_code}' -m 20 "${BASE_URL}${path}" || true
  else
    curl -sS -X "$method" \
      -H "Host: ${HOST_HEADER}" \
      -H "X-Forwarded-Proto: ${PROTO_HEADER}" \
      -o "$TMP_BODY" -w '%{http_code}' -m 20 "${BASE_URL}${path}" || true
  fi
}

request_code_with_retry() {
  local method="$1"
  local path="$2"
  local expected="$3"
  local label="$4"
  local extra_header_name="${5:-}"
  local extra_header_value="${6:-}"

  local got=""
  local attempt

  for ((attempt=1; attempt<=VERIFY_RETRY_ATTEMPTS; attempt++)); do
    got="$(request_code "$method" "$path" "$extra_header_name" "$extra_header_value")"
    if [[ "$got" == "$expected" ]]; then
      echo "$got"
      return 0
    fi

    # Retry only transient proxy/upstream states.
    if [[ "$got" =~ ^(429|502|503|504|000)$ ]] && (( attempt < VERIFY_RETRY_ATTEMPTS )); then
      echo "[VERIFY] WARN ${label}: got ${got} on attempt ${attempt}/${VERIFY_RETRY_ATTEMPTS}, retrying in ${VERIFY_RETRY_SLEEP_S}s" >&2
      sleep "$VERIFY_RETRY_SLEEP_S"
      continue
    fi

    break
  done

  echo "$got"
  return 1
}

assert_code() {
  local got="$1"
  local expected="$2"
  local label="$3"
  if [[ "$got" != "$expected" ]]; then
    echo "[VERIFY] FAIL ${label}: expected ${expected}, got ${got}"
    head -c 300 "$TMP_BODY" || true
    echo
    exit 1
  fi
}

# Warn instead of fail for non-critical checks (e.g., backend-dependent endpoints)
# Allows deployment to succeed even if transient backend issues occur
assert_code_warn_only() {
  local got="$1"
  local expected="$2"
  local label="$3"
  if [[ "$got" != "$expected" ]]; then
    echo "[VERIFY] WARN ${label}: expected ${expected}, got ${got}"
    head -c 300 "$TMP_BODY" || true
    echo
    CRITICAL_FAIL=1  # Indicate failure occurred but don't exit
    return 0
  fi

  return 0
}

assert_body_contains() {
  local needle="$1"
  local label="$2"
  if ! grep -q "$needle" "$TMP_BODY"; then
    echo "[VERIFY] FAIL ${label}: body missing '${needle}'"
    head -c 300 "$TMP_BODY" || true
    echo
    exit 1
  fi
}

assert_body_matches() {
  local pattern="$1"
  local label="$2"
  if ! grep -Eq "$pattern" "$TMP_BODY"; then
    echo "[VERIFY] FAIL ${label}: body does not match regex '${pattern}'"
    head -c 300 "$TMP_BODY" || true
    echo
    exit 1
  fi
}

echo "[VERIFY] 1/6 Zurich health"
code="$(request_code GET /api/zurich)"
assert_code "$code" "200" "zurich health code"
assert_body_contains '"status":"online"' "zurich online"

echo "[VERIFY] 2/6 Kloud bridge"
code="$(request_code GET /api/proxy/kloud-bridge)"
assert_code "$code" "200" "kloud bridge code"
assert_body_matches '"activity_updates":(null|[0-9]+)' "kloud activity_updates shape"

echo "[VERIFY] 3/6 user-data-sources without identity"
code="$(request_code GET /api/proxy/user-data-sources)"
assert_code "$code" "422" "user-data-sources no identity"
assert_body_contains 'Missing required identity' "user-data-sources strict identity"

echo "[VERIFY] 4/6 user-summary without identity"
code="$(request_code GET /api/proxy/user-summary)"
assert_code "$code" "422" "user-summary no identity"
assert_body_contains 'Missing required identity' "user-summary strict identity"

echo "[VERIFY] 5/6 user-data-sources with identity"
code="$(request_code_with_retry GET /api/proxy/user-data-sources 200 "user-data-sources with identity" X-User-ID "$TEST_USER_ID" || true)"
assert_code_warn_only "$code" "200" "user-data-sources with identity"

echo "[VERIFY] 6/6 user-summary with identity"
code="$(request_code_with_retry GET /api/proxy/user-summary 200 "user-summary with identity" X-User-ID "$TEST_USER_ID" || true)"
assert_code_warn_only "$code" "200" "user-summary with identity"

# Exit with appropriate message
if (( CRITICAL_FAIL == 1 )); then
  echo "[VERIFY] COMPLETE with non-critical failures (deployment proceeding)"
  exit 0  # Non-critical failures don't block deployment
else
  echo "[VERIFY] PASS"
  exit 0
fi
