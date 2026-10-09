# CLISONIX MONETIZATION SECURITY GUIDE
## Enterprise-Grade Credential & Data Protection

**Classification:** SECURITY-CRITICAL  
**Audience:** Developers, DevOps, Leadership  
**Review Cycle:** Quarterly (90 days)

---

## 🔐 SECURITY LAYERS

```
┌─────────────────────────────────────────────────┐
│ Layer 1: Local Development (.env.monetization) │
│ - Only on developer PC                          │
│ - Git-ignored (never committed)                 │
│ - TEST keys only                                │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: GitHub Actions (Encrypted Secrets)    │
│ - AES-256 encryption at rest                    │
│ - Decrypted only during workflow execution      │
│ - LIVE keys for production deployment           │
│ - Masked in logs automatically                  │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: Production Environment                │
│ - Environment variables injected at runtime     │
│ - Never stored in code or configuration files   │
│ - Rotated on schedule (90 days)                 │
│ - Audit logged for compliance                   │
└─────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST: BEFORE FIRST DEPLOYMENT

### **Local Setup**
- [ ] Copy `.env.monetization.local` to `.env.monetization`
- [ ] Fill in TEST keys only (pk_test_*, sk_test_*)
- [ ] Verify `.env.monetization*` in .gitignore
- [ ] Never open `.env.monetization` in terminal (cat/type commands log history)
- [ ] Use IDE with secret masking enabled
- [ ] Test locally: `python -c "from services.api_monetization import *"`

### **Git Safety**
- [ ] Verify `.env.monetization` not staged: `git status`
- [ ] Configure git hooks to prevent secrets:
  ```bash
  pip install detect-secrets
  detect-secrets scan > .secrets.baseline
  git add .secrets.baseline
  ```

### **GitHub Repository**
- [ ] Enable branch protection on main branch
- [ ] Require code review before merge (2 reviewers)
- [ ] Require passing CI/CD checks
- [ ] Enable secret scanning: Settings → Security → Secret scanning
- [ ] Set up security alerts via email

### **GitHub Secrets**
- [ ] All secrets from Step 3 added
- [ ] Verified in Actions tab: `gh secret list`
- [ ] Test workflow runs successfully
- [ ] Verify `.env.monetization` created in CI/CD environment

### **Production Environment**
- [ ] Env vars injected via container secrets manager
- [ ] NO secrets in Docker images or Compose files
- [ ] Audit logging enabled for all API access
- [ ] Monitoring alerts for suspicious activity

---

## 🛡️ KEY PROTECTION STRATEGIES

### **1. Environment Separation**

```bash
# DEVELOPMENT (Local):
# - Use TEST keys (pk_test_*, sk_test_*)
# - Cannot process real payments
# - Safe for experimentation

# STAGING (Pre-production):
# - Use TEST keys from staging Stripe account
# - Mirrors production infrastructure
# - Used for integration testing

# PRODUCTION (Live):
# - Use LIVE keys (pk_live_*, sk_live_*)
# - Real payments processed
# - Maximum security measures
# - Separate credentials from dev/staging
```

### **2. Least Privilege Access**

```yaml
# GitHub Action: Only grant required secrets
jobs:
  deploy:
    steps:
      - name: Deploy with minimal secrets
        env:
          # Only what this job needs:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: ./deploy.sh
        
      # Other jobs get different secrets:
      # - Analytics job: only MIXPANEL_TOKEN + GA keys
      # - Content job: only TIKTOK + YOUTUBE tokens
```

### **3. Secret Rotation Calendar**

```
QUARTERLY (90 days):
├── Stripe API Keys
├── Database Passwords  
├── AWS Access Keys
└── Redis Auth Tokens

ANNUALLY:
├── TikTok Tokens
├── YouTube API Keys
├── LinkedIn Credentials
└── SendGrid API Key

ON-DEMAND:
├── Employee termination
├── Security incident
├── Suspected compromise
└── Client request
```

### **4. Monitoring & Alerting**

```python
# Log all secret access
import logging
import time

logger = logging.getLogger('security')

def log_secret_access(service: str, action: str):
    """Track who accessed what secret and when"""
    logger.warning(f"[SECURITY] {service}:{action} accessed at {time.time()}")
    # Alert if:
    # - After hours
    # - Multiple failed attempts
    # - Unusual location
    # - Different user than normal
```

---

## 🚨 INCIDENT RESPONSE

### **If YOU Accidentally Expose a Secret:**

```bash
# 1. IMMEDIATELY stop what you're doing
# 2. Get the secret hash from git history:
git log --all -S "pk_test_" --pretty=format:"%H %s" | head -5

# 3. Find the commit:
git show <commit-hash>

# 4. Verify the secret is exposed:
grep -r "pk_test_" .

