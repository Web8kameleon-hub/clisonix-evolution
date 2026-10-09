# 🌊 OCEAN CORE v2 - HETZNER DEPLOYMENT GUIDE

## Overview

This guide covers deploying all 7 Ocean Core v2 implementations to the Hetzner production server (46.225.14.83) with **ZERO downtime** for existing services.

**Key Stats:**
- ✅ 7 complete Ocean Core implementations ready
- ✅ Safe deployment (only touches Ocean Core services)
- ✅ Full backup & rollback capability
- ✅ Health checks verify each service
- ✅ Protects live client services

---

## Prerequisites

### Local Machine (Windows/macOS/Linux)

1. **SSH Access Configured**
   ```bash
   # Test SSH connection
   ssh -i ~/.ssh/id_rsa root@46.225.14.83
   ```

2. **Files Present in Current Directory**
   ```
   ✓ docker-compose.yml (updated with Ocean services)
   ✓ ocean-core/Dockerfile
   ✓ ocean-core/Dockerfile.multimodal
   ✓ ocean-core/Dockerfile.strict-chat
   ✓ ocean-core/Dockerfile.blerina
   ✓ HETZNER_DEPLOY_v2.sh (Linux/macOS)
   ✓ HETZNER_DEPLOY_v2.ps1 (Windows)
   ```

### Hetzner Server (46.225.14.83)

- ✅ Docker installed
- ✅ Docker Compose installed
- ✅ Git repository cloned to `/root/clisonix-cloud`
- ✅ Ollama service running (provides LLM backend)
- ✅ SSH access enabled

---

## Service Mapping

| Service | Port | Function | Model |
|---------|------|----------|-------|
| ocean-core | 8030 | Primary (MegaLayerEngine, ResponseOrchestratorV5) | llama3.1:8b |
| ocean-core-multimodal | 8033 | Vision/Audio/Document/Reasoning | llama3.1:8b + llava + whisper |
| ocean-core-strict-chat | 8035 | Admin Mode (IRON RULES enforcement) | llama3.1:8b |
| ocean-core-blerina | 8032 | Advanced Architecture (EAP, gap detection) | llama3.1:8b |

---

## Deployment Steps

### Step 1: Choose Deployment Method

#### Option A: Linux/macOS (Bash Script)
```bash
chmod +x HETZNER_DEPLOY_v2.sh
./HETZNER_DEPLOY_v2.sh [host] [user] [port]

# Examples:
./HETZNER_DEPLOY_v2.sh 46.225.14.83 root 22
./HETZNER_DEPLOY_v2.sh                    # Uses defaults
```

#### Option B: Windows (PowerShell Script)
```powershell
# PowerShell 7+ required
./HETZNER_DEPLOY_v2.ps1 -HetznerHost 46.225.14.83 -HetznerUser root -HetznerPort 22

# Or with defaults:
./HETZNER_DEPLOY_v2.ps1
```

#### Option C: Manual Deployment (If Scripts Unavailable)
```bash
# 1. SSH to Hetzner
ssh -i ~/.ssh/id_rsa root@46.225.14.83

# 2. Backup existing config
mkdir -p /root/clisonix-backups
cp /root/clisonix-cloud/docker-compose.yml /root/clisonix-backups/docker-compose.yml.$(date +%s)

# 3. Transfer updated docker-compose.yml (from your local machine)
scp -i ~/.ssh/id_rsa docker-compose.yml root@46.225.14.83:/root/clisonix-cloud/

# 4. Transfer Dockerfiles
scp -i ~/.ssh/id_rsa ocean-core/Dockerfile* root@46.225.14.83:/root/clisonix-cloud/ocean-core/

# 5. Pull latest code
cd /root/clisonix-cloud && git pull origin main

# 6. Deploy only Ocean services
docker-compose up -d --build \
    ocean-core \
    ocean-core-multimodal \
    ocean-core-strict-chat \
    ocean-core-blerina

# 7. Wait for health checks
sleep 10
docker ps -a | grep ocean-core
```

---

## Verification After Deployment

### Quick Health Check
```bash
# Run from local machine
curl -v http://46.225.14.83:8030/health
curl -v http://46.225.14.83:8033/health
curl -v http://46.225.14.83:8035/health
curl -v http://46.225.14.83:8032/health

# All should return: HTTP 200 OK
```

### SSH-Based Verification
```bash
ssh root@46.225.14.83 "docker ps -a | grep ocean-core"

# Expected output:
# clisonix-ocean-core-multimodal   ...   Up (healthy)
# clisonix-ocean-core-strict-chat  ...   Up (healthy)
# clisonix-ocean-core-blerina      ...   Up (healthy)
# clisonix-ocean-core              ...   Up (healthy)
```

### Check Logs for Errors
```bash
ssh root@46.225.14.83 "docker logs clisonix-ocean-core | tail -50"
ssh root@46.225.14.83 "docker logs clisonix-ocean-core-multimodal | tail -50"
ssh root@46.225.14.83 "docker logs clisonix-ocean-core-strict-chat | tail -50"
ssh root@46.225.14.83 "docker logs clisonix-ocean-core-blerina | tail -50"
```

### Verify Live Services Unaffected
```bash
# SSH to server
ssh root@46.225.14.83

# List all containers
docker ps -a

# Check non-Ocean services are still running
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -v ocean-core
```

