# 🚀 SERVICE DISCOVERY - QUICK START

## What Just Got Built?

Your 4 microservices now auto-register in Google Firestore on startup:

```
✅ ALBA (5555)        → network-telemetry, data-collection, packet-routing
✅ ALBI (6680)        → neural-processing, pattern-detection, signal-analysis  
✅ JONA (7777)        → audio-generation, voice-generation, sound-synthesis
✅ Backend API (8000) → orchestration, routing, data-proxy
```

Each service:
- 🔄 Registers in Firestore on startup
- 💓 Sends heartbeat every 30 seconds  
- 🛑 Deregisters cleanly on shutdown
- 📡 Continues solo if Firestore unavailable

---

## Run Tests Now

### Option 1: Fully Automated (Recommended) ⭐

```bash
cd C:\Users\Admin\Desktop\Clisonix-cloud
python orchestrate_discovery_tests.py
```

This starts all 5 services and runs full test suite. Press `Ctrl+C` to stop.

**Time:** ~30-40 seconds for full test suite

### Option 2: Manual Testing

Start services in separate terminals:

```bash
# Terminal 1
python ocean_api_server.py

# Terminal 2  
cd apps\api && python -m uvicorn main:app --port 8000

# Terminal 3
python alba_service_5555.py

# Terminal 4
python albi_service_6680.py

# Terminal 5
python jona_service_7777.py
```

Then test discovery in another terminal:

```bash
# List all services
curl http://localhost:8000/api/v1/services

# Find service by capability
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d '{"capability":"neural-processing"}'

# Get all providers of a capability
curl http://localhost:8000/api/v1/capabilities/audio-generation
```

---

## Expected Output

```
✅ PHASE 1: SERVICE HEALTH CHECKS
   ✅ alba            (port 5555) - ✓ Responding
   ✅ albi            (port 6680) - ✓ Responding
   ✅ jona            (port 7777) - ✓ Responding
   ✅ backend-api     (port 8000) - ✓ Responding
   ✅ ocean-core      (port 8030) - ✓ Responding

✅ PHASE 2: SERVICE REGISTRY - LIST ALL SERVICES
   ✅ List Services Endpoint - Found 5 services

✅ PHASE 3: SERVICE DISCOVERY - BY NAME
   ✅ Discover 'alba' - http://localhost:5555
   ✅ Discover 'albi' - http://localhost:6680
   ✅ Discover 'jona' - http://localhost:7777

✅ PHASE 4: CAPABILITY-BASED DISCOVERY
   ✅ Capability 'network-telemetry' - 1 provider(s)
   ✅ Capability 'neural-processing' - 1 provider(s)

✅ PHASE 5: REGISTRY STATUS & HEALTH
   [PASS] Registry Status Endpoint
   Registry Mode: firestore
   Backend: Google Firestore
   Total Services: 5

✅ PHASE 6: CROSS-SERVICE COMMUNICATION TEST
   ✅ Backend discovered Ocean Core
   ✅ Verified Ocean Core is accessible

═══════════════════════════════════════════════════════════════════
  TEST SUMMARY
═══════════════════════════════════════════════════════════════════
  Tests Passed: 5/5

    ✅ health
    ✅ list
    ✅ discover_name
    ✅ registry_status
    ✅ cross_service

═══════════════════════════════════════════════════════════════════
🎉 ALL TESTS PASSED - FIRESTORE DISCOVERY FULLY OPERATIONAL!
═══════════════════════════════════════════════════════════════════
```

---

## What Each Test Does

| Test | Checks |
|------|--------|
| **Health Checks** | All 5 services respond on their ports |
| **List Services** | Registry returns all registered services |
| **Discover by Name** | Can find service by name (alba, albi, jona, etc) |
| **Capability Discovery** | Can find services by what they do |
| **Registry Status** | Registry health and Firestore stats |
| **Cross-Service Comm** | Services can discover each other |

---

## Key URLs for Manual Testing

```
Get all services:
  GET http://localhost:8000/api/v1/services

Find service by capability:
  POST http://localhost:8000/api/v1/service-discovery
  Body: {"capability": "neural-processing"}

Get all providers of capability:
  GET http://localhost:8000/api/v1/capabilities/audio-generation

Registry health:
  GET http://localhost:8000/api/v1/status
```

---

## What Gets Logged When Services Start

### ALBA logs:
```
✅ alba registered in Google Firestore
   Capabilities: network-telemetry, data-collection, packet-routing
   Heartbeat: 30-second refresh enabled
```

### ALBI logs:
```
✅ albi registered in Google Firestore
   Capabilities: neural-processing, pattern-detection, signal-analysis
   Heartbeat: 30-second refresh enabled
```

### JONA logs:
```
✅ jona registered in Google Firestore
   Capabilities: data-synthesis, audio-generation, neural-audio
   Heartbeat: 30-second refresh enabled
```

### Backend API logs:
```
✅ backend-api registered in Google Firestore
   Capabilities: orchestration, routing, data-proxy, authentication
   Orchestrates: alba, albi, jona, ocean-core
   Heartbeat: 30-second refresh enabled
```

---

## Success Criteria

- ✅ All 5 services respond to health checks
- ✅ Registry lists all 5 services with timestamps
- ✅ Discovery by name finds correct service URLs
- ✅ Discovery by capability finds all providers
- ✅ Registry shows Firestore backend active
- ✅ Services continue if Firestore becomes unavailable

---

## If Something Fails

1. **Service won't start?**
   - Check port already in use: `netstat -ano | findstr :PORT`
   - Check Python imports: `python -c "from services.registry import init_registry"`

2. **Discovery endpoint returns 404?**
   - Restart Backend API: `python -m uvicorn main:app --port 8000`
   - Check backend logs

3. **Firestore connection fails?**
   - Services still work! They'll use fallback in-memory storage
   - Check Google Cloud console if credentials missing

4. **Registry shows 0 services?**
   - Check all services logged "registered in Google Firestore"
   - Wait 5-10 seconds for Firestore write to propagate
   - Refresh: `curl http://localhost:8000/api/v1/services`

---

## Files Modified

| File | Change |
|------|--------|
| `alba_service_5555.py` | ✅ Added startup/shutdown auto-registration |
| `albi_service_6680.py` | ✅ Added startup/shutdown auto-registration |
| `jona_service_7777.py` | ✅ Added startup/shutdown auto-registration |
| `apps/api/main.py` | ✅ Added startup/shutdown auto-registration |
| `services/registry.py` | ✅ Already implemented (Firestore backend) |

---

## Next Steps After Tests Pass

1. **✅ Phase 2 Complete:** Service auto-registration & discovery tested
2. **Phase 3 (Next):** Environment configuration (`.env` files, secrets management)
3. **Phase 4:** Deployment guide (Docker Compose + Kubernetes)
4. **Phase 5:** Monitoring setup (Grafana + Prometheus)

---

## Questions?

See full guide: [TESTING_GUIDE.md](./TESTING_GUIDE.md)  
See registry code: [services/registry.py](./services/registry.py)  
See discovery tests: [test_firestore_discovery_e2e.py](./test_firestore_discovery_e2e.py)

