#!/usr/bin/env bash
set -euo pipefail

# Emergency recovery for Kloud mesh retry storms / FD pressure incidents.
# Usage:
#   bash scripts/hetzner/mesh_emergency_recover.sh
#   bash scripts/hetzner/mesh_emergency_recover.sh --reboot

DO_REBOOT=false
if [[ "${1:-}" == "--reboot" ]]; then
  DO_REBOOT=true
fi

echo "[1/8] Stopping mesh timers/services (best-effort)"
systemctl stop kloud-mesh-adapter.timer 2>/dev/null || true
systemctl stop kloud-mesh-ping.timer 2>/dev/null || true
systemctl stop kloud-mesh-adapter.service 2>/dev/null || true
systemctl stop kloud-mesh-ping.service 2>/dev/null || true
systemctl disable kloud-mesh-adapter.timer 2>/dev/null || true
systemctl disable kloud-mesh-ping.timer 2>/dev/null || true

echo "[2/8] Killing runaway mesh processes (best-effort)"
pkill -9 -f kloud-mesh 2>/dev/null || true
pkill -9 -f kloud 2>/dev/null || true

echo "[3/8] Resetting systemd manager state"
systemctl daemon-reexec || true
systemctl reset-failed || true

echo "[4/8] Applying runtime nofile limit"
ulimit -n 65535 || true

echo "[5/8] Ensuring systemd nofile baseline"
if ! grep -q '^DefaultLimitNOFILE=65535$' /etc/systemd/system.conf 2>/dev/null; then
  echo 'DefaultLimitNOFILE=65535' >> /etc/systemd/system.conf
fi

echo "[6/8] Restarting fail2ban (best-effort)"
systemctl restart fail2ban 2>/dev/null || true

echo "[7/8] Snapshot status"
echo "--- ulimit -n ---"
ulimit -n || true
echo "--- kloud timers ---"
systemctl list-timers --all | grep -E 'kloud-mesh|NEXT|LEFT' || true
echo "--- fail2ban ---"
fail2ban-client status || true

echo "[8/8] Done"
if [[ "${DO_REBOOT}" == "true" ]]; then
  echo "Reboot requested, rebooting now..."
  reboot
fi
