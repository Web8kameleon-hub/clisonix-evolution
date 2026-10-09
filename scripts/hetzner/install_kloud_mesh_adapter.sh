#!/usr/bin/env bash
set -euo pipefail

# Installs scalable Kloud mesh adapter as a systemd timer service.
# Usage:
#   bash scripts/hetzner/install_kloud_mesh_adapter.sh
# Optional env:
#   TARGET_HOST=root@46.225.14.83 SSH_PORT=22

TARGET_HOST="${TARGET_HOST:-root@46.225.14.83}"
SSH_PORT="${SSH_PORT:-22}"
REMOTE_ADAPTER="/usr/local/bin/kloud_mesh_adapter.py"
REMOTE_ENV="/etc/default/kloud-mesh-adapter"
REMOTE_SERVICE="/etc/systemd/system/kloud-mesh-adapter.service"
REMOTE_TIMER="/etc/systemd/system/kloud-mesh-adapter.timer"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ADAPTER="${SCRIPT_DIR}/kloud_mesh_adapter.py"

if [[ ! -f "${LOCAL_ADAPTER}" ]]; then
  echo "Adapter script not found: ${LOCAL_ADAPTER}" >&2
  exit 1
fi

scp -P "${SSH_PORT}" -o StrictHostKeyChecking=accept-new "${LOCAL_ADAPTER}" "${TARGET_HOST}:${REMOTE_ADAPTER}"

ssh -p "${SSH_PORT}" "${TARGET_HOST}" "bash -s" <<'REMOTE'
set -euo pipefail

chmod +x /usr/local/bin/kloud_mesh_adapter.py
mkdir -p /var/lib/kloud-mesh-adapter

cat > /etc/default/kloud-mesh-adapter << 'EOF'
KLOUD_BASE_URL=http://127.0.0.1:8889
KLOUD_API_PREFIX=/api/v1/hardware
KLOUD_ADAPTER_TIMEOUT_SEC=5
KLOUD_ADAPTER_ALERT_THRESHOLD=3
KLOUD_ADAPTER_MAX_PEERS_PER_RUN=32
KLOUD_ADAPTER_STATE_FILE=/var/lib/kloud-mesh-adapter/state.json
KLOUD_ADAPTER_LOG_FILE=/var/log/kloud-mesh-adapter.log
# KLOUD_NODE_TOKEN=
EOF

cat > /etc/systemd/system/kloud-mesh-adapter.service << 'EOF'
[Unit]
Description=Kloud Mesh Integration Adapter (Dynamic, Real Services)
After=network-online.target

[Service]
Type=oneshot
EnvironmentFile=-/etc/default/kloud-mesh-adapter
ExecStart=/usr/bin/env python3 /usr/local/bin/kloud_mesh_adapter.py
EOF

cat > /etc/systemd/system/kloud-mesh-adapter.timer << 'EOF'
[Unit]
Description=Run Kloud Mesh Adapter every 10 seconds

[Timer]
OnBootSec=8s
OnUnitActiveSec=10s
AccuracySec=1s
Unit=kloud-mesh-adapter.service
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now kloud-mesh-adapter.timer
systemctl start kloud-mesh-adapter.service
systemctl --no-pager --full status kloud-mesh-adapter.service | sed -n '1,20p'
REMOTE

echo "Installed scalable kloud mesh adapter on ${TARGET_HOST}"
