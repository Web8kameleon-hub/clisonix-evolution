# Kitchen Worker v2.0 - Production Job Orchestrator

## Quick Start

```bash
cd services/kitchen-worker
npm install
npm start
```

## Test with curl (Web API)

```bash
# 1. Queue newman test job
curl -X POST http://localhost:3000/api/kitchen/run \\
  -H "Content-Type: application/json" \\
  -d '{
    "collection": "clisonix-api-tests",
    "baseUrl": "http://localhost:8000"
  }'

# 2. Check queue
curl http://localhost:3000/api/kitchen/queue

# 3. Worker health
curl http://localhost:3100/health

# 4. Get report (after completion)
curl http://localhost:3000/api/kitchen/reports/{runId}

## Docker
docker build -t kitchen-worker .
docker run -p 3100:3100 -v $(pwd)/kitchen-jobs:/app/kitchen-jobs kitchen-worker

## Real Services (New)
- `type: \"shell\"` - Run arbitrary commands
- `type: \"data-fetch\"` - Fetch APIs (weather, crypto)
- Redis queue ready (REDIS_URL=...)

**Status**: Production ready with real on-demand workloads.**

