# 🧪 Service Discovery Testing Guide

## Overview

This guide walks you through testing the Firestore-based service discovery system. After the auto-registration code was deployed to all 4 microservices, you now have:

- ✅ **ALBA** (port 5555) - Auto-registers network-telemetry, data-collection capabilities
- ✅ **ALBI** (port 6680) - Auto-registers neural-processing, pattern-detection capabilities  
- ✅ **JONA** (port 7777) - Auto-registers audio-generation, voice-generation capabilities
- ✅ **Backend API** (port 8000) - Auto-registers orchestration, routing capabilities
- ✅ **Ocean Core** (port 8030) - Already running with nlp-generation capability

## Quick Start: Automated Testing

### Option A: Full Automated Test (Recommended)

This script starts all services and runs comprehensive E2E tests:

```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud

# Start all services and run tests
python orchestrate_discovery_tests.py
```

**What it does:**
1. ✅ Starts Ocean Core (port 8030)
2. ✅ Starts Backend API (port 8000)
3. ✅ Starts ALBA, ALBI, JONA in parallel
4. ✅ Waits for all services to register in Firestore
5. ✅ Runs 6 phases of comprehensive tests
6. ✅ Provides detailed report

**Expected output:**
```
✅ PHASE 1: SERVICE HEALTH CHECKS
   ✅ alba            (port 5555) - ✓ Responding
   ✅ albi            (port 6680) - ✓ Responding
   ✅ jona            (port 7777) - ✓ Responding
   ✅ ocean-core      (port 8030) - ✓ Responding
   ✅ backend-api     (port 8000) - ✓ Responding
   Summary: 5/5 services healthy

✅ PHASE 2: SERVICE REGISTRY - LIST ALL SERVICES
   ✅ List Services Endpoint - Found 5 services

✅ PHASE 3: SERVICE DISCOVERY - BY NAME
   ✅ Discover 'alba' - http://localhost:5555
   ✅ Discover 'albi' - http://localhost:6680
   ✅ Discover 'jona' - http://localhost:7777

✅ PHASE 4: CAPABILITY-BASED DISCOVERY
   ✅ Capability 'network-telemetry' - 1 provider(s)

... more detailed output ...

🎉 ALL TESTS PASSED - FIRESTORE DISCOVERY FULLY OPERATIONAL!
```

---

## Manual Testing: Step-by-Step

### Step 1: Start Services Individually

Open 5 separate terminals and start each service:

**Terminal 1 - Ocean Core:**
```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud
python ocean_api_server.py
# Should see: "✅ Ocean Core running on port 8030"
```

**Terminal 2 - Backend API:**
```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud\apps\api
python -m uvicorn main:app --port 8000 --host 0.0.0.0
# Should see: "Application startup complete"
```

**Terminal 3 - ALBA:**
```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud
python alba_service_5555.py
# Should see: "✅ alba registered in Google Firestore"
```

**Terminal 4 - ALBI:**
```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud
python albi_service_6680.py
# Should see: "✅ albi registered in Google Firestore"
```

**Terminal 5 - JONA:**
```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud
python jona_service_7777.py
# Should see: "✅ jona registered in Google Firestore"
```

### Step 2: Verify Services Are Running

Open a new terminal and check each service:

```bash
# Test ALBA health
curl http://localhost:5555/health

# Test ALBI health
curl http://localhost:6680/health

# Test JONA health
curl http://localhost:7777/health

# Test Backend API health
curl http://localhost:8000/health

# Test Ocean Core health
curl http://localhost:8030/health

# Expected: HTTP 200 with {"status": "ok"}
```

### Step 3: Check Service Registration

Check the logs of Backend API - it should show registry info:

```bash
# GET all registered services
curl http://localhost:8000/api/v1/services

# Expected response:
# [
#   {
#     "name": "alba",
#     "host": "localhost",
#     "port": 5555,
#     "capabilities": ["network-telemetry", "data-collection", ...],
#     "registered_at": "2025-02-18T10:30:00",
#     "last_heartbeat": "2025-02-18T10:30:30"
#   },
#   ... more services ...
# ]
```

### Step 4: Test Service Discovery by Name

Query the discovery endpoint to find a specific service:

```bash
# Find ALBA service
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"service_name": "alba"}'

# Expected response:
# {
#   "name": "alba",
#   "host": "localhost",
#   "port": 5555,
#   "url": "http://localhost:5555"
# }
```

### Step 5: Test Capability-Based Discovery

Find services by what they can do:

```bash
# Find a service that does "neural-processing"
curl http://localhost:8000/api/v1/capabilities/neural-processing

# Expected response:
# [
#   {
#     "name": "albi",
#     "host": "localhost",
#     "port": 6680,
#     "url": "http://localhost:6680",
#     "capability": "neural-processing"
#   }
# ]

# Find all services that do "audio-generation"
curl http://localhost:8000/api/v1/capabilities/audio-generation

# Expected response: List of services with audio-generation capability
```

### Step 6: Test Registry Health

