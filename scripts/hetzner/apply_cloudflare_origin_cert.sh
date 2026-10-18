#!/usr/bin/env bash
set -Eeuo pipefail

# Apply Cloudflare Origin certificate on Hetzner and validate nginx TLS.
#
# Usage (env text):
#   export CLOUDFLARE_ORIGIN_CERT="$(cat origin-cert.pem)"
#   export CLOUDFLARE_ORIGIN_KEY="$(cat origin-key.pem)"
#   bash scripts/hetzner/apply_cloudflare_origin_cert.sh /root/Clisonix-cloud
#
# Usage (file paths):
#   CLOUDFLARE_ORIGIN_CERT_FILE=/tmp/origin-cert.pem \
#   CLOUDFLARE_ORIGIN_KEY_FILE=/tmp/origin-key.pem \
#   bash scripts/hetzner/apply_cloudflare_origin_cert.sh /root/Clisonix-cloud

PROJECT_DIR="${1:-/root/Clisonix-cloud}"
ENV_FILE="${CLISONIX_ENV_FILE:-.env}"
COMPOSE_FILE="${CLISONIX_COMPOSE_FILE:-docker-compose.75-services.yml}"
CERTS_DIR="${CERTS_DIR:-$PROJECT_DIR/certs}"
CERT_PATH="$CERTS_DIR/cert.pem"
KEY_PATH="$CERTS_DIR/key.pem"
TLS_HOSTNAME="${TLS_HOSTNAME:-www.clisonix.com}"
REQUIRED_SAN_1="${REQUIRED_SAN_1:-clisonix.com}"
REQUIRED_SAN_2="${REQUIRED_SAN_2:-*.clisonix.com}"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[TLS_APPLY] Missing command: $cmd"
    exit 1
  fi
}

require_cmd docker
require_cmd openssl
require_cmd curl

if [ ! -d "$PROJECT_DIR" ]; then
  echo "[TLS_APPLY] Project directory not found: $PROJECT_DIR"
  exit 1
fi

read_secret_file() {
  local path="$1"
  if [ -z "$path" ] || [ ! -f "$path" ]; then
    return 1
  fi
  cat "$path"
}

CERT_CONTENT="${CLOUDFLARE_ORIGIN_CERT:-}"
KEY_CONTENT="${CLOUDFLARE_ORIGIN_KEY:-}"

if [ -z "$CERT_CONTENT" ]; then
  CERT_CONTENT="$(read_secret_file "${CLOUDFLARE_ORIGIN_CERT_FILE:-}" || true)"
fi

if [ -z "$KEY_CONTENT" ]; then
  KEY_CONTENT="$(read_secret_file "${CLOUDFLARE_ORIGIN_KEY_FILE:-}" || true)"
fi

if [ -z "$CERT_CONTENT" ] || [ -z "$KEY_CONTENT" ]; then
  echo "[TLS_APPLY] Missing origin certificate or key."
  echo "[TLS_APPLY] Provide CLOUDFLARE_ORIGIN_CERT/CLOUDFLARE_ORIGIN_KEY"
  echo "[TLS_APPLY] or CLOUDFLARE_ORIGIN_CERT_FILE/CLOUDFLARE_ORIGIN_KEY_FILE."
  exit 1
fi

mkdir -p "$CERTS_DIR"
printf '%s\n' "$CERT_CONTENT" > "$CERT_PATH"
printf '%s\n' "$KEY_CONTENT" > "$KEY_PATH"
chmod 644 "$CERT_PATH"
chmod 600 "$KEY_PATH"

echo "[TLS_APPLY] Validate certificate and key format"
openssl x509 -in "$CERT_PATH" -noout >/dev/null
openssl pkey -in "$KEY_PATH" -noout >/dev/null

cert_mod="$(openssl x509 -noout -modulus -in "$CERT_PATH" | openssl md5 | awk '{print $2}')"
key_mod="$(openssl rsa -noout -modulus -in "$KEY_PATH" | openssl md5 | awk '{print $2}')"
if [ "$cert_mod" != "$key_mod" ]; then
  echo "[TLS_APPLY] Certificate and key do not match."
  exit 1
fi

san_text="$(openssl x509 -in "$CERT_PATH" -noout -ext subjectAltName 2>/dev/null || true)"
if ! printf '%s' "$san_text" | grep -Fq "$REQUIRED_SAN_1"; then
  echo "[TLS_APPLY] SAN missing required host: $REQUIRED_SAN_1"
  echo "$san_text"
  exit 1
fi
if ! printf '%s' "$san_text" | grep -Fq "$REQUIRED_SAN_2"; then
  echo "[TLS_APPLY] SAN missing required host: $REQUIRED_SAN_2"
  echo "$san_text"
  exit 1
fi

echo "[TLS_APPLY] Restart nginx"
cd "$PROJECT_DIR"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d nginx

echo "[TLS_APPLY] Wait for nginx"
sleep 3

echo "[TLS_APPLY] nginx status"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps nginx

echo "[TLS_APPLY] Test local HTTPS handshake"
echo | openssl s_client -connect 127.0.0.1:443 -servername "$TLS_HOSTNAME" 2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

echo "[TLS_APPLY] Test local HTTP response"
curl -sS -I http://127.0.0.1/ | head -n 1 || true

echo "[TLS_APPLY] DONE"
