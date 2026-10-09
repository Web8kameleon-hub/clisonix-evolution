# ULTRA Reporting Command Center - Real Data Configuration

**Status**: ✅ Fixed - Ready for Deployment

## Problem

The ULTRA Reporting Command Center dashboard was showing "Unavailable" and "0" values for all metrics because the frontend (`clisonix-web` service) couldn't reach the real reporting service (`clisonix-reporting`).

### Dashboard Issues

```
Service Health Monitor
0 services discovered
0/0 containers running
0 Kloud nodes
```

Metrics showing as "Unavailable":
- Total Requests (24h)
- Error Rate  
- Average Response Time
- Cache Hit Rate
- Database Status
- Running Containers

## Root Cause

The web service was missing the `REPORTING_INTERNAL_URL` environment variable, which prevented it from connecting to the reporting service at `http://clisonix-reporting:8001`.

### Connection Flow

```
Frontend Dashboard
    ↓
/api/proxy/reporting-dashboard (Next.js API Route)
    ↓
fetchJsonFromCandidates(group: "reporting", path: "/api/reporting/dashboard")
    ↓
REPORTING_INTERNAL_URL config → looks for http://clisonix-reporting:8001
    ↓
❌ NOT SET → returns null → dashboard shows "Unavailable"
```

## Solution

Added `REPORTING_INTERNAL_URL: "http://clisonix-reporting:8001"` to the `web` service environment in `docker-compose.yml`.

### Changes Made

**File**: `docker-compose.yml`

**Commit**: `e2c5b626` - "fix(reporting): connect web service to reporting endpoint via REPORTING_INTERNAL_URL"

```yaml
web:
  environment:
    API_INTERNAL_URL: "http://clisonix-api:8000"
    OCEAN_INTERNAL_URL: "http://ocean-core:8030"
    REPORTING_INTERNAL_URL: "http://clisonix-reporting:8001"  # ← ADDED
    # ... other vars
  depends_on:
    api:
      condition: service_healthy
    ocean-core:
      condition: service_healthy
    reporting:  # ← ADDED
      condition: service_healthy
    # ... other services
```

## What the Reporting Service Provides

The reporting service (`clisonix-reporting` on port 8001) implements **REAL DATA** endpoints following NO_FAKE_DATA_POLICY:

### 1. System Metrics (`GET /api/reporting/system-metrics`)
**Real data from psutil:**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Uptime (seconds)
- Network I/O

**No synthetic data**: Returns actual system stats or null/503 if unavailable.

### 2. Docker Container Monitoring (`GET /api/reporting/docker-containers`)
**Real data from Docker CLI / Docker SDK:**
- List of all running containers
- Container status (running, exited, etc.)
- Health status
- Port mappings
- Image names

**No synthetic data**: Queries actual Docker daemon or returns error.

### 3. Docker Statistics (`GET /api/reporting/docker-stats`)
**Real data from docker stats:**
- CPU percentage per container
- Memory usage per container
- Network I/O per container
- Block I/O per container

**No synthetic data**: Live data or error response.

### 4. Dashboard Aggregation (`GET /api/reporting/dashboard`)
**Combines all real data sources:**
- System metrics (psutil)
- Container status (Docker daemon)
- Upstream service health (HTTP probes to real services)
- Project materials inventory (filesystem scan)
- API metrics from upstream services

**Returns complete real dashboard or degraded status if some upstream unavailable.**

### 5. Capabilities (`GET /api/reporting/capabilities`)
**Reports what data sources are available:**
- psutil availability
- Docker SDK availability
- Excel export capability
- PowerPoint export capability
- Available upstream integrations

## Data Flow After Fix

```
Frontend Dashboard
    ↓
GET /api/proxy/reporting-dashboard
    ↓
Next.js API Route: /apps/web/app/api/proxy/reporting-dashboard/route.ts
    ↓
fetchJsonFromCandidates({
  group: "reporting",
  path: "/api/reporting/dashboard"
})
    ↓
REPORTING_INTERNAL_URL = "http://clisonix-reporting:8001"
    ↓
GET http://clisonix-reporting:8001/api/reporting/dashboard
    ↓
clisonix-reporting service processes:
  1. Collects real system metrics (psutil)
  2. Lists real containers (docker ps)
  3. Gets real stats (docker stats)
  4. Probes upstream services
  5. Scans project materials
    ↓
Returns complete real dashboard payload
    ↓
Dashboard displays REAL data:
  ✓ N containers running
  ✓ X% CPU usage
  ✓ Y GB memory
  ✓ Z% disk usage
  ✓ Service health from real probes
```

## Verification

### Build and Start

```bash
# Rebuild services with new config
docker-compose up --build -d

# Verify reporting service is running
docker ps | grep reporting
# Should show: clisonix-reporting UP

# Check logging
docker logs clisonix-reporting
# Should show: "connection successful" or health checks
```

### Test Endpoints

Run the validation script:

```bash
bash scripts/validate-reporting-endpoints.sh
```

Expected output:
```
Testing Reporting Health... ✓ PASS (HTTP 200, 450 bytes)
Testing Docker Containers... ✓ PASS (HTTP 200, 2847 bytes)
Testing System Metrics... ✓ PASS (HTTP 200, 680 bytes)
Testing Dashboard... ✓ PASS (HTTP 200, 5923 bytes)
```

### Manual Testing