---

## Rollback Procedure

### If Something Goes Wrong

```bash
# SSH to Hetzner server
ssh root@46.225.14.83

# List available backups
ls -lh /root/clisonix-backups/

# Restore from most recent backup
cp /root/clisonix-backups/docker-compose.yml.TIMESTAMP /root/clisonix-cloud/docker-compose.yml

# Stop affected services
docker-compose -f /root/clisonix-cloud/docker-compose.yml \
    stop ocean-core ocean-core-multimodal ocean-core-strict-chat ocean-core-blerina

# Restart with old config
cd /root/clisonix-cloud && docker-compose up -d

# Verify services are running
docker ps -a | grep ocean-core
```

---

## Safety Features

### What's Protected

✅ **Non-Ocean Services**: Other running services are NOT stopped or modified
✅ **Configuration**: Original docker-compose.yml is backed up before modification
✅ **Data**: All volumes and data are preserved
✅ **Rollback**: Can revert to previous deployment in seconds

### What Happens

1. **Backup**: Existing docker-compose.yml timestamped
2. **Transfer**: Updated configs sent to server
3. **Stop**: ONLY Ocean Core services stopped (others continue)
4. **Build**: ONLY Ocean Core containers rebuilt
5. **Start**: ONLY Ocean Core services restarted
6. **Verify**: Health checks confirm each service is responsive
7. **Check**: Confirms no impact on other services

---

## Troubleshooting

### "Connection refused" on Port 8030/8033/8035/8032

**Cause**: Service not yet healthy or not listening
**Fix**:
```bash
# SSH to server
ssh root@46.225.14.83

# Check service status
docker ps -a | grep ocean-core

# If not running or unhealthy, check logs
docker logs clisonix-ocean-core

# Wait longer (services can take 30-60 seconds to start)
sleep 30

# Try health check again
curl -sf http://localhost:8030/health

# If still fails, check Ollama is running
docker ps | grep ollama
```

### Service Crashes After Startup

**Cause**: Import error, missing dependency, or misconfiguration
**Fix**:
```bash
# Check full logs for error details
ssh root@46.225.14.83 "docker logs clisonix-ocean-core | tail -100"

# Common issues:
# - Missing module import (check if ocean_core_full.py, real_answer_engine exist)
# - Ollama not responding (ensure ollama service running on port 11434)
# - Port already in use (check: docker ps -a)
```

### Other Services Stopped Unexpectedly

**Cause**: Manual error or script issue
**Fix**:
```bash
# SSH to server
ssh root@46.225.14.83

# Restart docker-compose with original config
cd /root/clisonix-cloud
git checkout docker-compose.yml  # Restore from git

# Restart all services
docker-compose up -d

# Verify non-Ocean services are back
docker ps | grep -v ocean-core
```

---

## Performance Monitoring

### Monitor Service Resource Usage
```bash
ssh root@46.225.14.83 "docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep ocean-core"
```

### Check Service Latency
```bash
# Measure response time
time curl -sf http://46.225.14.83:8030/health

# Expected: < 100ms for local machine, < 500ms over internet
```

### Monitor Container Logs in Real-Time
```bash
# Follow specific service logs
ssh root@46.225.14.83 "docker logs -f clisonix-ocean-core"

# Ctrl+C to stop following
```

---

## What's New in v2

### Ocean Core v2 Features

**ocean_core_full.py (Port 8030)**
- ✅ MegaLayerEngine: 14 billion combinations
- ✅ ResponseOrchestratorV5: Production brain
- ✅ TrinityDebate: 5-persona debate system
- ✅ Zürich Engine: 9-stage deterministic reasoning

**ocean_multimodal.py (Port 8033)**
- ✅ Vision processing (llava)
- ✅ Audio processing (whisper)
- ✅ Document processing
- ✅ Integrated reasoning

**ocean_strict_chat.py (Port 8035)**
- ✅ Admin mode
- ✅ IRON RULES enforcement
- ✅ Restricted conversation mode
- ✅ Audit logging

**ocean_blerina_core.py (Port 8032)**
- ✅ Advanced architecture processing
- ✅ EAP pipeline
- ✅ Gap detection
- ✅ Quality validation

---

## Post-Deployment Checklist

- [ ] SSH into Hetzner confirms all 4 Ocean services running
- [ ] curl http://46.225.14.83:8030/health returns 200 OK
- [ ] curl http://46.225.14.83:8033/health returns 200 OK
- [ ] curl http://46.225.14.83:8035/health returns 200 OK
- [ ] curl http://46.225.14.83:8032/health returns 200 OK
- [ ] Non-Ocean services still running (verify with docker ps)
- [ ] No error messages in Docker logs
- [ ] Live clients report normal service
- [ ] Backup saved in /root/clisonix-backups/
- [ ] Rollback procedure documented

---

## Support & Questions

For deployment issues:
1. Check logs: `docker logs clisonix-ocean-core-*`
2. Run diagnostics: `docker-compose config`
3. Verify Hetzner network: `curl http://localhost:8030/health`
4. Test local connectivity: `telnet 46.225.14.83 8030`

---

**Version**: 2.0.0  
**Updated**: December 2024  
**Status**: Production Ready ✅
