#!/usr/bin/env bash
set -euo pipefail

WEB_BASE_URL="${1:-http://127.0.0.1:3000}"
API_BASE_URL="${2:-http://127.0.0.1:8000}"
PAYWALL_BASE_URL="${3:-http://127.0.0.1:8020}"
OCEAN_CORE_URL="${4:-http://127.0.0.1:8030}"

TMP_BODY="/tmp/clisonix_auth_billing_ocean_verify_body"

request_code() {
  local method="$1"
  local url="$2"
  local content_type="${3:-}"
  local body="${4:-}"

  if [[ -n "$content_type" ]]; then
    curl -sS -X "$method" "$url" \
      -H "Content-Type: ${content_type}" \
      -d "$body" \
      -o "$TMP_BODY" -w '%{http_code}' -m 25 || true
  else
    curl -sS -X "$method" "$url" \
      -o "$TMP_BODY" -w '%{http_code}' -m 25 || true
  fi
}

assert_code_in() {
  local got="$1"
  local expected_csv="$2"
  local label="$3"
  IFS=',' read -r -a allowed <<< "$expected_csv"
  for c in "${allowed[@]}"; do
    if [[ "$got" == "$c" ]]; then
      return 0
    fi
  done
  echo "[VERIFY] FAIL ${label}: expected one of [${expected_csv}], got ${got}"
  head -c 500 "$TMP_BODY" || true
  echo
  exit 1
}

assert_body_has_any() {
  local regex="$1"
  local label="$2"
  if ! grep -Eq "$regex" "$TMP_BODY"; then
    echo "[VERIFY] FAIL ${label}: body missing regex ${regex}"
    head -c 500 "$TMP_BODY" || true
    echo
    exit 1
  fi
}

echo "[VERIFY] 1/10 Web Ocean health"
code="$(request_code GET "${WEB_BASE_URL}/api/ocean")"
assert_code_in "$code" "200" "web ocean health status"
assert_body_has_any '"status"' "web ocean health body"

echo "[VERIFY] 2/10 Ocean core status"
code="$(request_code GET "${OCEAN_CORE_URL}/api/v1/status")"
assert_code_in "$code" "200" "ocean core status"

echo "[VERIFY] 3/10 Ocean chat functional"
code="$(request_code POST "${WEB_BASE_URL}/api/ocean" "application/json" '{"message":"health check curiosity","stream":false}')"
assert_code_in "$code" "200,503" "web ocean functional"
if [[ "$code" == "200" ]]; then
  assert_body_has_any '"ocean_response"' "ocean response present"
fi

echo "[VERIFY] 4/10 Billing plans"
code="$(request_code GET "${WEB_BASE_URL}/api/billing/plans")"
assert_code_in "$code" "200,503" "billing plans"

echo "[VERIFY] 5/10 Billing payment-methods auth gate"
code="$(request_code GET "${WEB_BASE_URL}/api/billing/payment-methods")"
assert_code_in "$code" "200,401" "billing payment-methods auth gate"

echo "[VERIFY] 6/10 Billing subscription auth gate"
code="$(request_code GET "${WEB_BASE_URL}/api/billing/subscription")"
assert_code_in "$code" "200,401" "billing subscription auth gate"

echo "[VERIFY] 7/10 Billing portal auth gate"
code="$(request_code POST "${WEB_BASE_URL}/api/billing/portal" "application/json" '{}')"
assert_code_in "$code" "200,401,404,503" "billing portal"

echo "[VERIFY] 8/10 Paywall health"
code="$(request_code GET "${PAYWALL_BASE_URL}/health")"
assert_code_in "$code" "200" "paywall health"

echo "[VERIFY] 9/10 Paywall tiers"
code="$(request_code GET "${PAYWALL_BASE_URL}/api/tiers")"
assert_code_in "$code" "200" "paywall tiers"
assert_body_has_any '"tiers"' "paywall tiers body"

echo "[VERIFY] 10/10 Auth login gateway smoke"
code="$(request_code POST "${API_BASE_URL}/auth/login" "application/json" '{"username_or_email":"probe@example.com","password":"invalid"}')"
assert_code_in "$code" "200,401,403,422,503" "auth login gateway smoke"

echo "[VERIFY] PASS auth+billing+paywall+ocean"
