# 🌊 OCEAN CORE v2 - DEPLOYMENT EXECUTION CHECKLIST

**Print this page and check off items as you go!**

---

## ✅ Latest Execution Snapshot (2026-02-25)

- [x] Deployment executed on `hetzner-new` (`/opt/clisonix-cloud`)
- [x] Backup created: `/root/clisonix-backups/docker-compose.yml.20260225075522`
- [x] Ocean Core services deployed and started:
  - [x] ocean-core (8030)
  - [x] ocean-core-multimodal (8033)
  - [x] ocean-core-strict-chat (8035)
  - [x] ocean-core-blerina (8032)
- [x] Health endpoints verified with HTTP 200 on all 4 ports
- [x] Web routes rebuilt and verified:
  - [x] `/api/debate` (200)
  - [x] `/api/zurich` (200)

---

## 📋 PRE-DEPLOYMENT PHASE (5-10 minutes)

### ☐ Section 1: Preparation

- [ ] Read [START_HERE_DEPLOYMENT_GUIDE.md](START_HERE_DEPLOYMENT_GUIDE.md)
- [ ] Understand the 3 deployment options available
- [ ] Choose deployment method:
  - [ ] Option 1: Bash script (Linux/macOS)
  - [ ] Option 2: PowerShell script (Windows)  
  - [ ] Option 3: Manual SSH commands

### ☐ Section 2: File Verification

- [ ] Verify all files present:

  ```bash
  ls -l docker-compose.yml HETZNER_DEPLOY_v2.* ocean-core/Dockerfile*
  ```

  Required files:
  - [ ] docker-compose.yml
  - [ ] HETZNER_DEPLOY_v2.sh (if using Bash)
  - [ ] HETZNER_DEPLOY_v2.ps1 (if using PowerShell)
  - [ ] ocean-core/Dockerfile
  - [ ] ocean-core/Dockerfile.multimodal
  - [ ] ocean-core/Dockerfile.strict-chat
  - [ ] ocean-core/Dockerfile.blerina

### ☐ Section 3: SSH Connectivity Check

- [ ] Test SSH connection to Hetzner:

  ```bash
  ssh -i ~/.ssh/id_rsa root@46.225.14.83 "echo SSH Connection Successful"
  ```

  Expected output: "SSH Connection Successful"
  
  ✓ SSH working: [____________]
  
- [ ] If SSH fails:
  - [ ] Check SSH key exists: `ls ~/.ssh/id_rsa`
  - [ ] Check file permissions: `chmod 600 ~/.ssh/id_rsa`
  - [ ] Verify IP address is correct
  - [ ] Contact DevOps if issues persist

### ☐ Section 4: Script Permissions (if using Bash)

- [ ] Make script executable:

  ```bash
  chmod +x HETZNER_DEPLOY_v2.sh
  ```

- [ ] Verify permissions:

  ```bash
  stat HETZNER_DEPLOY_v2.sh | grep -i access
  ```

### ☐ Section 5: Stakeholder Notification

- [ ] Notify relevant teams (optional but recommended):
  - [ ] DevOps team
  - [ ] Backend team
  - [ ] QA team
  - [ ] Note: No downtime for live services expected

### ☐ Section 6: Final Pre-Deployment Confirmation

- [ ] All files present ✓
- [ ] SSH working ✓
- [ ] Backup location confirmed: `/root/clisonix-backups/` ✓
- [ ] Rollback procedure understood ✓
- [ ] Ready to proceed? YES / NO

**If NO, do not proceed. Review issues first.**

---

## 🚀 DEPLOYMENT PHASE (5-10 minutes)

### ☐ Choose Execution Method

#### IF OPTION 1 (Linux/macOS Bash)

- [ ] Execute deployment:

  ```bash
  chmod +x HETZNER_DEPLOY_v2.sh
  ./HETZNER_DEPLOY_v2.sh 46.225.14.83 root 22
  ```

**Monitor for these messages**:

- [ ] "SSH connectivity verified" → ✅
- [ ] "Docker and Docker Compose available" → ✅
- [ ] "Backups created" → ✅
- [ ] "Files transferred" → ✅
- [ ] "Ocean Core services built and started" → ✅
- [ ] All services show "HEALTHY" → ✅

