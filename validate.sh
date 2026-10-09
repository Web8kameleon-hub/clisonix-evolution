#!/bin/bash
# Validation script for production deployment
# Run before switching to new configuration

echo "═══════════════════════════════════════════════════════════"
echo "PRODUCTION DEPLOYMENT VALIDATION"
echo "═══════════════════════════════════════════════════════════"

ERRORS=0
WARNINGS=0

echo ""
echo "📋 1. Checking configuration files..."

# Check docker-compose
if docker-compose -f /opt/clisonix-cloud/docker-compose.production.yml.new config > /dev/null 2>&1; then
  echo "✅ docker-compose.production.yml.new: valid"
else
  echo "❌ docker-compose.production.yml.new: INVALID"
  docker-compose -f /opt/clisonix-cloud/docker-compose.production.yml.new config 2>&1 | head -10
  ((ERRORS++))
fi

# Check nginx config
if docker run --rm -v /opt/clisonix-cloud:/etc/nginx:ro nginx:alpine \
  nginx -t -c /etc/nginx/nginx.production.conf > /dev/null 2>&1; then
  echo "✅ nginx.production.conf: valid"
else
  echo "❌ nginx.production.conf: INVALID"
  ((ERRORS++))
fi

# Check .env.production exists
if [ -f /opt/clisonix-cloud/.env.production ]; then
  echo "✅ .env.production: exists"
  # Check required variables
  source /opt/clisonix-cloud/.env.production
  
  if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD not set"
    ((ERRORS++))
  fi
  if [ -z "$REDIS_PASSWORD" ]; then
    echo "❌ REDIS_PASSWORD not set"
    ((ERRORS++))
  fi
  if [ -z "$JWT_SECRET" ]; then
    echo "❌ JWT_SECRET not set"
    ((ERRORS++))
  fi
else
  echo "❌ .env.production: MISSING"
  ((ERRORS++))
fi

echo ""
echo "🔐 2. Checking SSL certificates..."

if [ -f /opt/clisonix-cloud/certs/cert.pem ] && [ -f /opt/clisonix-cloud/certs/key.pem ]; then
  echo "✅ SSL certificates: exist"
  
  # Check cert expiry
  EXPIRY=$(openssl x509 -enddate -noout -in /opt/clisonix-cloud/certs/cert.pem | cut -d= -f2)
  echo "   Expiry: $EXPIRY"
else
  echo "❌ SSL certificates: MISSING"
  ((ERRORS++))
fi

echo ""
echo "🐳 3. Checking Docker services..."

# Check if docker is running
if docker ps > /dev/null 2>&1; then
  echo "✅ Docker daemon: running"
else
  echo "❌ Docker daemon: NOT running"
  ((ERRORS++))
fi

# Check existing services (shouldn't break)
RUNNING_CONTAINERS=$(docker ps -q | wc -l)
echo "   Current containers: $RUNNING_CONTAINERS"

echo ""
echo "💾 4. Checking backups..."

LATEST_DB_BACKUP=$(ls -t /opt/clisonix-cloud/backups/db-backup-*.sql.gz 2>/dev/null | head -1)
if [ -n "$LATEST_DB_BACKUP" ]; then
  SIZE=$(du -h "$LATEST_DB_BACKUP" | cut -f1)
  echo "✅ Latest DB backup: $(basename $LATEST_DB_BACKUP) ($SIZE)"
else
  echo "⚠️ No database backups found"
  ((WARNINGS++))
fi

echo ""
echo "🌐 5. Checking network connectivity..."

if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
  echo "✅ Internet: connected"
else
  echo "❌ Internet: NOT connected"
  ((ERRORS++))
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "VALIDATION RESULTS"
echo "═══════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ]; then
  echo "✅ All validations passed!"
  echo ""
  echo "🟢 READY FOR DEPLOYMENT"
  echo ""
  echo "Next steps:"
  echo "1. docker-compose -f docker-compose.production.yml.new up -d"
  echo "2. Wait 30 seconds for services to stabilize"
  echo "3. bash switch-nginx.sh"
  echo "4. bash monitor.sh"
  exit 0
else
  echo "❌ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)"
  echo ""
  echo "🔴 DO NOT DEPLOY - Fix errors above and rerun validation"
  exit 1
fi
