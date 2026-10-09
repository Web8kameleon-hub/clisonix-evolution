#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://www.clisonix.com}"

echo "[1/3] Checking providers endpoint: ${BASE_URL}/api/auth/providers"
PROVIDERS_JSON="$(curl -fsS "${BASE_URL}/api/auth/providers")"
echo "${PROVIDERS_JSON}"

if [[ "${PROVIDERS_JSON}" == "{}" ]]; then
  echo "ERROR: NextAuth providers are empty. AUTH_GOOGLE_ID/AUTH_GOOGLE_SECRET are not loaded in production."
  exit 2
fi

if ! grep -q 'google' <<<"${PROVIDERS_JSON}"; then
  echo "ERROR: Google provider is missing in NextAuth providers response."
  exit 3
fi

echo "[2/3] Checking sign-up page status"
SIGNUP_STATUS="$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/sign-up")"
echo "HTTP ${SIGNUP_STATUS}"
if [[ "${SIGNUP_STATUS}" != "200" ]]; then
  echo "ERROR: /sign-up returned non-200 status."
  exit 4
fi

echo "[3/3] Checking sign-in page status"
SIGNIN_STATUS="$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/sign-in")"
echo "HTTP ${SIGNIN_STATUS}"
if [[ "${SIGNIN_STATUS}" != "200" ]]; then
  echo "ERROR: /sign-in returned non-200 status."
  exit 5
fi

echo "OK: NextAuth production checks passed."