# 5. Report to security team IMMEDIATELY
# 6. DO NOT just commit & push the fix (log history still has it)

# 7. Revoke the key in service (Stripe, TikTok, YouTube dashboard)
# 8. Generate new key
# 9. Update GitHub Secret
# 10. Purge git history (requires admin):
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env*' \
  --prune-empty

# 11. Force push (dangerous - notify team):
git push origin main --force-with-lease

# 12. Audit service logs for unauthorized access
```

### **If Someone ELSE Discovers a Secret:**

```
Thank them publicly
↓
Verify the exposure method
↓
Follow steps 5-12 above
↓
Review security log for access
↓
Implement additional controls
↓
Update this security guide with lessons learned
```

---

## 🔍 VERIFICATION COMMANDS

### **Check Local Safety**

```bash
# Ensure secrets not in git history
git log --all -S "sk_test_" --pretty=format:"%H" 
# Should return nothing if properly set up

# Check all .env files ignored
cat .gitignore | grep env
# Should show: .env, .env.*, .env.monetization

# Verify current working directory is clean
git status
# Should NOT show .env.monetization as modified/staged
```

### **Check GitHub Secrets**

```bash
# List secrets (names only)
gh secret list --repo=Web8kameleon-hub/clisonix.com

# Verify workflow uses secrets correctly
gh workflow view deploy.yml --repo=Web8kameleon-hub/clisonix.com

# Check workflow runs
gh run list --repo=Web8kameleon-hub/clisonix.com --status=completed --limit=5
```

### **Check Production**

```bash
# Verify no secrets in Docker image
docker inspect clisonix-monetization | grep -i "env"
# Should NOT show any credentials

# Check pod environment (K8s)
kubectl describe pod <pod-name> -n clisonix
# Env vars should be loaded from secrets, not inline

# Audit access logs
tail -f /var/log/clisonix/security.log | grep -i "secret"
```

---

## 📋 COMPLIANCE & AUDITING

### **SOC 2 / ISO 27001 Requirements**

```
✅ Access Control
   - Principle of least privilege enforced
   - Role-based access control (RBAC)
   - Multi-factor authentication for GitHub

✅ Encryption
   - Secrets encrypted at rest (GitHub AES-256)
   - TLS 1.2+ for all API communication
   - Database encryption enabled

✅ Monitoring & Logging
   - All secret access logged with timestamp
   - Failed access attempts tracked
   - Regular audit reports generated

✅ Incident Response
   - Response plan documented above
   - Testing quarterly
   - Communication protocol defined

✅ Data Retention
   - Logs kept for 90 days minimum
   - Audit trail preserved
   - Backups retained securely
```

### **PCI DSS (if storing payment data)**

```
✅ No plaintext storage of payment data
✅ Tokenization used for card storage
✅ Stripe handles PCI compliance
✅ NO manual credit card processing
✅ Quarterly security assessment
```

---

## 🔐 SECRET MASKING IN LOGS

### **GitHub Actions automatically masks secrets**

```
$ echo "Secret is ${{ secrets.STRIPE_SECRET_KEY }}"

# Output shows:
Secret is ***

# But logs will contain masked values:
[DEBUG] Connecting to Stripe with key *** ✓
```

### **Manual masking in Python**

```python
import os
import re

def mask_secrets(text):
    """Mask secrets in logs"""
    secrets = [
        os.getenv('STRIPE_SECRET_KEY', ''),
        os.getenv('DATABASE_URL', ''),
    ]
    
    result = text
    for secret in secrets:
        if secret:
            # Replace with ***: or first 4 + **** + last 4
            prefix = secret[:4] if len(secret) > 8 else ''
            suffix = secret[-4:] if len(secret) > 8 else ""
            masked = f"{prefix}****{suffix}"
            result = result.replace(secret, masked)
    
    return result

# Usage:
logger.info(mask_secrets(f"Connected to {db_url}"))
```

---

## 📞 EMERGENCY CONTACTS

| Role | Contact | On-Call |
|------|---------|---------|
| Security Lead | clisonix@pm.me | 24/7 |
| DevOps | clisonix@pm.me | 24/7 |
| Database Admin | clisonix@pm.me | Business hours |

**Security Incident Hotline:** +1-XXX-XXX-XXXX  
**Breach Notification:** clisonix@pm.me

---

## ✅ ACKNOWLEDGMENT

```
By deploying to Clisonix, you acknowledge:
✓ You have read and understand this security guide
✓ You will follow all policies exactly
✓ You report any suspected breaches immediately
✓ You rotate credentials on schedule
✓ You never commit secrets to any repository
```

---

**Security Status: IMPLEMENTED** ✅  
**Last Review: March 12, 2026**  
**Next Review: June 12, 2026**

**Questions? Ask in #security Slack channel or email clisonix@pm.me**

