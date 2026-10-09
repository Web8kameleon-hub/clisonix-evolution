# 🚀 Production Deployment Checklist — May 4, 2026

## Pre-Deployment Validation (CI Gate)

### Step 1: Trigger & Monitor CI Workflow

```bash
# Option A: Automated (push to main)
git push origin main
# → Automatically triggers kloud-edge-ci.yml

# Option B: Manual (on-demand)
# Visit: https://github.com/Web8kameleon-hub/clisonix.com/actions/workflows/kloud-edge-ci.yml
# Click: "Run workflow" → main branch
```

**Timeline**: ~25 minutes total
- kloud-bridge-status: ~3–5 min
- rust-node-agent: ~2–3 min
- kloud-soc-build: ~20–25 min (includes prjlattice build)

### Step 2: Validate All Jobs Pass

Monitor GitHub Actions page:
```
✅ kloud-bridge-status — PASS (exit code 0)
✅ rust-node-agent — PASS (exit code 0)
✅ kloud-soc-build — PASS (exit code 0)
   - Artifacts uploaded: firmware.hex, kloud_soc.bit
```

**Check for**:
- ❌ No exit codes 127 (ecppack missing)
- ❌ No exit codes 128 (git auth)
- ❌ No deprecation warnings from Node 20
- ⚠️ Netscan alerts → log for Hetzner ticket (not blocking)

### Step 3: Verify Artifact Consistency

```bash
# Check GitHub Actions artifacts are available
# https://github.com/Web8kameleon-hub/clisonix.com/actions/runs/[RUN_ID]/artifacts

# Expected files:
# - firmware.hex (RISC-V firmware)
# - kloud_soc.bit (ECP5 FPGA bitstream)
```

---

## Production Deployment (Hetzner 178.63.89.121)

### Step 4: SSH to Hetzner & Pull Latest

```bash
ssh root@178.63.89.121

# Verify current commit
cd /root/Clisonix-cloud
git log -1 --oneline
# Expected: 494e28b5 (or latest after your push)

# Pull latest changes
git pull origin main
# Expected output:
# - Updating 0cc6ee33..494e28b5
# - 10 files changed, 1016 insertions(+), 174 deletions(-)
```

### Step 5: Rebuild & Deploy Services

```bash
# Option A: Full rebuild (recommended on first deploy)
docker-compose -f docker-compose.75-services.yml \
  down --remove-orphans

docker-compose -f docker-compose.75-services.yml \
  up -d --build \
  web api ocean-core user-management
  
# Expected timeline: 8–12 minutes (includes npm install, pip install, build)

# Option B: Zero-downtime rolling update (if containers exist)
./scripts/hetzner-autodeploy.sh

# Option C: Manual service restart (if no code changes, just env vars)
docker-compose -f docker-compose.75-services.yml \
  restart web api ocean-core
```

### Step 6: Health Check — All Services

```bash
# Wait 30 seconds for services to be ready
sleep 30

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}"
# Expected: All 3 services showing "Up X seconds" (no "Exited")

# Test web service
curl -sS http://127.0.0.1:3000 | head -20
# Expected: HTML response (Next.js app)

# Test API service
curl -sS http://127.0.0.1:8000/health | jq .
# Expected: {"status": "ok", ...}

# Test ocean-core service
curl -sS http://127.0.0.1:8001/health | jq .
# Expected: Returns health/status JSON
```

### Step 7: PUBLIC HTTPS Validation

```bash
# From local machine (not SSH):

# Test web (HTTPS)
curl -sS https://www.clisonix.com | head -20
# Expected: HTML response from production

# Test API (HTTPS)
curl -sS https://www.clisonix.com/api/health | jq .
# Expected: {"status": "ok", ...}

# Test OAuth flow (browser)
# Visit: https://www.clisonix.com/api/auth/signin
# Expected: Google Auth redirect works
```

### Step 8: Verify Env Secrets Loaded

```bash
# SSH to Hetzner (continued)

# Check that services loaded env correctly
docker exec clisonix-web env | grep -i "GOOGLE\|AUTH\|KITCHEN"
# Expected: All auth keys should be present

docker exec clisonix-api env | grep -i "KITCHEN"
# Expected: KITCHEN_RUN_API_KEY=clisonix-kitchen-secret
```

### Step 9: Check Logs for Errors

