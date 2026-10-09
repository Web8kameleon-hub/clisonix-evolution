#!/bin/bash
# ═════════════════════════════════════════════════════════════
# CLISONIX LEAN DEPLOYMENT - CORE 5 SERVICES ONLY
# Backend, Frontend, Ocean Core, PostgreSQL, Redis
# ═════════════════════════════════════════════════════════════

set -e

cd /opt/clisonix-cloud

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 CLISONIX LEAN DEPLOYMENT - 5 CORE SERVICES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs) 2>/dev/null || true

echo ""
echo "✅ Configuration Loaded:"
echo "   Environment: $ENVIRONMENT"
echo "   Debug: $DEBUG"
echo "   API Port: $API_PORT"
echo "   DB: $DB_NAME"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Step 1: Validate Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ docker-compose.lean.yml is VALID"
else
    echo "❌ Configuration invalid! Exiting."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 Step 2: Stop Existing Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml down 2>/dev/null || true
sleep 3
echo "✅ Old containers stopped"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗄️  Step 3: Start Databases (PostgreSQL + Redis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d postgres redis

echo "⏳ Waiting 20 seconds for databases..."
sleep 20

PG_READY=$(docker exec clisonix-postgres pg_isready -U $DB_USER -d $DB_NAME 2>/dev/null | grep -c "accepting" || echo "0")
if [ "$PG_READY" -gt "0" ]; then
    echo "✅ PostgreSQL is HEALTHY"
else
    echo "⚠️  PostgreSQL still initializing..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Step 4: Start Ocean Core (AI Engine)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d ocean-core

echo "⏳ Waiting 30 seconds for Ocean Core..."
sleep 30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Step 5: Start Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d api

echo "⏳ Waiting 20 seconds for API startup..."
sleep 20

API_READY=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${API_PORT}/health 2>/dev/null || echo "000")
if [ "$API_READY" == "200" ]; then
    echo "✅ Backend API is HEALTHY"
else
    echo "⚠️  Backend API starting... (HTTP $API_READY)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Step 6: Start Frontend Web"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d web

echo "⏳ Waiting 15 seconds for Web startup..."
sleep 15

WEB_READY=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$WEB_READY" == "200" ] || [ "$WEB_READY" == "302" ]; then
    echo "✅ Frontend Web is HEALTHY"
else
    echo "⚠️  Frontend Web starting... (HTTP $WEB_READY)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔀 Step 7: Start Nginx Proxy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.lean.yml up -d nginx

echo "⏳ Waiting 10 seconds for Nginx..."
sleep 10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📋 Services Status:"
echo ""
docker-compose -f docker-compose.lean.yml ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Endpoints:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Local Access:"
echo "   Backend API: http://localhost:${API_PORT}"
echo "   API Docs: http://localhost:${API_PORT}/docs"
echo "   Frontend: http://localhost:3000"
echo "   PostgreSQL: localhost:5432 (User: $DB_USER)"
echo "   Redis: localhost:6379"
echo "   Ocean Core: http://localhost:8030"
echo ""
echo "🌍 Production URLs:"
echo "   ${NEXT_PUBLIC_API_URL}"
echo "   https://clisonix.com"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Monitoring:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "docker-compose -f docker-compose.lean.yml logs -f"
echo ""
echo "✅ Deployment successful! 🎉"

