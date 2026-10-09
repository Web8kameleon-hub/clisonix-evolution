# 🔒 Clisonix Security & Repository Architecture Plan

**Status:** Proposal  
**Date:** March 27, 2026  
**Priority:** 🔴 CRITICAL

---

## Executive Summary

Current risk: **Everyone with repo access sees all backend IP, API keys, service configs, and client data models.**

The codebase is currently a **single monolithic repository** with mixed access - anyone cloned can see secrets, service configurations, and client-specific logic. This violates security best practices for:
- SaaS applications
- Multi-tenant systems
- Client deliverables
- Regulatory compliance (GDPR, financial service regulations)

### Recommendation: **Hybrid Multi-Repo Architecture (Option 3)**

---

## Current State Analysis

### 📊 What's Currently Exposed

| Data Type | Where | Risk Level |
|-----------|-------|-----------|
| Database credentials | `apps/api/main.py`, `.env` files | 🔴 CRITICAL |
| Payment API keys | Stripe/SEPA configs | 🔴 CRITICAL |
| Client source code | `apps/web`, `/ocean-core` | 🟠 HIGH |
| Endpoint configs | docker-compose.yml, service files | 🟠 HIGH |
| Internal architecture | README, architecture docs | 🟡 MEDIUM |

### 👥 Current Access Model

```
Git Repo (Public/Shared)
├── Anyone with GitHub account
├── Full clone = Full visibility
├── No branch protection on sensitive changes
└── Monolithic = Can't separate permissions
```

### ⚠️ Key Problems

1. **Single Point of Failure**: One compromised account = full system exposure
2. **No Client Separation**: Clients could see each other's configurations
3. **Compliance Gap**: Violates data isolation requirements
4. **Hard to Onboard**: New devs/contractors see 100% of codebase
5. **Difficult Deployment**: Can't easily track which code went where

---

## Proposed Architecture: Hybrid Multi-Repo (Option 3)

### 📚 Repository Structure

```
clisonix-ecosystem
├── ✅ clisonix-sdk (PUBLIC SDK Repo)
│   ├── sdk/python/
│   ├── sdk/typescript/
│   ├── docs/api-reference/
│   └── examples/integrations/
│
├── 🔐 clisonix-cloud (PRIVATE Services Repo)
│   ├── ocean-core/
│   ├── alba/
│   ├── albi/
│   ├── apps/api/
│   ├── docker-compose.yml
│   ├── .env (secrets)
│   └── All internal services
│
├── 🔐 clisonix-internal (PRIVATE Tools Repo - DevOps Only)
│   ├── infrastructure/
│   ├── kubernetes/
│   ├── monitoring/
│   ├── backup scripts/
│   └── Deployment pipelines
│
└── 📖 clisonix-docs (PUBLIC/PRIVATE hybrid)
    ├── User Documentation (PUBLIC)
    ├── API Guides (PUBLIC)
    ├── Architecture (PRIVATE - internal only)
    └── Security Policies (PRIVATE)
```

### 🔑 Access Control Model

| Repository | Access Level | Who | Purpose |
|------------|--------------|-----|---------|
| **clisonix-sdk** | Public | Everyone | Use our APIs |
| **clisonix-cloud** | Private | Core Dev Team | Build & deploy services |
| **clisonix-internal** | Private | DevOps/SRE Only | Infrastructure & secrets |
| **clisonix-docs** (public branch) | Public | Everyone | Read API docs |
| **clisonix-docs** (private branch) | Private | Team Leads | Architecture decisions |

### 🛡️ GitHub RBAC Setup

```yaml
Organization: Web8kameleon-hub

Teams:
  ┌─ Core Development (clisonix-cloud)
  │  ├── Push access to main (protected)
  │  ├── Create release branches
  │  ├── Access to Docker secrets
  │  └── Members: 3-5 senior devs
  │
  ├─ DevOps/SRE (clisonix-internal)
  │  ├── Admin access to infrastructure
  │  ├── Access to AWS/Azure secrets
  │  ├── Can trigger CI/CD pipelines
  │  └── Members: 2-3 ops engineers
  │
  ├─ Frontend Team (clisonix-cloud + clisonix-sdk)
  │  ├── Write + Push to apps/web branches
  │  ├── Read-only for backend services
  │  └── Members: Frontend devs
  │
  ├─ Contractors/Agencies (clisonix-sdk ONLY)
  │  ├── Read-only on SDK
  │  ├── NO access to cloud/internal
  │  └── Can propose examples
  │
  └─ Client Support (clisonix-docs PUBLIC branch)
     ├── Read-only documentation
     └── Can create support tickets
```

---

## Implementation Phase 1: Immediate Actions (Week 1)

