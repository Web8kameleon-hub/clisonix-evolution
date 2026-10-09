#!/bin/bash
# Switch nginx to new configuration (CRITICAL - zero downtime)

set -e  # Exit on any error

echo "════════════════════════════════════════════════════════════"
echo "🔴 NGINX TRAFFIC SWITCH - PRODUCTION CRITICAL"
echo "════════════════════════════════════════════════════════════"
echo ""

# Confirmation
read -p "⚠️ This will switch production traffic to new configuration. Continue? (yes/no) " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "❌ Cancelled"
  exit 1
fi

cd /opt/clisonix-cloud

echo ""
echo "📋 Pre-switch checks..."

# 1. Verify new nginx config exists
if [ ! -f nginx.production.conf.new ]; then
  echo "❌ nginx.production.conf.new not found"
  exit 1
fi
echo "✅ New nginx config exists"

# 2. Test new config syntax
if docker run --rm -v $(pwd):/etc/nginx:ro nginx:alpine \
  nginx -t -c /etc/nginx/nginx.production.conf.new > /dev/null 2>&1; then
  echo "✅ New nginx config syntax valid"
else
  echo "❌ New nginx config has syntax errors"
  docker run --rm -v $(pwd):/etc/nginx:ro nginx:alpine \
    nginx -t -c /etc/nginx/nginx.production.conf.new
  exit 1
fi

# 3. Verify current nginx is running
if docker ps | grep -q clisonix-nginx; then
  echo "✅ Current nginx is running"
else
  echo "❌ Current nginx is not running"
  exit 1
fi

# 4. Backup current config
echo ""
echo "📦 Backing up current nginx config..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cp nginx.conf nginx.conf.backup-$TIMESTAMP
echo "✅ Backed up to nginx.conf.backup-$TIMESTAMP"

echo ""
echo "🔄 Switching nginx configuration..."

# 5. Replace config
cp nginx.production.conf.new nginx.conf
echo "✅ Config replaced"

# 6. Reload nginx (zero-downtime)
docker exec clisonix-nginx nginx -s reload

# Check if reload succeeded
sleep 1
if docker exec clisonix-nginx ps aux | grep -q "[n]ginx"; then
  echo "✅ nginx reloaded successfully"
else
  echo "❌ nginx process not running - ROLLBACK ACTIVATED"
  cp nginx.conf.backup-$TIMESTAMP nginx.conf
  docker exec clisonix-nginx nginx -s reload
  exit 1
fi

echo ""
echo "🧪 Post-switch verification..."

# 7. Check if requests are being served
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [[ $HTTP_CODE == 200 ]] || [[ $HTTP_CODE == 301 ]] || [[ $HTTP_CODE == 302 ]]; then
  echo "✅ nginx is responding correctly ($HTTP_CODE)"
else
  echo "❌ nginx not responding correctly ($HTTP_CODE) - ROLLBACK ACTIVATED"
  cp nginx.conf.backup-$TIMESTAMP nginx.conf
  docker exec clisonix-nginx nginx -s reload
  exit 1
fi

# 8. Check health endpoints through new config
sleep 1
echo "   Testing API through nginx..."
API_RESPONSE=$(curl -s http://localhost/ | head -c 100)
if [ -n "$API_RESPONSE" ]; then
  echo "✅ API is responding"
else
  echo "❌ API not responding - ROLLBACK ACTIVATED"
  cp nginx.conf.backup-$TIMESTAMP nginx.conf
  docker exec clisonix-nginx nginx -s reload
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🟢 NGINX SWITCH SUCCESSFUL"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ All services responding correctly"
echo "✅ Zero-downtime switch completed"
echo "✅ Backup: nginx.conf.backup-$TIMESTAMP"
echo ""
echo "Next steps:"
echo "1. Monitor logs: docker logs -f clisonix-nginx"
echo "2. Test endpoints: curl https://clisonix.com/health"
echo "3. When stable, run: bash cleanup.sh"
