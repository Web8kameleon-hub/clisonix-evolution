#!/bin/bash
# Monitoring script for production deployment
# Run in separate terminal during/after deployment

echo "════════════════════════════════════════════════════════════"
echo "PRODUCTION HEALTH MONITORING"
echo "════════════════════════════════════════════════════════════"
echo "Monitoring for 10 minutes (120 checks, 5-second intervals)"
echo ""

CHECK_COUNT=0
FAILURE_COUNT=0
SUCCESS_COUNT=0

# Health check endpoints
declare -A ENDPOINTS=(
  [api]="http://localhost:8000/health"
  [ocean-core]="http://localhost:8030/health"
  [ocean-v2]="http://localhost:8031/api/v2/health"
  [web]="http://localhost:3000/"
  [postgres]="exec:docker exec clisonix-postgres psql -U clisonix -d clisonixdb -c 'SELECT 1'"
  [redis]="exec:docker exec clisonix-redis redis-cli PING"
)

# Run checks for 10 minutes
for i in {1..120}; do
  ((CHECK_COUNT++))
  TIMESTAMP=$(date '+%H:%M:%S')
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Check $CHECK_COUNT/120 [$TIMESTAMP] | ✅: $SUCCESS_COUNT | ❌: $FAILURE_COUNT"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Check each service
  for SERVICE in "${!ENDPOINTS[@]}"; do
    ENDPOINT=${ENDPOINTS[$SERVICE]}
    
    if [[ $ENDPOINT == exec:* ]]; then
      # Execute command
      CMD=${ENDPOINT#exec:}
      if eval "$CMD" > /dev/null 2>&1; then
        echo "✅ $SERVICE"
        ((SUCCESS_COUNT++))
      else
        echo "❌ $SERVICE"
        ((FAILURE_COUNT++))
      fi
    else
      # HTTP request
      HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT" 2>/dev/null)
      
      if [[ $HTTP_CODE == 200 ]] || [[ $HTTP_CODE == 301 ]] || [[ $HTTP_CODE == 302 ]]; then
        echo "✅ $SERVICE ($HTTP_CODE)"
        ((SUCCESS_COUNT++))
      else
        echo "❌ $SERVICE ($HTTP_CODE)"
        ((FAILURE_COUNT++))
      fi
    fi
  done
  
  # Container status
  RUNNING=$(docker ps -q | wc -l)
  echo "📦 Docker containers: $RUNNING"
  
  # Memory usage
  MEMORY=$(docker stats --no-stream --format "{{.MemUsage}}" 2>/dev/null | head -5 | tail -1)
  echo "💾 Memory: $MEMORY"
  
  echo ""
  
  # Break after 10 minutes
  if [ $i -lt 120 ]; then
    sleep 5
  fi
done

echo "════════════════════════════════════════════════════════════"
echo "MONITORING COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo "Total Checks: $CHECK_COUNT"
echo "✅ Successes: $SUCCESS_COUNT"
echo "❌ Failures: $FAILURE_COUNT"
echo ""

if [ $FAILURE_COUNT -eq 0 ]; then
  echo "🟢 ALL SERVICES HEALTHY - Safe to proceed"
  exit 0
else
  echo "🟡 Some services had issues - Review logs"
  echo ""
  echo "Common issues:"
  echo "- API not connecting to DB: docker logs clisonix-api"
  echo "- Ocean not connecting to Ollama: docker logs clisonix-ocean-core"
  echo "- nginx not routing: docker logs clisonix-nginx"
  exit 1
fi
