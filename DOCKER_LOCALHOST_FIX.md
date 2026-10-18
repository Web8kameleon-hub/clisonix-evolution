# Docker Localhost Fix - Validation Guide

## Problem Fixed ✅
Node.js container was unable to reach other services because it was using `localhost:PORT` which resolves to the Node container itself, not the host or other containers.

## Solution Applied ✅

### 1. Environment Variables (docker-compose.75-services.yml)
Added to `web` service environment:
```yaml
API_INTERNAL_URL: "http://clisonix-api:8000"
OCEAN_INTERNAL_URL: "http://clisonix-ocean-core:8030"
OCEAN_MULTIMODAL_URL: "http://clisonix-ocean-core-multimodal:8033"
OCEAN_STRICT_CHAT_URL: "http://clisonix-ocean-core-strict-chat:8035"
OCEAN_BLERINA_URL: "http://clisonix-ocean-core-blerina:8032"
OPENMIND_INTERNAL_URL: "http://clisonix-openmind:9999"
```

### 2. API Routes Updated
- **apps/web/app/api/service-info/route.ts** - Uses env vars in fallback service map
- **apps/web/app/api/zurich/route.ts** - conditionally uses localhost in dev, container names in production
- **apps/web/app/api/service-discovery/route.ts** - detects Docker environment and uses container names

### 3. Service URL Utility Created
**apps/web/lib/api/service-urls.ts** - Centralized service URL resolution:
- Checks for explicit environment variable overrides
- Detects Docker via `API_INTERNAL_URL` presence  
- Falls back to localhost for local development
- Supports all major services with proper typing

## Testing Checklist

### Local Development (localhost)
```bash
# Start docker-compose
docker-compose up -d

# Test web container can reach ocean
docker exec clisonix-web curl -s http://localhost:8030/health | head -c 100

# Test web container can reach api
docker exec clisonix-web curl -s http://localhost:8000/health | head -c 100

# Verify front end still works
curl http://localhost:3000/api/service-info -X POST -d '{"service":"ocean-core"}' -H "Content-Type: application/json" | jq
```

### Docker Compose Network Testing
```bash
# Verify docker network exists and services are connected
docker network ls | grep clisonix-net

# Check web container can resolve service names
docker exec clisonix-web nslookup clisonix-api
docker exec clisonix-web nslookup clisonix-ocean-core

# Test inter-container communication
docker exec clisonix-web curl -v http://clisonix-ocean-core:8030/health

# Check environment variables are set
docker exec clisonix-web env | grep API_INTERNAL_URL
docker exec clisonix-web env | grep OCEAN_INTERNAL_URL
```

### Frontend Dashboard Tests
```bash
# Visit system-status API
curl http://localhost:3000/api/system-status

# Visit service-discover API  
curl http://localhost:3000/api/service-discovery

# Visit service-info API
curl http://localhost:3000/api/service-info -X POST \
  -H "Content-Type: application/json" \
  -d '{"service":"ocean-core"}' | jq
```

### Expected Success Indicators ✓
- [ ] `curl http://localhost:3000/api/service-info` returns ocean-core service info
- [ ] `docker exec clisonix-web curl http://clisonix-ocean-core:8030/health` returns 200
- [ ] No "Cannot reach localhost" or "Connection refused" errors in logs
- [ ] `docker logs clisonix-web` shows clean startup with no DNS resolution errors
- [ ] Dashboard shows proper service status (not "Unavailable")

## Files Changed in Commit
- `docker-compose.75-services.yml` - Added 5 service URL env vars to web container
- `apps/web/app/api/service-info/route.ts` - Uses env vars for fallback service URLs
- `apps/web/app/api/zurich/route.ts` - Dev/prod conditional URL resolution
- `apps/web/app/api/service-discovery/route.ts` - Docker environment detection
- `apps/web/lib/api/service-urls.ts` - NEW: Service URL utility (TypeScript, exported functions)

## Rollback Plan
If issues occur, revert with:
```bash
git revert e28e7832 --no-edit
docker-compose down && docker-compose up --build -d
```

## Next Steps
1. ✅ Code changes committed
2. ⏳ Test in local Docker environment
3. ⏳ Push to remote branch
4. ⏳ Trigger deployment workflow to Hetzner
5. ⏳ Monitor service logs for 5 minutes
6. ⏳ Verify dashboard loads with real service data

## DNS/Network Debugging
If containers still can't reach each other:

```bash
# Check Docker network
docker network inspect clisonix-net | grep -A 20 "Containers"

# Verify service is on network
docker inspect clisonix-ocean-core | grep -A 30 NetworkSettings

# Test from host (should fail if no port binding)
curl http://clisonix-ocean-core:8030/health
# Normal to fail - service name only resolves inside docker network

# Test with specific network
docker exec clisonix-web bash -c "for i in {1..3}; do echo '=== Attempt $i ==='; curl -v http://clisonix-ocean-core:8030/health || true; sleep 1; done"
```

## Environment Detection Logic
The routes use this algorithm:
```
IF API_INTERNAL_URL env var is set
  → Assume Docker environment
  → Use container names (clisonix-api:8000, clisonix-ocean-core:8030)
ELSE
  → Assume local development
  → Use localhost:PORT (localhost:8000, localhost:8030)
```

This allows the same code to work in:
- ✅ Local development (`npm run dev` - uses localhost)
- ✅ Docker Compose (API_INTERNAL_URL set - uses container names)
- ✅ Production (API_INTERNAL_URL set - uses container names)

---
**Commit**: e28e7832  
**Date**: 2026-05-19  
**Status**: Ready for Testing