Check the registry status and backend:

```bash
# Registry status and stats
curl http://localhost:8000/api/v1/status

# Expected response:
# {
#   "status": "healthy",
#   "mode": "firestore",
#   "backend": "Google Firestore",
#   "services": 5,
#   "free_tier_limits": {
#     "reads_per_day": 50000,
#     "writes_per_day": 20000
#   }
# }
```

### Step 7: Test Cross-Service Communication

Services should be able to discover each other:

```bash
# Backend API discovers Ocean Core by capability
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"capability": "nlp-generation"}'

# Backend API discovers ALBA by capability
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"capability": "network-telemetry"}'

# Backend API discovers ALBI by capability
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"capability": "neural-processing"}'

# Backend API discovers JONA by capability
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"capability": "audio-generation"}'
```

### Step 8: Test Service Heartbeat (Optional)

Check that services keep their registration alive:

```bash
# Check registration timestamp
curl http://localhost:8000/api/v1/services

# Wait 30 seconds, check again - last_heartbeat should be updated
sleep 30
curl http://localhost:8000/api/v1/services

# Each service's "last_heartbeat" should be more recent than before
```

### Step 9: Test Graceful Fallback (Optional)

Stop Firestore and verify services continue working:

```bash
# Services will log: "⚠️  Service Registry unavailable: ..."
# But service continues to run on its port
# Other services can still discover via DNS/localhost hardcoding

# Start services again - they'll reconnect to Firestore
```

---

## Test Validation Checklist

After running tests, verify:

- [ ] All 5 services return HTTP 200 on `/health`
- [ ] `GET /api/v1/services` lists all 5 services ✓
- [ ] Services show "last_heartbeat" within last 30 seconds ✓
- [ ] `POST /api/v1/service-discovery` finds services by name ✓
- [ ] `GET /api/v1/capabilities/{capability}` finds services by capability ✓
- [ ] Each service has correct capabilities listed ✓
- [ ] All services show "registered_at" timestamp ✓
- [ ] Registry mode shows "firestore" ✓
- [ ] Free tier limits display correctly ✓
- [ ] Services continue running if Firestore becomes unavailable ✓

---

## Advanced Testing

### Test Load (Optional)

Test multiple concurrent discovery queries:

```python
import asyncio
import httpx

async def test_concurrent_discovery():
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("http://localhost:8000/api/v1/services")
            for _ in range(100)
        ]
        results = await asyncio.gather(*tasks)
        print(f"✅ {len([r for r in results if r.status_code == 200])}/100 requests succeeded")

asyncio.run(test_concurrent_discovery())
```

### Test Service Failover

Stop a service and verify it's removed from registry:

```bash
# In a running service terminal, press Ctrl+C
# Service should log: "✅ alba deregistered from Firestore"

# Verify it's removed
curl http://localhost:8000/api/v1/services
# alba should no longer be in the list

# Restart service
python alba_service_5555.py
# Service should re-register automatically
```

### Test Registry Fallback Mode

This requires Firebase credentials to be missing. Check that services:

1. Still register in local in-memory store
2. Can discover each other via localhost
3. Log "⚠️  Service Registry unavailable"
4. Continue serving traffic normally

---

## Debugging

### Service not registering?

Check service logs for:
```
❌ Service Registry unavailable: ...
```

Possible causes:
- Firestore API not enabled → Enable in Google Cloud Console
- Service account permissions wrong → Check IAM roles
- Network connectivity → Verify Google Cloud can be reached

### Discovery endpoint returns 404?

Check that Backend API startup handler ran:
```
✅ backend-api registered in Google Firestore
```

If not, restart Backend API with debug logging.

### Services can register but can't discover each other?

Check that all services have correct capabilities list:
```bash
curl http://localhost:8000/api/v1/services | python -m json.tool
```

Each service should have "capabilities" array populated.

### Firestore quota exceeded?

Check registry status:
```bash
curl http://localhost:8000/api/v1/status | python -m json.tool
```

If reads/writes exceed limits:
- Implement caching (currently 30-second cache in frontend)
- Batch discovery requests
- Consider moving to paid Firestore plan

---

## What's Next After Tests Pass?

Once all tests pass, proceed to:

1. **✅ Phase 2 Complete - Services register and discover**
2. **Phase 3 (Next):** Environment Configuration
   - Create `.env.example` files
   - Move hardcoded secrets to env variables
   - Document all environment variables

3. **Phase 4:** Deployment Guide
   - Docker Compose orchestration
   - Kubernetes manifests
   - Production checklist

4. **Phase 5:** Monitoring Setup
   - Prometheus metrics collection
   - Grafana dashboards
   - Health alerts

---

## Need Help?

Check these files:
- Auto-registration code: `alba_service_5555.py`, `albi_service_6680.py`, `jona_service_7777.py`, `apps/api/main.py`
- Registry implementation: `services/registry.py`
- Discovery code: `apps/web/lib/service-resolver.ts`
- Test suite: `test_firestore_discovery_e2e.py`