### 1. Create Private Cloud Repo 🔐

```bash
# Clone and restructure
git clone https://github.com/Web8kameleon-hub/clisonix.com clisonix-cloud-private
cd clisonix-cloud-private

# Keep only backend-related directories
keep: ocean-core, alba, albi, apps/api, docker-compose.yml, .env, .github, requirements/
remove: apps/web (move to separate repo), docs/public

# Push to new private repo
git remote set-url origin https://github.com/Web8kameleon-hub/clisonix-cloud
git push -u origin main
```

**Time:** 1-2 hours  
**Who:** CTO + 1 Senior Dev

### 2. Extract SDK to Public Repo ✅

```bash
# Create public SDK repo
git init ../clisonix-sdk
cd ../clisonix-sdk

# Copy SDK files preserving git history (subtree)
git subtree add --prefix sdk/python ../../clisonix-cloud main:sdk/python
git subtree add --prefix sdk/typescript ../../clisonix-cloud main:sdk/typescript

# Add README, examples, CI/CD for SDK
# Push to public GitHub
```

**Time:** 30-45 min  
**Who:** 1 Dev

### 3. Move Frontend to Separate Repo (Optional)

If clients need custom UI access:
```bash
# Create clisonix-web (can be private or public per client)
git init ../clisonix-web
git subtree add --prefix . ../../clisonix-cloud main:apps/web
```

**Time:** 30 min  
**Who:** 1 Frontend Dev

### 4. Set Up GitHub Teams & RBAC

Go to: `github.com/settings/organizations/Web8kameleon-hub`

```
Teams → Create New Team
├── Core Cloud Developers
│   ├── Members: yourself, 2-3 core devs
│   ├── Permissions: Write on clisonix-cloud
│   └── No access: clisonix-internal
│
├── DevOps/Infrastructure
│   ├── Members: SRE/DevOps person
│   ├── Permissions: Admin on clisonix-internal
│   └── Push access clisonix-cloud (for deployment)
│
├── Contractors
│   ├── Members: External developers
│   ├── Permissions: Read-only on clisonix-sdk
│   └── 0 access: All private repos
│
└── Client Support
    ├── Members: Support team
    ├── Permissions: Read-only on clisonix-docs (public branch)
    └── 0 access: Code repos
```

**Time:** 30 min  
**Who:** Repo admin

---

## Implementation Phase 2: Secrets Management (Week 2)

### 🔑 Migrate Secrets from `.env` Files

#### Before (❌ Insecure)
```bash
# .env in repo
DATABASE_URL=postgresql://user:pass@prod.db.com
STRIPE_SECRET_KEY=sk_live_...
AWS_ACCESS_KEY=AKIA...
```

#### After (✅ Secure)

**Option A: GitHub Secrets (Simple)**
```yaml
# .github/workflows/deploy.yml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL_PROD }}
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
  AWS_CONFIG: ${{ secrets.AWS_CONFIG_JSON }}
```

Go to: `Settings → Secrets and Variables → Actions`

**Option B: HashiCorp Vault (Advanced)**
```yaml
# For production deployments
- name: Get Secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.clisonix.cloud
    token: ${{ secrets.VAULT_TOKEN }}
    secrets: |
      secret/database URL | DATABASE_URL
      secret/stripe key | STRIPE_SECRET_KEY
```

**Option C: AWS Secrets Manager (If using AWS)**
```python
# ocean-core/config.py
import boto3
secretsmanager = boto3.client('secretsmanager')
db_secret = secretsmanager.get_secret_value(SecretId='clisonix/db')
```

**Recommendation for Clisonix:** Use **GitHub Secrets** (free) + **Vault** (production)

---

## Implementation Phase 3: Branch Protection & CI/CD (Week 3)

### 📋 Branch Protection Rules

**For `clisonix-cloud` (Private)**

```
Repository Settings → Branches → add rule for "main"

✅ Require pull request reviews: 2 approvals
✅ Require approval from code owners
✅ Require branches to be up to date before merging
✅ Include admins in restrictions
✅ Require status checks (lint, test, build)
✅ Restrict who can push: Only DevOps team
```

**For `clisonix-sdk` (Public)**
```
✅ Require pull request reviews: 1 approval
✅ Require status checks: Tests + linting
⚠️ Allow force pushes: NO
⚠️ Allow deletions: NO
✅ Auto-delete head branches
```

### 🔄 CI/CD Updates