**If any message missing or shows ERROR**: STOP and check logs

---

#### IF OPTION 2 (Windows PowerShell)

- [ ] Execute deployment:

  ```powershell
  ./HETZNER_DEPLOY_v2.ps1 -HetznerHost 46.225.14.83 -HetznerUser root -HetznerPort 22
  ```

**Monitor for these messages**:

- [ ] "SSH connectivity verified" → ✅
- [ ] "Docker and Docker Compose available" → ✅
- [ ] "Backups created" → ✅
- [ ] "Files transferred" → ✅
- [ ] "Ocean Core services built and started" → ✅
- [ ] All services show "HEALTHY" → ✅

**If any message missing or shows ERROR**: STOP and check logs

---

#### IF OPTION 3 (Manual SSH)

Follow commands in [OCEAN_CORE_v2_HETZNER_GUIDE.md](OCEAN_CORE_v2_HETZNER_GUIDE.md#option-c-manual-deployment)

- [ ] Step 1: Backup existing
- [ ] Step 2: Transfer updated docker-compose.yml
- [ ] Step 3: Transfer Dockerfiles
- [ ] Step 4: Pull latest code from git
- [ ] Step 5: Deploy services
- [ ] Step 6: Wait 30 seconds
- [ ] Step 7: Check status

---

### ☐ Deployment Complete?

- [ ] Script execution finished without errors
- [ ] Backup created (note timestamp): _______________
- [ ] Services deployed
- [ ] Ready for verification? YES / NO

---

## 🏥 VERIFICATION PHASE (5-10 minutes)

### ☐ Section 1: Quick Health Check (1 minute)

- [ ] Run verification script:

  ```bash
  python verify_ocean_core_v2.py --host 46.225.14.83
  ```

**Expected output**:

```
[SUCCESS] ocean-core is HEALTHY ✓
[SUCCESS] ocean-core-multimodal is HEALTHY ✓
[SUCCESS] ocean-core-strict-chat is HEALTHY ✓
[SUCCESS] ocean-core-blerina is HEALTHY ✓
✅ All Ocean Core services are HEALTHY!
```

- [ ] All services show HEALTHY? YES / NO

**If NO**: Go to "Troubleshooting" section

### ☐ Section 2: Manual Endpoint Checks (2 minutes)

- [ ] Test ocean-core (port 8030):

  ```bash
  curl -v http://46.225.14.83:8030/health
  ```

  Expected: HTTP 200 OK → ✅

- [ ] Test ocean-core-multimodal (port 8033):

  ```bash
  curl -v http://46.225.14.83:8033/health
  ```

  Expected: HTTP 200 OK → ✅

- [ ] Test ocean-core-strict-chat (port 8035):

  ```bash
  curl -v http://46.225.14.83:8035/health
  ```

  Expected: HTTP 200 OK → ✅

- [ ] Test ocean-core-blerina (port 8032):

  ```bash
  curl -v http://46.225.14.83:8032/health
  ```

  Expected: HTTP 200 OK → ✅

- [ ] All endpoints responding? YES / NO

**If NO**: Check logs

```bash
ssh root@46.225.14.83 "docker logs clisonix-ocean-core | tail -50"
```

### ☐ Section 3: Docker Status Check (2 minutes)

- [ ] SSH to server and check container status:

  ```bash
  ssh root@46.225.14.83 "docker ps -a | grep ocean-core"
  ```
  
  Expected output (all should say "Up (healthy)"):
  - [ ] ocean-core: Up (healthy) ✓
  - [ ] ocean-core-multimodal: Up (healthy) ✓
  - [ ] ocean-core-strict-chat: Up (healthy) ✓
  - [ ] ocean-core-blerina: Up (healthy) ✓

- [ ] All containers running? YES / NO

### ☐ Section 4: Other Services Verification (2 minutes)

- [ ] Check other services still running:

  ```bash
  ssh root@46.225.14.83 "docker ps | grep -v ocean-core"
  ```

- [ ] Other services affected? YES / NO

**If YES**: Immediate rollback required!

### ☐ Section 5: Log Verification (2 minutes)

- [ ] Check for errors in Ocean Core logs:

  ```bash
  ssh root@46.225.14.83 "docker logs clisonix-ocean-core | grep -i 'error\|exception' | head -5"
  ```

- [ ] Errors found? YES / NO

**If YES**: Review error and determine if critical

### ☐ Section 6: Generate Report (Optional, 2 minutes)

- [ ] Generate HTML verification report:

  ```bash
  python verify_ocean_core_v2.py --host 46.225.14.83 --html deployment_report.html
  ```

- [ ] Report generated? YES / NO
- [ ] All services show Green (Healthy)? YES / NO

---

## ✅ POST-DEPLOYMENT PHASE (10 minutes)

### ☐ Section 1: Success Verification

Current status:

- [ ] All 4 Ocean Core services HEALTHY
- [ ] SSH endpoints responding HTTP 200
- [ ] Docker containers running properly
- [ ] Other services unaffected
- [ ] No critical errors in logs

**Summary**: ✅ DEPLOYMENT SUCCESSFUL

### ☐ Section 2: Documentation

- [ ] Record deployment details:

  ```
  Deployment Date: _______________
  Deployment Time: _______________
  Backup Location: /root/clisonix-backups/docker-compose.yml._______________
  Services Deployed: 4 (ocean-core, multimodal, strict-chat, blerina)
  Verification Time: _______________
  Status: ✅ SUCCESS
  ```

### ☐ Section 3: Monitoring Period (10 minutes)

- [ ] Monitor services for next 10 minutes:

  ```bash
  # Watch logs
  ssh root@46.225.14.83 "docker logs -f clisonix-ocean-core"
  ```

- [ ] Check every 2 minutes for errors
- [ ] Any issues detected? YES / NO

**If YES during monitoring**: See troubleshooting section

### ☐ Section 4: Team Notification

- [ ] Notify stakeholders of successful deployment:
  - [ ] DevOps team
  - [ ] Backend team
  - [ ] Production operations
  - [ ] Message template:

    ```
    ✅ Ocean Core v2 successfully deployed to production
    - Services: 4 (ocean-core, multimodal, strict-chat, blerina)
    - Ports: 8030, 8033, 8035, 8032
    - Status: All services HEALTHY
    - No impact on other services
    - Ready for production use
    ```

### ☐ Section 5: Finalización

- [ ] Deployment package stored/archived
- [ ] Backup verified accessible
- [ ] Rollback procedure documented
- [ ] Team aware of emergency procedures
- [ ] Final sign-off: Deployment complete ✓

---

## 🚨 TROUBLESHOOTING PHASE (If Issues Occur)

### ⚠️ During Deployment Script

**Issue**: Script fails or hangs

- [ ] Check error message displayed
- [ ] Run verification immediately:

  ```bash
  python verify_ocean_core_v2.py --host 46.225.14.83
  ```

- [ ] Check logs:

  ```bash
  ssh root@46.225.14.83 "docker logs clisonix-ocean-core 2>&1 | tail -100"
  ```

- [ ] If critical: Execute rollback (see below)

**Issue**: "Connection refused" or SSH fails

- [ ] Verify SSH access: `ssh root@46.225.14.83 "echo OK"`
- [ ] Check network connectivity: `ping 46.225.14.83`
- [ ] Verify SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- [ ] Check firewall rules

**Issue**: Services not coming up

- [ ] Wait 30 seconds (initial startup time)
- [ ] Check Ollama service: `ssh root@46.225.14.83 "curl http://localhost:11434/api/tags"`
- [ ] Check disk space: `ssh root@46.225.14.83 "df -h /"`
- [ ] Check memory: `ssh root@46.225.14.83 "free -h"`

---

### ⚠️ Post-Deployment Issues

**Issue**: Services show "Unhealthy" or "Exited"

- [ ] Check service logs: `docker logs clisonix-ocean-core | tail -50`
- [ ] Look for specific error messages
- [ ] Check if Ollama is running: `docker ps | grep ollama`
- [ ] If problem persists: Execute rollback

**Issue**: Health check timeouts still after 2 minutes

- [ ] Services may need more time to initialize
- [ ] Check process status: `docker top clisonix-ocean-core`
- [ ] Try manual health endpoint: `curl http://46.225.14.83:8030/health`
- [ ] If still failing: Check memory/CPU constraints

**Issue**: Other services stopped

- [ ] ⚠️ EMERGENCY: Execute immediate rollback
- [ ] ```bash
  ssh root@46.225.14.83 "cd /root/clisonix-cloud && git checkout docker-compose.yml && docker-compose up -d"

  ```
- [ ] Verify all services running: `docker ps`

- [ ] Investigate root cause in logs

---

## 🔄 EMERGENCY ROLLBACK PROCEDURE

**Use only if critical issues occur**

### Step 1: STOP (Do Not Panic)

- [ ] Issue identified
- [ ] Backup exists: `/root/clisonix-backups/docker-compose.yml.*`
- [ ] Ready to rollback

### Step 2: EXECUTE ROLLBACK

```bash
BACKUP_FILE=$(ssh root@46.225.14.83 "ls -t /root/clisonix-backups/docker-compose.yml.* | head -1")
ssh root@46.225.14.83 "cp $BACKUP_FILE /root/clisonix-cloud/docker-compose.yml && \
  cd /root/clisonix-cloud && \
  docker-compose down ocean-core ocean-core-multimodal ocean-core-strict-chat ocean-core-blerina && \
  docker-compose up -d"
```

- [ ] Rollback command executed
- [ ] Services restarting
- [ ] Wait 30 seconds

### Step 3: VERIFY ROLLBACK

- [ ] Check services running:

  ```bash
  ssh root@46.225.14.83 "docker ps"
  ```

- [ ] All services operational? YES / NO
- [ ] Other services running? YES / NO

### Step 4: POST-ROLLBACK

- [ ] Rollback successful ✓
- [ ] Investigate root cause
- [ ] Document issue
- [ ] Contact DevOps for analysis
- [ ] Plan for redeploy when ready

---

## 📞 ESCALATION PATH

**If deployment fails and you need immediate help:**

1. **Collect Information**:
   - [ ] Output of verify script in JSON format:

     ```bash
     python verify_ocean_core_v2.py --host 46.225.14.83 --json debug.json
     # Attach debug.json file
     ```

   - [ ] Last 100 lines from docker logs:

     ```bash
     ssh root@46.225.14.83 "docker logs clisonix-ocean-core | tail -100" > ocean_logs.txt
     # Attach ocean_logs.txt file
     ```

   - [ ] docker-compose version:

     ```bash
     docker-compose --version
     ```

2. **Contact DevOps** with:
   - [ ] debug.json file
   - [ ] ocean_logs.txt file
   - [ ] Command executed
   - [ ] Error message
   - [ ] Steps already attempted

3. **Priority**: ⚠️ HIGH (production deployment)

---

## ✨ DEPLOYMENT COMPLETION CHECKLIST

**Final verification before marking complete:**

- [ ] The four Ocean Core services deployed:
  - [ ] ocean-core (port 8030) ✓
  - [ ] ocean-core-multimodal (port 8033) ✓
  - [ ] ocean-core-strict-chat (port 8035) ✓
  - [ ] ocean-core-blerina (port 8032) ✓

- [ ] All services reporting HEALTHY status ✓

- [ ] HTTP health endpoints responding 200 ✓

- [ ] Other services unaffected ✓

- [ ] No errors in Docker logs ✓

- [ ] Backup created and accessible ✓

- [ ] Rollback procedure documented ✓

- [ ] Team notified of completion ✓

- [ ] Deployment complete and successful ✓

---

## 🎉 DEPLOYMENT COMPLETE

**Congratulations!** Ocean Core v2 is now running in production on Hetzner server 46.225.14.83 with:

✅ 4 operational services (Full, Multimodal, Strict-Chat, Blerina)  
✅ All services healthy and responsive  
✅ Other services unaffected  
✅ Complete backup and rollback capability  
✅ Comprehensive monitoring in place  

**Services ready for production use!** 🚀

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Verification Completed By**: _______________  
**Status**: ✅ **COMPLETE & VERIFIED**  

---

*Keep this checklist for your records*  
*Archive backup location information*  
*Share with operations team*
