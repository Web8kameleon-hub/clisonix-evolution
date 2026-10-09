#!/bin/bash
# 🌊 Clisonix Ocean-Core - Full Deployment & Validation
# Deploys all updates and validates production readiness

set -e

REMOTE_HOST="46.225.14.83"
REMOTE_USER="root"
SSH_KEY="$HOME/.ssh/id_hetzner"
REMOTE_DIR="/root/Clisonix-cloud"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🌊 CLISONIX OCEAN-CORE - DEPLOYMENT & VALIDATION 2026         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
echo "[1/5] Configuring SSH connection..."
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=20 -i $SSH_KEY"

# Deploy updated code
echo "[2/5] Deploying ocean-core updates..."
scp $SSH_OPTS ocean-core/ocean_api.py root@$REMOTE_HOST:$REMOTE_DIR/ocean-core/ > /dev/null && \
scp $SSH_OPTS ocean-core/response_orchestrator_v5.py root@$REMOTE_HOST:$REMOTE_DIR/ocean-core/ > /dev/null && \
echo "  ✓ Files deployed"

# Restart containers
echo "[3/5] Restarting ocean-core container..."
ssh $SSH_OPTS root@$REMOTE_HOST "
  cd $REMOTE_DIR && \
  docker compose -f docker-compose.75-services.yml down ocean-core 2>/dev/null || true && \
  sleep 3 && \
  docker compose -f docker-compose.75-services.yml up -d ocean-core && \
  sleep 10 && \
  echo '  ✓ Ocean-core restarted'
" > /dev/null 2>&1

echo "[4/5] Verifying health..."
ssh $SSH_OPTS root@$REMOTE_HOST "
  python3 << 'HEALTHCHECK'
import requests
import time

for i in range(6):
    try:
        r = requests.get('http://localhost:8030/health', timeout=5)
        if r.status_code == 200:
            print('  ✓ Health check passed')
            exit(0)
    except:
        pass
    time.sleep(2)

print('  ✗ Health check failed')
exit(1)
HEALTHCHECK
" || exit 1

# Run validation
echo "[5/5] Running validation suite..."
scp $SSH_OPTS validate_ocean_ready.py root@$REMOTE_HOST:/root/validate_ocean.py > /dev/null 2>&1

ssh $SSH_OPTS root@$REMOTE_HOST "python3 /root/validate_ocean.py"

echo "[extra] Running post-deploy smoke checks..."
ssh $SSH_OPTS root@$REMOTE_HOST "cd $REMOTE_DIR && chmod +x scripts/hetzner/post_deploy_ocean_smoke.sh && ./scripts/hetzner/post_deploy_ocean_smoke.sh http://127.0.0.1:3000"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✓ DEPLOYMENT COMPLETE                                         ║"
echo "║                                                                ║"
echo "║  Ocean-Core is now ready with:                                 ║"
echo "║  • Multi-language support (responds in question language)      ║"
echo "║  • Instant streaming (0.2s start)                              ║"
echo "║  • Elastic timeouts (scales with content)                      ║"
echo "║  • End-to-end integration                                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