**clisonix-cloud/`.github/workflows/deploy.yml`**
```yaml
name: Deploy Private Services

on:
  push:
    branches: [main]

jobs:
  test-build-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For OIDC
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Lint & Test
        run: |
          docker-compose build --no-cache ocean-core alba albi
          docker run clisonix-ocean-core pytest ocean-core/tests/
      
      - name: Deploy to Hetzner (Secrets)
        env:
          SSH_KEY: ${{ secrets.HETZNER_SSH_KEY }}
          DOCKER_REGISTRY_PASSWORD: ${{ secrets.DOCKER_REGISTRY_PASSWORD }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_KEY" > ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa
          ssh -o StrictHostKeyChecking=no root@hetzner-new \
            "cd /root/Clisonix-cloud && git pull && docker compose up -d --build"
```

**clisonix-sdk/`.github/workflows/release.yml`**
```yaml
name: Release SDK to PyPI/NPM

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Publish Python SDK
        run: |
          pip install twine
          cd sdk/python
          python setup.py sdist bdist_wheel
          twine upload -u __token__ -p ${{ secrets.PYPI_TOKEN }} dist/*
      
      - name: Publish TypeScript SDK
        run: |
          cd sdk/typescript
          npm ci
          npm run build
          npm publish --access public
```

---

## Complete Transition Timeline

| Phase | Duration | Actions | Team | Risk |
|-------|----------|---------|------|------|
| **Phase 0** | Ready | Backup current repo, get approvals | CTO | LOW |
| **Phase 1** | Week 1 | Create private cloud repo, extract SDKs, setup RBAC | 2 devs | MEDIUM |
| **Phase 2** | Week 2 | Migrate secrets to GitHub/Vault, remove from code | 1 infra | MEDIUM |
| **Phase 3** | Week 3 | Add branch protection, update CI/CD, enforce policies | 1-2 devs | LOW |
| **Phase 4** | Ongoing | Audit access, monitor deployments, train team | DevOps | LOW |

---

## Quick Reference: Security Checklist

### Before Going Live

- [ ] Remove all `.env` files from git history
  ```bash
  git filter-branch --tree-filter 'rm -f .env .env.production' -- --all
  ```

- [ ] Add `.env` to `.gitignore`
  ```
  *.env
  .env*
  secrets/
  !.env.example
  ```

- [ ] Create `.env.example` with dummy values
  ```
  DATABASE_URL=postgresql://user:password@localhost/clisonix
  STRIPE_SECRET_KEY=sk_test_...
  ```

- [ ] Rotate all exposed credentials immediately
  - [ ] Database passwords
  - [ ] API keys (Stripe, PayPal, SEPA)
  - [ ] SSH keys
  - [ ] AWS credentials

- [ ] Enable 2FA on GitHub accounts
- [ ] Add branch protection rules
- [ ] Set up secret scanning

### Ongoing

- [ ] Weekly audit of who has access
- [ ] Monitor for accidental commits (branch hooks)
- [ ] Monthly review of secrets expiration
- [ ] Quarterly penetration testing

---

## FAQ

**Q: Won't separating repos add complexity?**  
A: Yes, but it's better than the complexity of discovering a security breach

. Clear module boundaries = easier to maintain anyway.

**Q: Can clients clone the public SDK repo?**  
A: Yes! That's the whole point. They build integrations with your public API, not your internals.

**Q: What about clients who need custom backend?**  
A: They can't fork private cloud repo. Instead:
- You grant them **read-only access** to specific files via GitHub gists or S3
- You deploy their custom code on your infrastructure
- They never see production credentials

**Q: Does this slow down development?**  
A: No. You'll merge faster because:
- Code reviews are focused (one repo per feature)
- CI/CD is faster (smaller repos)
- Credentials aren't blocking developers

**Q: What if I need to share code between SDK and Cloud?**  
A: Use git subtree or create a private `clisonix-shared` repo:
```bash
git subtree add --prefix shared path/to/clisonix-shared main
```

---

## Estimated Costs

| Item | Cost | Notes |
|------|------|-------|
| GitHub Team Seats | $21/user/month | Already have this |
| GitHub Secrets | Free | Built into GitHub |
| HashiCorp Vault (optional) | $40/month OSS | For production-grade secrets |
| SSL Certificates | Free | Let's Encrypt |
| **Total** | **~$100/month** | More than offset by security |

---

## Next Steps

1. **Review this plan** with team & stakeholders (tomorrow)
2. **Get approval** from CTO/Security (Friday)
3. **Create Phase 1 timeline** (next Monday)
4. **Start repo restructuring** (Week of April 1)
5. **Complete by May 1** for compliance review

---

## Questions?

- 🔐 **Security Questions?** Ask clisonix@pm.me
- 🏗️ **Architecture Questions?** Ask clisonix@pm.me
- 👥 **Team Access?** Ask clisonix@pm.me

---

**Document Status:** DRAFT - Ready for Discussion  
**Last Updated:** March 27, 2026  
**Next Review:** After team feedback (April 2, 2026)

