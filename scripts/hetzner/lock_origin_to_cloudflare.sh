#!/usr/bin/env bash
set -Eeuo pipefail

# Lock origin ports 80/443 to Cloudflare IP ranges while preserving SSH admin access.
# Defensive use only. This script does not initiate any outbound attack behavior.
#
# Usage:
#   ADMIN_SSH_CIDR="203.0.113.10/32" bash scripts/hetzner/lock_origin_to_cloudflare.sh --dry-run
#   ADMIN_SSH_CIDR="203.0.113.10/32" bash scripts/hetzner/lock_origin_to_cloudflare.sh

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

ADMIN_SSH_CIDR="${ADMIN_SSH_CIDR:-}"
SSH_PORT="${SSH_PORT:-22}"

if [[ -z "$ADMIN_SSH_CIDR" ]]; then
  echo "[ORIGIN_LOCK] ADMIN_SSH_CIDR is required to avoid lockout."
  echo "[ORIGIN_LOCK] Example: ADMIN_SSH_CIDR=\"203.0.113.10/32\" $0 --dry-run"
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "[ORIGIN_LOCK] Missing curl"
  exit 1
fi

if ! command -v ufw >/dev/null 2>&1; then
  echo "[ORIGIN_LOCK] ufw not found. Install ufw or apply equivalent nftables rules manually."
  exit 1
fi

run_cmd() {
  echo "[ORIGIN_LOCK] $*"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    eval "$@"
  fi
}

TMP_V4="$(mktemp)"
TMP_V6="$(mktemp)"
trap 'rm -f "$TMP_V4" "$TMP_V6"' EXIT

curl -fsSL https://www.cloudflare.com/ips-v4 > "$TMP_V4"
curl -fsSL https://www.cloudflare.com/ips-v6 > "$TMP_V6"

echo "[ORIGIN_LOCK] Ensuring baseline SSH allowance"
run_cmd "ufw allow from $ADMIN_SSH_CIDR to any port $SSH_PORT proto tcp"

echo "[ORIGIN_LOCK] Allowing Cloudflare ranges to 80/443"
while IFS= read -r cidr; do
  [[ -z "$cidr" ]] && continue
  run_cmd "ufw allow from $cidr to any port 80 proto tcp"
  run_cmd "ufw allow from $cidr to any port 443 proto tcp"
done < "$TMP_V4"

while IFS= read -r cidr; do
  [[ -z "$cidr" ]] && continue
  run_cmd "ufw allow from $cidr to any port 80 proto tcp"
  run_cmd "ufw allow from $cidr to any port 443 proto tcp"
done < "$TMP_V6"

echo "[ORIGIN_LOCK] Denying direct public access to origin 80/443"
run_cmd "ufw deny 80/tcp"
run_cmd "ufw deny 443/tcp"

run_cmd "ufw status numbered"

echo "[ORIGIN_LOCK] Completed. Verify application through Cloudflare proxy only."
