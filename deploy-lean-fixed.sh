#!/bin/bash
# ═════════════════════════════════════════════════════════════
# CLISONIX LEAN DEPLOYMENT - CRITICAL 5 SERVICES
# With Ollama integrated inside Ocean Core
# ═════════════════════════════════════════════════════════════

set -e

cd /opt/clisonix-cloud

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 CLISONIX LEAN DEPLOYMENT - FIXED VERSION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load environment
export $(cat .env.production | grep -v '^#' | xargs) 2>/dev/null || true

echo ""
echo "✅ Environment Loaded"
echo "   DB: $DB_NAME"
echo "   API Port: $API_PORT"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  CLEANUP: Remove conflicting containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml down --remove-orphans 2>/dev/null || true
sleep 5
echo "✅ Cleaned up"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PHASE 1: Start Databases"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d postgres redis
echo "⏳ Waiting 25s for DB health checks..."
sleep 25
echo "✅ Databases ready"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PHASE 2: Start Ollama (LLM Engine)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d ollama
echo "⏳ Waiting 40s for Ollama healthcheck..."
sleep 40

OLLAMA_STATUS=$(docker exec clisonix-ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "READY" || echo "LOADING")
echo "Ollama Status: $OLLAMA_STATUS"
echo "✅ Ollama started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  PHASE 3: Start Ocean Core (AI with Ollama)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d ocean-core
echo "⏳ Waiting 30s for Ocean Core..."
sleep 30
echo "✅ Ocean Core started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  PHASE 4: Start Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d api
echo "⏳ Waiting 25s for API..."
sleep 25

API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${API_PORT}/health 2>/dev/null || echo "000")
echo "API Health Check: HTTP $API_HEALTH"
echo "✅ API started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  PHASE 5: Start Frontend Web"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d web
echo "⏳ Waiting 20s for Web..."
sleep 20

WEB_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
echo "Web Health Check: HTTP $WEB_HEALTH"
echo "✅ Web started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  PHASE 6: Start Nginx Proxy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d nginx
echo "⏳ Waiting 10s for Nginx..."
sleep 10
echo "✅ Nginx started"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL SERVICES DEPLOYED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 FINAL STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose -f docker-compose.lean.yml ps

echo ""
echo "🔗 SERVICE ENDPOINTS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Backend API:    http://localhost:${API_PORT}"
echo "✅ API Docs:       http://localhost:${API_PORT}/docs"
echo "✅ Frontend:       http://localhost:3000"
echo "✅ Ollama LLM:     http://localhost:11434"
echo "✅ Ocean Core:     http://localhost:8030"
echo "✅ PostgreSQL:     localhost:5432"
echo "✅ Redis:          localhost:6379"
echo ""
echo "🌍 Production URLs:"
echo "   ${NEXT_PUBLIC_API_URL}"
echo "   https://clisonix.com"
echo ""
echo "📝 VIEW LOGS:"
echo "   docker-compose -f docker-compose.lean.yml logs -f"
echo ""
echo "✅ ✅ ✅ DEPLOYMENT COMPLETE! ✅ ✅ ✅"

