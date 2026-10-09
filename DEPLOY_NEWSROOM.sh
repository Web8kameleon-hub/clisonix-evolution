#!/bin/bash
#
# Clisonix Newsroom Service v5.0 - Hetzner Deployment Script
# Run this on Hetzner server to deploy Newsroom service
#
# Usage:
#   ssh hetzner-new 'bash /root/DEPLOY_NEWSROOM.sh'
# Or copy to server and run locally:
#   ./DEPLOY_NEWSROOM.sh

set -e

echo "================================================"
echo "🚀 Clisonix Newsroom v5.0 - Deployment Script"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -d "/root/Clisonix-cloud" ]; then
    echo "❌ ERROR: /root/Clisonix-cloud not found"
    exit 1
fi

cd /root/Clisonix-cloud

echo "📂 Working Directory: $(pwd)"
echo ""

# Step 1: Pull latest code
echo "Step 1️⃣ : Pulling latest code from GitHub..."
git fetch origin
git pull origin blackboxai/fix-slo-sli-gate-errors
echo "✅ Code pulled successfully"
echo ""

# Step 2: Verify Newsroom service exists
echo "Step 2️⃣ : Verifying Newsroom service files..."
if [ ! -f "services/newsroom/main.py" ]; then
    echo "❌ ERROR: services/newsroom/main.py not found"
    exit 1
fi
echo "✅ Newsroom service files found"
ls -lh services/newsroom/
echo ""

# Step 3: Build Newsroom Docker image
echo "Step 3️⃣ : Building Newsroom Docker image..."
docker compose build --no-cache newsroom
echo "✅ Docker image built successfully"
echo ""

# Step 4: Stop existing newsroom container (if any)
echo "Step 4️⃣ : Stopping existing Newsroom containers..."
docker compose down newsroom 2>/dev/null || true
echo "✅ Old containers stopped"
echo ""

# Step 5: Start Newsroom service
echo "Step 5️⃣ : Starting Newsroom service..."
docker compose up -d newsroom
echo "✅ Newsroom container started"
echo ""

# Step 6: Wait for service to be healthy
echo "Step 6️⃣ : Waiting for service to be healthy..."
sleep 5
for i in {1..30}; do
    if curl -s http://localhost:9800/health | grep -q "healthy"; then
        echo "✅ Service is healthy!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 1
done
echo ""

# Step 7: Check container status
echo "Step 7️⃣ : Checking container status..."
docker ps --filter "name=clisonix-newsroom" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Step 8: Display logs
echo "Step 8️⃣ : Recent container logs:"
docker logs --tail 20 clisonix-newsroom
echo ""

# Step 9: Test health endpoints
echo "Step 9️⃣ : Testing health endpoints..."
echo ""
echo "  /health endpoint:"
curl -s http://localhost:9800/health | jq . 2>/dev/null || curl -s http://localhost:9800/health
echo ""
echo "  /status endpoint:"
curl -s http://localhost:9800/status | jq . 2>/dev/null || curl -s http://localhost:9800/status
echo ""

# Step 10: Manual trigger for publishing (optional)
echo "Step 🔟 : Ready to publish!"
echo ""
echo "To trigger first publishing cycle, run:"
echo "  curl -X POST http://localhost:9800/publish -d '{\"posts\":10}'"
echo ""

echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Monitor publishing: curl http://localhost:9800/audit?limit=10"
echo "2. Check articles on: https://news.clisonix.com"
echo "3. View logs: docker logs -f clisonix-newsroom"
echo ""
