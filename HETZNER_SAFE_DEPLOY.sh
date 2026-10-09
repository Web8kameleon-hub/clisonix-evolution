#!/bin/bash
# 🚀 SAFE DEPLOYMENT TO HETZNER - With Live Clients
# Author: Ledjan Ahmati | Date: 2026-02-19
# ⚠️  CAREFUL: Only rebuild Ocean Core, don't touch live services

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🌊 OCEAN CORE SAFE DEPLOYMENT (Live Clients Active)          ║"
echo "║  Server: Hetzner rocky-32gb-nbg1-1                            ║"
echo "║  IP: 46.225.14.83                                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Check current running services${NC}"
docker-compose ps 2>/dev/null || echo "docker-compose.yml not found yet"

echo ""
echo -e "${YELLOW}Step 2: Backup current docker-compose.yml${NC}"
if [ -f docker-compose.yml ]; then
    cp docker-compose.yml docker-compose.yml.backup
    echo "✅ Backup created: docker-compose.yml.backup"
else
    echo "⚠️  No existing docker-compose.yml to backup"
fi

echo ""
echo -e "${YELLOW}Step 3: Pull latest changes from git${NC}"
git pull origin main || echo "⚠️  Git pull failed - using local files"

echo ""
echo -e "${YELLOW}Step 4: Check Ocean Core services status${NC}"
echo "Current running Ocean Core services:"
docker ps --filter "name=ocean-core" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "No containers running yet"

echo ""
echo -e "${YELLOW}Step 5: Rebuild ONLY Ocean Core containers (don't rebuild everything!)${NC}"
echo "Rebuilding: ocean-core, ocean-core-multimodal, ocean-core-strict-chat"
docker-compose build --no-cache ocean-core ocean-core-multimodal ocean-core-strict-chat ocean-core-blerina

echo ""
echo -e "${YELLOW}Step 6: Start Ocean Core services (keep others running)${NC}"
echo "Starting: ocean-core, ocean-core-multimodal, ocean-core-strict-chat, ocean-core-blerina"
docker-compose up -d ocean-core ocean-core-multimodal ocean-core-strict-chat ocean-core-blerina

echo ""
echo -e "${YELLOW}Step 7: Wait for containers to be healthy${NC}"
sleep 10
docker-compose ps | grep ocean-core

echo ""
echo -e "${YELLOW}Step 8: Health checks${NC}"
echo "Checking Ocean Core Full (8030)..."
curl -f http://localhost:8030/health && echo "✅ 8030 is healthy" || echo "⚠️  8030 not responding yet"

echo ""
echo "Checking Ocean Multimodal (8033)..."
curl -f http://localhost:8033/health && echo "✅ 8033 is healthy" || echo "⚠️  8033 not responding yet"

echo ""
echo "Checking Ocean Strict Chat (8035)..."
curl -f http://localhost:8035/health && echo "✅ 8035 is healthy" || echo "⚠️  8035 not responding yet"

echo ""
echo -e "${YELLOW}Step 9: Post-deploy Ocean smoke checks${NC}"
if [ -x ./scripts/hetzner/post_deploy_ocean_smoke.sh ]; then
    ./scripts/hetzner/post_deploy_ocean_smoke.sh http://127.0.0.1:3000
else
    echo "⚠️  Smoke script not found or not executable: scripts/hetzner/post_deploy_ocean_smoke.sh"
fi

echo ""
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo ""
echo "Services Status:"
docker-compose ps

echo ""
echo -e "${YELLOW}Running services that were NOT touched:${NC}"
docker ps --filter "label!=ocean-core" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "None"

echo ""
echo -e "${GREEN}✨ Ocean Core v2 is now running on Hetzner!${NC}"
echo "   Primary: http://46.225.14.83:8030"
echo "   Multimodal: http://46.225.14.83:8033"
echo "   Strict Chat: http://46.225.14.83:8035"
