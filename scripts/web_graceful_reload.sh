#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${1:-clisonix-web}"
PUBLIC_URL="${2:-https://clisonix.com}"

echo "[1/4] Health check before reload..."
curl -fsS -I --max-time 8 "$PUBLIC_URL" >/dev/null

echo "[2/4] Trigger PM2 graceful reload..."
docker exec "$CONTAINER" pm2 reload clisonix-web --update-env

echo "[3/4] Wait for workers to settle..."
sleep 2

echo "[4/4] Health check after reload..."
curl -fsS -I --max-time 8 "$PUBLIC_URL" >/dev/null

echo "✅ Graceful reload completed without taking the site down."