```bash
# Test reporting service directly
curl http://localhost:8001/api/reporting/system-metrics | jq

# Test via web service proxy
curl http://localhost:3000/api/proxy/reporting-dashboard | jq

# Check specific metrics
curl http://localhost:8001/api/reporting/docker-containers | jq '.containers | length'
```

Expected response shows real data:
```json
{
  "timestamp": "2026-04-22T18:42:15.832945",
  "data_type": "REAL",
  "system": {
    "cpu_percent": 7.5,
    "memory_percent": 71.2,
    "disk_percent": 29.5,
    "uptime_seconds": 172800,
    "uptime_formatted": "2d 0h 0m"
  },
  "docker": {
    "total": 101,
    "healthy": 100,
    "containers": [
      {"name": "clisonix-api", "status": "Up 2 days", "healthy": true},
      {"name": "clisonix-web", "status": "Up 2 days", "healthy": true},
      ...
    ]
  },
  ...
}
```

## Policy Compliance: NO_FAKE_DATA ✓

This solution follows **NO_FAKE_DATA_POLICY.md**:

### ✓ Real Data Only
- System metrics from psutil (actual CPU, memory, disk)
- Container data from Docker daemon (actual running containers)
- Service health from actual HTTP probes (no synthetic responses)
- No placeholder values like "0" or "Unavailable" when data is available

### ✓ Proper Error Handling
- Returns HTTP 503 if upstream unavailable (not synthetic data)
- Returns HTTP 200 with complete real data if available
- No fallback snapshots or degraded mode synthetic data

### ✓ No Fake/Demo Values
- No hardcoded sample data
- No mock responses
- No fallback chains with fake candidates
- Every metric is from actual source or error response

### ✓ Configuration-Driven
- Environment variables control upstream URLs
- No hardcoded service addresses
- Respects deployment environment (local, Docker, production)

## Deployment Steps

1. **Code**: Commit applied (commit e2c5b626)
2. **Config**: docker-compose.yml updated with REPORTING_INTERNAL_URL
3. **Dependencies**: requirements.txt already has all needed packages
4. **Verification**: Run `scripts/validate-reporting-endpoints.sh`
5. **Deployment Trigger**: Normal CI/CD workflow (rebuild-web scope or full-stack)

### For Hetzner Production (46.225.14.83)

```bash
# SSH to host
ssh root@46.225.14.83

# Pull latest changes
cd /root/Clisonix-cloud
git pull origin main

# Rebuild and restart
docker-compose up --build -d reporting web

# Verify health
curl http://localhost:8001/health
curl http://localhost:3000/api/proxy/reporting-dashboard | head -c 200

# Check logs
docker logs clisonix-reporting --tail 20
docker logs clisonix-web --tail 20
```

## Files Changed

```
docker-compose.yml
  - Added REPORTING_INTERNAL_URL: "http://clisonix-reporting:8001"
  - Added reporting to web service depends_on
  
scripts/validate-reporting-endpoints.sh
  - New: Validation script for all reporting endpoints
  
ULTRA_REPORTING_CONFIGURATION.md
  - New: This documentation file
```

## Next Steps

1. ✅ Environment variable configured
2. ⏳ Deploy to staging/production (rebuild-web or full deployment)
3. ⏳ Verify dashboard shows real Docker container counts
4. ⏳ Verify system metrics display real CPU/memory/disk usage
5. ⏳ Monitor reporting service health (check logs for errors)
6. ⏳ Set up automated monitoring of reporting endpoint availability

## Troubleshooting

### Dashboard still shows "Unavailable"

```bash
# 1. Check environment variable is set
docker exec clisonix-web env | grep REPORTING_INTERNAL_URL
# Should output: REPORTING_INTERNAL_URL=http://clisonix-reporting:8001

# 2. Check reporting service is healthy
docker ps | grep reporting
# Should show: ... (healthy)

# 3. Check can reach reporting service from web container
docker exec clisonix-web curl -s http://clisonix-reporting:8001/health | head -c 100

# 4. Check web service logs for errors
docker logs clisonix-web --since 5m | grep -i reporting
```

### Reporting service not starting

```bash
# Check logs
docker logs clisonix-reporting

# Verify Docker socket is mounted
docker inspect clisonix-reporting | grep -A5 Mounts

# Test psutil in container
docker exec clisonix-reporting python3 -c "import psutil; print(psutil.cpu_percent())"
```

### Slow response times

The reporting service has built-in timeouts to prevent hanging:
- System metrics: 0.9s timeout
- Docker containers: 1.25s timeout
- Docker stats: 1.25s timeout
- Project materials: 1.0s timeout
- Upstream probes: 1.75s timeout

If timeouts occur:
1. Check host system load
2. Check Docker daemon health
3. Check network connectivity to upstream services

## References

- Policy: [NO_FAKE_DATA_POLICY.md](../NO_FAKE_DATA_POLICY.md)
- Service: [services/reporting/main.py](../services/reporting/main.py)
- Dashboard: [apps/web/app/modules/reporting-dashboard/page.tsx](../apps/web/app/modules/reporting-dashboard/page.tsx)
- Routes: [apps/web/app/api/proxy/reporting-dashboard/route.ts](../apps/web/app/api/proxy/reporting-dashboard/route.ts)
- Upstream config: [apps/web/app/api/_lib/upstream.ts](../apps/web/app/api/_lib/upstream.ts)

---

**Created**: 2026-04-22
**Fixed By**: GitHub Copilot
**Status**: Ready for Deployment
