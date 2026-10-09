#!/bin/bash
# Cleanup after successful deployment

echo "════════════════════════════════════════════════════════════"
echo "POST-DEPLOYMENT CLEANUP"
echo "════════════════════════════════════════════════════════════"
echo ""

cd /opt/clisonix-cloud

# Confirmation
echo "⚠️ This will:"
echo "  - Remove *.new configuration files"
echo "  - Stop old docker containers"
echo "  - Clean up orphaned volumes"
echo ""
read -p "Continue? (yes/no) " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "❌ Cancelled"
  exit 1
fi

echo ""
echo "🧹 Cleaning up..."

# 1. Remove .new config files
if [ -f docker-compose.production.yml.new ]; then
  rm docker-compose.production.yml.new
  echo "✅ Removed docker-compose.production.yml.new"
fi

if [ -f nginx.production.conf.new ]; then
  rm nginx.production.conf.new
  echo "✅ Removed nginx.production.conf.new"
fi

# 2. Stop old containers (if using old docker-compose)
# Uncomment if you want to stop old containers
# docker-compose -f docker-compose.yml down --remove-orphans
# echo "✅ Stopped old containers"

# 3. Clean orphaned volumes
docker volume prune -f > /dev/null
echo "✅ Cleaned orphaned volumes"

# 4. Clean dangling images
docker image prune -f > /dev/null
echo "✅ Cleaned dangling images"

# 5. List current containers and volumes
echo ""
echo "📊 Current deployment status:"
echo ""
echo "Active containers:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(clisonix|postgres|redis|ollama|ocean|api|web|nginx)" || echo "  None"

echo ""
echo "Mounted volumes:"
docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep -E "(postgres|redis|ollama|ocean|nginx)" || echo "  None"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ CLEANUP COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Deployment successful! ✨"
echo ""
echo "Monitor the system:"
echo "  - Logs: docker logs -f clisonix-api"
echo "  - Status: docker ps"
echo "  - Health: curl https://clisonix.com/health"
echo ""
echo "Backups are stored at: /opt/clisonix-cloud/backups/"
