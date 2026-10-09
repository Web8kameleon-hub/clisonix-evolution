# Ocean-Core Timeout Fix - Implementation Report

## Problem Identified
The Ocean-Core service was failing with "Processing timeout" errors after 2 seconds, preventing Ollama from generating responses (which typically take 10-30+ seconds).

## Root Cause
- **File**: `ocean-core/ocean_api.py`
- **Issue**: Default timeout was set to 2.0 seconds
  - Line 1291 (simple_chat endpoint): `fast_timeout = float(os.getenv("OCEAN_FAST_TIMEOUT_SECONDS", "2.0"))`
  - Line 1365 (fast_chat endpoint): `timeout_s = float(os.getenv("OCEAN_FAST_TIMEOUT_SECONDS", "2.0"))`

## Fix Applied
Increased timeout to 45 seconds to allow Ollama adequate time to generate responses:
- Line 1291: Changed to `"45.0"`
- Line 1365: Changed to `"45.0"`

## Deployment Status
✅ File changed locally  
✅ Changes deployed to server via SCP  
✅ Container restarted with: `docker compose -f docker-compose.75-services.yml restart ocean-core`

## Verification Steps
To verify the fix is working:

```bash
# 1. Check container is running
docker ps | grep ocean-core

# 2. Test Ollama directly
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# 3. Test Ocean-Core chat (should NOT timeout after 2s now)
curl -X POST http://localhost:8030/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "language": "en"}' \
  --max-time 60

# 4. Test frontend proxy
curl -X POST http://localhost:3000/api/ocean \
  -H "Content-Type: application/json" \
  -d '{"question": "What is consciousness?", "language": "en"}' \
  --max-time 60
```

## Expected Behavior After Fix
1. **User asks question in UI** (e.g., "What is consciousness?")
2. **Frontend sends to proxy** `/api/ocean` → `/api/v1/chat`
3. **Orchestrator processes**:
   - Detects language
   - Calls Ollama with message
4. **Ollama generates response** (takes 10-30+ seconds)
5. **Frontend receives and streams response** to user

## Success Indicators
- ✅ `/api/v1/chat` responds with status 200 (not 504)
- ✅ Response contains `"response"` field with actual text
- ✅ No timeout error messages in logs
- ✅ Curiosity Ocean UI shows responses instead of "Ocean-Core stream failed"

## Additional Notes
- The 45-second timeout can be adjusted via environment variable `OCEAN_FAST_TIMEOUT_SECONDS`
- Ollama models available: llama3.1:8b (4.9GB), llama3.2:3b (2GB)
- Frontend has proper catch-all routes targeting `/api/v1/*` paths
- OpenMind service integration also deployed and running

## If Issues Persist
Check:
1. Ollama is responding: `curl http://ollama:11434/api/tags`
2. Ollama can generate: `curl -X POST http://ollama:11434/api/generate -d '{"model":"llama3.2:3b","prompt":"test"}'`
3. Container logs: `docker logs clisonix-ocean-core --tail 50`
4. Network connectivity between containers: All services on `clisonix-net`
