#!/usr/bin/env bash
set -euo pipefail

# Emergency kill switch for kloud mesh adapter on a host.
# Usage:
#   bash scripts/hetzner/disable_kloud_mesh_adapter.sh

echo "==> Disabling kloud-mesh-adapter timer/service"
sudo systemctl disable --now kloud-mesh-adapter.timer || true
sudo systemctl stop kloud-mesh-adapter.service || true

if [ -f /etc/default/kloud-mesh-adapter ]; then
  sudo sed -i 's/^KLOUD_ADAPTER_ENABLED=.*/KLOUD_ADAPTER_ENABLED=false/' /etc/default/kloud-mesh-adapter || true
  if ! grep -q '^KLOUD_ADAPTER_ENABLED=' /etc/default/kloud-mesh-adapter; then
    echo 'KLOUD_ADAPTER_ENABLED=false' | sudo tee -a /etc/default/kloud-mesh-adapter >/dev/null
  fi
fi

echo "==> Reloading systemd"
sudo systemctl daemon-reload || true

echo "==> Status"
sudo systemctl --no-pager status kloud-mesh-adapter.timer || true
sudo systemctl --no-pager status kloud-mesh-adapter.service || true

echo "✅ kloud-mesh-adapter disabled"
