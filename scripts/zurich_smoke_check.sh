#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${1:-https://www.clisonix.com/api/zurich}"
PROMPT="Given sequence states S0 = 3, S1 = 7, S2 = 15, S3 = 31, compute S7."

payload=$(cat <<JSON
{"prompt":"$PROMPT"}
JSON
)

response_file=$(mktemp)
status_code=$(curl -sS -o "$response_file" -w "%{http_code}" \
  -H "Content-Type: application/json" \
  -X POST "$TARGET_URL" \
  --data "$payload")

if [[ "$status_code" != "200" ]]; then
  echo "[FAIL] HTTP status: $status_code"
  cat "$response_file"
  rm -f "$response_file"
  exit 1
fi

if ! grep -q '"ok":true' "$response_file"; then
  echo "[FAIL] Missing ok=true in response"
  cat "$response_file"
  rm -f "$response_file"
  exit 1
fi

if ! grep -q 'S_7 = 511' "$response_file"; then
  echo "[FAIL] Missing expected deterministic value S_7 = 511"
  cat "$response_file"
  rm -f "$response_file"
  exit 1
fi

echo "[PASS] Zurich smoke check passed for $TARGET_URL"
cat "$response_file"
rm -f "$response_file"
