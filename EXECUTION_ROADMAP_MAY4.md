# 🎯 May 4, 2026 — Execution Roadmap (Final)

**Status**: All analysis complete, documentation ready, 3 parallel tracks identified.

---

## ✅ What Was Analyzed

### 4-Point Root Cause Analysis
**Problem 1**: Node.js 20 deprecation (CI actions)  
**Root Cause**: `actions/checkout@v4` and `actions/setup-python@v5` locked to Node 20 (EOL: June 2, 2026)  
**Fix**: Updated to v4.2 / v6 (Node 24-compatible)  
**Status**: ✅ COMPLETE (Commit 0cc6ee33)

**Problem 2**: Git authentication failure (Exit code 128)  
**Root Cause**: Missing explicit `GITHUB_TOKEN` in checkout action  
**Fix**: Added `token: ${{ secrets.GITHUB_TOKEN }}` (all 3 jobs)  
**Status**: ✅ COMPLETE (Commit 0cc6ee33)

**Problem 3**: ecppack missing (Exit code 127)  
**Root Cause**: APT package `fpga-icestorm` doesn't include `ecppack`; must build from prjlattice  
**Fix**: Added CMake build for prjlattice in kloud-soc-build job (+5 min)  
**Status**: ✅ COMPLETE (Commit 0cc6ee33)

**Problem 4**: Netscan detection (Hetzner security alert)  
**Root Cause**: Legitimate CI traffic (DNS, git clone, cargo, npm) flagged as scanning  
**Fix**: Request whitelist for 178.63.89.121 from Hetzner support  
**Status**: 🟡 ADVISORY (not blocking, template provided)

---

## 📋 Documentation Created (Commit 7ceff188)

1. **`.github/CI_PROBLEMS_ROOT_ANALYSIS_MAY4.md`** (150 lines)
   - Root cause analysis for all 4 problems
   - Verification checklist
   - Impact assessment
   - Fix details with code snippets

2. **`HETZNER_SUPPORT_TEMPLATE.md`** (35 lines)
   - Pre-written support ticket
   - IP address + use case details
   - Expected SLA (1–2 business days)
   - Copy-paste ready

3. **`PRODUCTION_DEPLOYMENT_CHECKLIST.md`** (280 lines)
   - 12-step validation procedure
   - Health check commands (local + HTTPS)
   - Smoke test paths (web, api, ocean-core)
   - Rollback procedures + incident response
   - Sign-off checklist

---

## 🚀 Parallel Execution Tracks

### TRACK 1: CI Validation (20–25 min)
**Goal**: Verify all 3 jobs pass without exit codes 127, 128, or deprecation warnings

**Steps**:
```bash
# Trigger workflow (automatic on push, or manual)
# https://github.com/Web8kameleon-hub/clisonix.com/actions/workflows/kloud-edge-ci.yml

# Monitor these jobs:
✓ kloud-bridge-status (3–5 min)
✓ rust-node-agent (2–3 min)
✓ kloud-soc-build (20–25 min) ← includes prjlattice build

# Verify artifacts uploaded:
- firmware.hex (RISC-V firmware)
- kloud_soc.bit (ECP5 bitstream)
```

**Success Criteria**:
- ✅ All 3 jobs: exit code 0
- ✅ No "ecppack: command not found" (exit 127)
- ✅ No git auth failures (exit 128)
- ✅ No Node 20 deprecation warnings
- ✅ Artifacts uploaded to GitHub Actions

**Owner**: GitHub Actions (automated, you monitor)  
**Timeline**: 25 min from trigger  
**Blocker for**: Track 3 (deployment)

---

### TRACK 2: Hetzner Whitelist Request (1–2 business days)
**Goal**: Prevent netscan alerts during future CI runs

**Steps**:
```
1. Open Hetzner support ticket:
   https://support.hetzner.com/

2. Copy content from:
   HETZNER_SUPPORT_TEMPLATE.md

3. Submit with:
   - Subject: "Whitelist IP 178.63.89.121 for GitHub Actions CI automation"
   - Include: Traffic patterns, expected schedule
   
4. Wait for confirmation email (~1–2 business days)

5. Verify next CI run doesn't trigger netscan alert
```

**Success Criteria**:
- ✅ Support ticket accepted
- ✅ 178.63.89.121 whitelisted in Hetzner abuse system
- ✅ Next CI run shows no netscan alerts

**Owner**: You (manual support request)  
**Timeline**: Async (SLA: 1–2 business days)  
**Blocker for**: Nothing (advisory only, not blocking CI/deployment)

---

### TRACK 3: Production Deployment (After Track 1 passes)
**Goal**: Deploy latest code (infra hardening + polling fixes) to Hetzner

**Steps** (from PRODUCTION_DEPLOYMENT_CHECKLIST.md):
```bash
1. Verify Track 1 CI validation passed
2. SSH to Hetzner: ssh root@178.63.89.121
3. Pull latest: git pull origin main
4. Rebuild services: docker-compose ... up -d --build web api ocean-core
5. Health checks: curl localhost:3000, localhost:8000, localhost:8001
6. Public HTTPS tests: curl https://www.clisonix.com
7. Verify secrets loaded: docker exec clisonix-web env | grep AUTH
8. Smoke test critical paths (auth, api, kitchen)
9. Check logs for errors
10. Monitor Cloudflare analytics
11. Final confirmation
12. Document deployment timestamp + commit hash
```