```bash
# Monitor logs for first 2 minutes
docker-compose -f docker-compose.75-services.yml logs -f --tail=50

# Watch for:
# ✅ "Application startup complete" (API)
# ✅ "Server running on" (Web)
# ❌ "Connection error" / "Authentication failed" / "Exit 1"

# Exit after 2 min: Ctrl+C
```

---

## Post-Deployment Validation

### Step 10: Smoke Test Critical Paths

#### Web App
```bash
# 1. Page load
curl -sS https://www.clisonix.com -o /dev/null -w "Status: %{http_code}\n"
# Expected: 200

# 2. API proxy (Cloudflare analytics)
curl -sS "https://www.clisonix.com/api/proxy/docker-containers" -H "Accept: application/json" | jq .
# Expected: JSON with container list

# 3. Google Auth callback
curl -sS -L "https://www.clisonix.com/api/auth/signin" | grep -i "google" | head -5
# Expected: Contains google oauth redirect
```

#### API Service
```bash
# 1. Kitchen endpoints
curl -sS "https://www.clisonix.com/api/kitchen/health" | jq .
# Expected: {"service": "protocol-kitchen", "status": "healthy"}

# 2. System metrics
curl -sS "https://www.clisonix.com/api/system-metrics" | jq .
# Expected: CPU, memory, disk metrics

# 3. Database connectivity
curl -sS "https://www.clisonix.com/api/health" | jq ".database"
# Expected: "connected" or "healthy"
```

#### Ocean Core
```bash
# 1. Health
curl -sS "https://www.clisonix.com/api/ocean/health" | jq .
# Expected: healthy status

# 2. Metrics
curl -sS "https://www.clisonix.com/api/ocean/metrics" | jq .
# Expected: request counts, error rates, latency
```

### Step 11: Monitor Metrics & Alerts

```bash
# Check Cloudflare Analytics (in production)
# Dashboard: https://dash.cloudflare.com/
# Look for:
# ✅ Traffic flowing (requests/second > 0)
# ✅ Error rate < 1%
# ✅ No SSL errors
# ✅ Cache hit rate reasonable
```

```bash
# Check application logs (from SSH)
docker-compose -f docker-compose.75-services.yml logs --tail=100 api | grep ERROR
# Expected: No ERROR messages (warnings are OK)

docker-compose -f docker-compose.75-services.yml logs --tail=100 web | grep ERROR
# Expected: No ERROR messages
```

### Step 12: Final Confirmation

```bash
# Roll back if issues found:
git checkout [PREVIOUS_COMMIT_HASH]
docker-compose -f docker-compose.75-services.yml up -d --build web api ocean-core

# Commit deployment record
git log --oneline -1
# Verify commit hash matches what's deployed
```

---

## Rollback Plan (If Issues Found)

### Immediate Rollback
```bash
ssh root@178.63.89.121
cd /root/Clisonix-cloud

# Revert to last known good commit
git reset --hard [PREVIOUS_COMMIT_HASH]

# Restart services
docker-compose -f docker-compose.75-services.yml down
docker-compose -f docker-compose.75-services.yml up -d --build web api ocean-core

# Verify health
docker ps
curl -sS http://127.0.0.1:3000 -o /dev/null -w "Status: %{http_code}\n"
```

### Incident Reporting
```bash
# If rollback occurs, document:
# 1. What went wrong? (logs)
# 2. What was deployed? (commit hash)
# 3. When was it detected? (timestamp)
# 4. Who was notified? 

# Create incident post in #engineering:
# "[INCIDENT] Deployment 494e28b5 rolled back — [REASON]"
```

---

## Sign-Off Checklist

- [ ] CI workflow passed (all 3 jobs, no exit code 127/128)
- [ ] Web service health check: 200 OK
- [ ] API service health check: 200 OK
- [ ] Ocean core health check: 200 OK
- [ ] Google Auth callback working (OAuth flow tested)
- [ ] No error spikes in logs
- [ ] Cloudflare analytics showing traffic
- [ ] Commit hash verified in production
- [ ] Team notified of deployment

---

**Deployment template**: Ready for execution  
**Expected total time**: CI gate (25 min) + deployment (15 min) + smoke tests (10 min) = **50 minutes**  
**Risk level**: 🟢 **Low** (all changes backward compatible, CI validated)
