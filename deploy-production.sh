#!/bin/bash
# ═════════════════════════════════════════════════════════════
# CLISONIX PRODUCTION DEPLOYMENT
# ═════════════════════════════════════════════════════════════

cd /opt/clisonix-cloud

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 CLISONIX PRODUCTION DEPLOYMENT - PHASE 1"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load environment variables from .env.production
export $(cat .env.production | grep -v '^#' | xargs) 2>/dev/null || true

echo ""
echo "✅ Environment variables loaded:"
echo "   DB_USER: $DB_USER"
echo "   DB_NAME: $DB_NAME"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   DEBUG: $DEBUG"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 PHASE 1: Starting Databases (postgres, redis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.production.yml up -d postgres redis

echo "⏳ Waiting 30 seconds for databases to become healthy..."
sleep 30

echo ""
echo "🏥 Database Status:"
docker-compose -f docker-compose.production.yml ps postgres redis

# Check postgres health
PG_HEALTH=$(docker exec clisonix-postgres pg_isready -U $DB_USER -d $DB_NAME 2>/dev/null | grep -c "accepting")
if [ "$PG_HEALTH" -gt 0 ]; then
    echo "✅ PostgreSQL is HEALTHY"
else
    echo "⚠️  PostgreSQL is still starting..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 PHASE 2: Starting AI Engines (ollama, ocean-core)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.production.yml up -d ollama ocean-core

echo "⏳ Waiting 30 seconds for AI services to start..."
sleep 30

echo ""
echo "🏥 AI Services Status:"
docker-compose -f docker-compose.production.yml ps ollama ocean-core

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 PHASE 3: Starting Application (api, web, nginx)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker-compose -f docker-compose.production.yml up -d api web nginx

echo "⏳ Waiting 20 seconds for application to start..."
sleep 20

echo ""
echo "🏥 Application Status:"
docker-compose -f docker-compose.production.yml ps api web nginx

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL SERVICES STARTED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 Complete Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🔗 Service Endpoints:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API: http://localhost:8000/health"
echo "API Docs: http://localhost:8000/docs"
echo "Web: http://localhost:3000"
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"
echo "Ollama: localhost:11434"
echo "Ocean-Core: http://localhost:8030"
echo ""
echo "🌐 Production Domain:"
echo "   https://clisonix.com"
echo "   https://api.clisonix.com"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Next Steps:"
echo "   1. Verify health endpoints (curl http://localhost:8000/health)"
echo "   2. Check logs: docker-compose -f docker-compose.production.yml logs -f api"
echo "   3. Test API: curl -X GET http://localhost:8000/api/v1/health"
echo ""
echo "✅ Deployment Complete! 🎉"