**Success Criteria**:
- ✅ Web service: HTTP 200 on https://www.clisonix.com
- ✅ API service: /health endpoint responds
- ✅ Google Auth: OAuth callback works
- ✅ Kitchen: /api/kitchen/health responds
- ✅ No errors in logs (first 2 minutes)
- ✅ Cloudflare showing traffic

**Owner**: You (manual deployment)  
**Timeline**: 50 min total (CI 25 + deployment 15 + tests 10)  
**Dependencies**: Track 1 (CI validation must pass first)  
**Rollback available**: Yes (documented procedure)

---

## 📊 Execution Timeline

### Scenario A: All Parallel (Optimal)
```
Time 0:00
  ├─ Track 1: Trigger CI workflow
  ├─ Track 2: Open Hetzner support ticket (2 min)
  └─ Track 3: Wait for Track 1

Time 0:25 (CI completes)
  └─ Track 3: Begin deployment

Time 1:15 (Deployment + smoke tests complete)
  └─ ✅ ALL DONE
  
Track 2 continues async (whitelist approval within 1–2 business days)
```

**Total active time**: 75 minutes  
**Critical path**: Track 1 (CI) + Track 3 (deployment)

---

### Scenario B: Sequential (Conservative)
```
Time 0:00 → Track 1 (CI validation)
Time 0:25 → Review results
Time 0:30 → Track 2 (Hetzner ticket)
Time 0:35 → Track 3 (Deployment)
Time 1:25 → Complete
```

**Total active time**: 85 minutes  
**Risk**: Lower (longer validation window)

---

## 🎬 Next Action

**Choose your track**:

```
Option A: "Let's validate CI first, then deploy immediately"
  ← Recommended (parallel execution, fastest)
  
Option B: "Open Hetzner ticket, then deploy after CI is confirmed"
  ← Sequential approach
  
Option C: "Just deploy (CI + Track 3, skip Hetzner for now)"
  ← Fast, not recommended (netscan alerts may occur)
```

---

## ✨ What You Get After Execution

### Post-Track 1 (CI Validation)
✅ Verified: All 3 CI jobs pass without errors  
✅ Confirmed: FPGA bitstream builds successfully (ecppack works)  
✅ Artifacts: firmware.hex + kloud_soc.bit available for deployment

### Post-Track 2 (Hetzner Whitelist)
✅ IP 178.63.89.121 whitelisted for CI automation  
✅ Future CI runs: No more netscan alerts  
✅ Confidence: Can run CI 2–6x daily without abuse alerts

### Post-Track 3 (Production Deployment)
✅ Latest code live on https://www.clisonix.com  
✅ Includes:
  - Autod eploy hardening (scripts/hetzner-autodeploy.sh)
  - Security posture monitoring (/api/security/posture)
  - CSP reporting (Content Security Policy)
  - Admin security dashboard
  - Dependency lock file updates
  
✅ Services verified:
  - Web (Next.js app)
  - API (FastAPI backend)
  - Ocean Core (Stream processing)
  
✅ Auth working:
  - Google OAuth (redirects configured)
  - NextAuth session (NEXTAUTH_SECRET loaded)
  - Kitchen module (internal protocol system)

---

## 📞 Support References

**If CI validation fails**:
→ Check `.github/CI_PROBLEMS_ROOT_ANALYSIS_MAY4.md` for each exit code

**If deployment fails**:
→ Use PRODUCTION_DEPLOYMENT_CHECKLIST.md rollback section

**If GitHub secret scanning blocks push**:
→ Already fixed (Commit 7ceff188 removed exposed secrets)

**If Hetzner support is slow**:
→ Alternative: Move CI to GitHub-hosted runners (Option B in analysis)

---

## 📋 Summary Table

| Item | Status | Location | Action |
|------|--------|----------|--------|
| **CI Fixes** | ✅ Complete | Commit 0cc6ee33 | Trigger workflow to validate |
| **Root Analysis** | ✅ Complete | .github/CI_PROBLEMS_ROOT_ANALYSIS_MAY4.md | Reference for troubleshooting |
| **Hetzner Template** | ✅ Ready | HETZNER_SUPPORT_TEMPLATE.md | Copy & submit to support |
| **Deploy Checklist** | ✅ Ready | PRODUCTION_DEPLOYMENT_CHECKLIST.md | Follow 12-step procedure |
| **Infra Hardening** | ✅ Complete | Commit 494e28b5 | Already in codebase |
| **Google Auth** | ✅ Verified | .env (git-ignored) | Real keys confirmed present |
| **Kitchen Module** | ✅ Verified | services/kitchen-api | Internal, no external deps |
| **GitHub Push** | ✅ Fixed | Commit 7ceff188 | Secrets redacted, push OK |

---

**Ready for execution?** 🚀

**Your decision**: Which track order?
1. Parallel (A) — Fastest, all at once
2. Sequential (B) — Conservative, step-by-step
3. Deploy only (C) — Skip Hetzner for now

Let me know, and I'll orchestrate the execution!
