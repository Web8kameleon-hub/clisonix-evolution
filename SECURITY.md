# 🔐 Clisonix Cloud Security Policy

**Document Version:** 1.0  
**Last Updated:** December 18, 2025  
**Status:** Enterprise Production Standard  
**Classification:** Internal - Security Policy

---

## 📋 Table of Contents

1. [Deklarim & Dokumentim](#deklarim--dokumentim-formal-specification)
2. [Menaxhim i Sekreteve](#menaxhim-i-sekreteve-secret-management)
3. [Validim Automatik](#validim-automatik-automated-validation)
4. [Audit & Rotacion](#audit--rotacion-audit--rotation)
5. [Segregim i Mjediseve](#segregim-i-mjediseve-environment-segregation)
6. [Compliance & Best Practices](#compliance--best-practices)

---

## 🎯 Security Goals

- **Supply Chain Integrity**: Every build is signed, versioned, and traceable
- **Zero-Trust Architecture**: Least privilege for all components
- **Secret Hygiene**: No plaintext credentials in code, logs, or configuration
- **Auditability**: Complete audit trail for compliance (ISO 27001, OWASP)
- **Automation First**: Security gates in CI/CD, not manual reviews
- **Rapid Response**: Secrets rotated within 24h of exposure

---

## Deklarim & Dokumentim (Formal Specification)

### Purpose
All environment variables must be formally declared, documented, and tracked.

### Requirements

#### 1. `.env.example` Template (Source of Truth)
Every environment variable used in production **MUST** be declared in `.env.example`:

```bash
# ===============================================
# CLISONIX CLOUD - ENVIRONMENT VARIABLES
# ===============================================
# Production: Copy to .env and fill with real values
# Version: 1.0
# Last Updated: 2025-12-18

# ===== DATABASE =====
DB_HOST=localhost
DB_PORT=5432
DB_USER=clisonix_user
DB_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS_MIN
DB_NAME=clisonix_prod
DB_SSL_MODE=require

# ===== REDIS CACHE =====
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS_MIN
REDIS_DB=0

# ===== JWT & AUTHENTICATION =====
JWT_SECRET=GENERATE_SECURE_JWT_SECRET_64_CHARS_MIN
JWT_EXPIRY=86400  # 24 hours in seconds
JWT_REFRESH_SECRET=GENERATE_SEPARATE_REFRESH_SECRET
JWT_REFRESH_EXPIRY=2592000  # 30 days in seconds

# ===== API KEYS (Third-party services) =====
STRIPE_API_KEY=sk_live_XXXXXXXXXXXXX_PRODUCTION_ONLY
STRIPE_SECRET_KEY=sk_secret_XXXXXXXXXXXXX_PRODUCTION_ONLY
SENDGRID_API_KEY=SG.XXXXXXXXXXXXX_PRODUCTION_ONLY
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXX/YYYY/ZZZZ

# ===== MINIO S3 COMPATIBLE =====
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS_MIN
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=GENERATE_SECURE_PASSWORD_32_CHARS_MIN
MINIO_BUCKET=clisonix-prod
MINIO_REGION=us-east-1

# ===== GRAFANA DASHBOARD =====
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS_MIN
GF_INSTALL_PLUGINS=grafana-piechart-panel

# ===== HETZNER DEPLOYMENT =====
HETZNER_IP=157.90.234.158
HETZNER_SSH_KEY_PATH=/opt/clisonix/.ssh/id_rsa
DEPLOYMENT_ENVIRONMENT=production

# ===== MONITORING & LOGGING =====
PROMETHEUS_RETENTION=30d
LOKI_RETENTION_DAYS=30
LOG_LEVEL=INFO  # DEBUG, INFO, WARN, ERROR
ENABLE_SENTRY=true
SENTRY_DSN=https://xxxxx@xxxx.ingest.sentry.io/xxxxx

# ===== APPLICATION SETTINGS =====
ENVIRONMENT=production
DEBUG=false
PORT=8000
FRONTEND_URL=https://clisonix-cloud.com
BACKEND_URL=https://api.clisonix-cloud.com
CORS_ORIGINS=https://clisonix-cloud.com,https://app.clisonix-cloud.com

# ===== SECURITY HEADERS =====
SECURITY_HEADERS_CSP=default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
SECURITY_HEADERS_HSTS=max-age=31536000; includeSubDomains; preload

# ===== ENCRYPTION KEYS =====
ENCRYPTION_KEY=GENERATE_32_CHAR_HEX_KEY_FOR_DATA_ENCRYPTION
HMAC_KEY=GENERATE_32_CHAR_HEX_KEY_FOR_HMAC_SIGNING
```

#### 2. Variable Classification

| Category | Examples | Rotation | Risk |
|----------|----------|----------|------|
| **Credentials** | DB_PASSWORD, JWT_SECRET, API_KEYS | 90 days | CRITICAL |
| **Connections** | DB_HOST, REDIS_HOST, MINIO_ENDPOINT | On-demand | HIGH |
| **Identifiers** | DB_NAME, MINIO_BUCKET, LOG_LEVEL | Never | LOW |
| **Configuration** | DEBUG, PORT, CORS_ORIGINS | On-demand | LOW |

#### 3. Documentation Rules

- Every variable must have a comment explaining its purpose
- Mandatory variables must be marked with `[REQUIRED]`
- Optional variables marked with `[OPTIONAL]`
- Format restrictions (min length, character set) must be documented
- Examples must use placeholder values, NEVER real credentials

---

## Menaxhim i Sekreteve (Secret Management)

### Principle: Defense in Depth

Secrets never appear in:
- ❌ Source code repositories
- ❌ Docker image layers
- ❌ CI/CD logs
- ❌ Configuration files tracked in git
- ❌ Docker Compose files (if in version control)

### Best Practices

#### 1. GitHub Actions Secrets (CI/CD)
All production secrets stored in GitHub Secrets, referenced as `${{ secrets.SECRET_NAME }}`:

```yaml
- name: Deploy to Production
  env:
    DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
    JWT_SECRET: ${{ secrets.PROD_JWT_SECRET }}
    STRIPE_API_KEY: ${{ secrets.PROD_STRIPE_API_KEY }}
```

**Rules:**
- One secret per GitHub Actions secret (no combined secrets)
- Prefix: `PROD_`, `STAGING_`, `DEV_` by environment
- Never log secret values; only log variable name existence
- Auto-redact in logs: `***[REDACTED]***`

#### 2. Runtime Secret Management (Production)

**Hetzner VPS Deployment:**
```bash
# Generated automatically by deploy-hetzner.sh
/opt/clisonix/.env.production  # Git-ignored, 0600 perms
/opt/clisonix/.credentials.txt # Backup of initial passwords
/opt/clisonix/.ssh/            # SSH keys with 0600 perms
```

**Kubernetes Secret Objects (Future):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: clisonix-prod-secrets
  namespace: production
type: Opaque
data:
  DB_PASSWORD: base64encodedvalue
  JWT_SECRET: base64encodedvalue
---
```

#### 3. Secret Generation (Policy)

All secrets must be generated using cryptographically secure methods:

```bash
# Passwords (32+ chars, mixed case + numbers + symbols)
openssl rand -base64 32

# JWT Secrets (64+ chars)
openssl rand -base64 48

# API Keys (environment-specific format)
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Encryption Keys (hex)
openssl rand -hex 32
```

**Never use:**
- Dictionary words
- Sequential characters (abc123xyz)
- Predictable patterns
- Same secret across environments

#### 4. Secret Access Control

| Secret | Storage | Access | Rotation |
|--------|---------|--------|----------|
| DB_PASSWORD | GitHub Secrets + Vault | CI/CD + Hetzner | 90 days |
| JWT_SECRET | GitHub Secrets + Vault | App + CI/CD | 30 days |
| API Keys (Stripe, etc) | GitHub Secrets + Vault | App + CI/CD | As-needed |
| SSH Keys | Vault + Local (0600) | Deploy Agent | On-breach |

---

## Validim Automatik (Automated Validation)

### CI/CD Security Gates

All security checks run automatically on every `push` and `pull_request`:

#### Gate 1: Secret Detection (Gitleaks + TruffleHog)
```yaml
- Gitleaks scans for 15+ secret patterns (passwords, API keys, tokens)
- TruffleHog checks for high-entropy strings
- Fails fast if secrets detected
- Auto-redacts findings in reports
```

**Result:** ✅ Pass if no secrets found, ❌ Fail if any detected

#### Gate 2: Dependency Vulnerabilities (CodeQL + Trivy)
```yaml
- CodeQL scans Python & JavaScript for code vulnerabilities
- Trivy scans for CRITICAL/HIGH CVEs in dependencies
- Dependency Review fails on new HIGH+ vulnerabilities in PRs
```

**Result:** ✅ Pass if no CRITICAL/HIGH, ⚠️ Warn on MEDIUM

#### Gate 3: Policy Enforcement (OPA/Conftest)
```yaml
- Dockerfile: No root user, pinned base images, no secrets in ENV
- Docker Compose: No privileged mode, no host networking, resource limits
- Kubernetes: Non-root containers, dropped capabilities, resource limits
```

**Result:** ✅ Pass if all policies met, ❌ Fail if violated

#### Gate 4: Container Image Scan (Trivy)
```yaml
- Scans image layers for CRITICAL/HIGH vulnerabilities
- Scans filesystem for exposed secrets, misconfigs
- Generates SBOM (Syft) for supply chain transparency
```

**Result:** ✅ Pass if no CRITICAL, ❌ Fail if found

#### Gate 5: Environment Validation
```yaml
- .gitignore covers .env, .secrets, *.pem, *.key
- .env.example exists (documentation)
- docker-compose.yml uses ${VAR} syntax (not hardcoded)
```

**Result:** ✅ Pass if all checks OK, ⚠️ Warn if manual review needed

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Code Push / PR Created                                  │
└────────────┬────────────────────────────────────────────┘
             │
      ┌──────▼───────────┐
      │ Secret Detection │ ◄─── Gitleaks + TruffleHog
      │ (2 min)          │
      └──────┬───────────┘
             │
      ┌──────▼──────────────────┐
      │ Dependency Analysis     │ ◄─── CodeQL + Dependency Review
      │ (8 min)                 │
      └──────┬──────────────────┘
             │
      ┌──────▼────────────┐
      │ Policy Gates      │ ◄─── OPA/Conftest (Docker, K8s, Compose)
      │ (2 min)           │
      └──────┬────────────┘
             │
      ┌──────▼──────────┐
      │ Build & Scan    │ ◄─── Docker Build + Trivy + Syft
      │ (10 min)        │
      └──────┬──────────┘
             │
      ┌──────▼────────────────┐
      │ Environment Check     │ ◄─── Variable Validation + SBOM
      │ (1 min)               │
      └──────┬────────────────┘
             │
      ┌──────▼────────────────┐
      │ Summary Report        │ ◄─── SARIF + Attestations
      │ (Instant)             │
      └──────┬────────────────┘
             │
         ✅ PASS / ❌ FAIL
```

---

## Audit & Rotacion (Audit & Rotation)

### Secret Rotation Policy

#### Rotation Cadence

| Secret Type | Frequency | Reason | Approval |
|-------------|-----------|--------|----------|
| DB_PASSWORD | 90 days | Standard crypto rotation | Team Lead |
| JWT_SECRET | 30 days | Auth token expiry | Team Lead |
| API Keys | As-needed | Provider policy | Security Officer |
| SSH Keys | 180 days | Access control | DevOps Lead |
| Encryption Keys | 1 year | Regulatory compliance | CISO |

#### Rotation Process

1. **Generate new secret** using approved methods
2. **Test in staging** with new secret for 24h
3. **Schedule production deploy** (low-traffic window)
4. **Deploy with new secret + old as fallback** (15min)
5. **Monitor for errors** (30min post-deployment)
6. **Disable old secret** after monitoring period
7. **Archive** for audit trail

#### Breach Response (Immediate)

If secret suspected compromised:
1. ⚠️ Alert CISO + Security Team
2. 🚨 Revoke secret immediately (GitHub, provider)
3. 🔄 Generate new secret
4. ⏱️ Deploy within 4 hours (or 1 hour for critical)
5. 📋 Log incident with root cause
6. 🔍 Audit all access since compromise time

### Audit Trail Requirements

Every environment variable access must be logged:

```json
{
  "timestamp": "2025-12-18T22:30:15Z",
  "service": "clisonix-api",
  "action": "SECRET_READ",
  "secret_id": "DB_PASSWORD",
  "actor": "deployment-pipeline",
  "source_ip": "157.90.234.158",
  "result": "success",
  "exposure_risk": "none"
}
```

**Monitoring & Alerts:**
- Unauthorized access attempts
- Mass secret reads
- Access from unexpected IPs
- Secret rotation failures

---

## Segregim i Mjediseve (Environment Segregation)

### Three-Tier Environment Strategy

#### 1. Development (`DEV_*` prefix)
- **Location**: Local machine + GitHub Actions runners
- **Data**: Synthetic, non-sensitive
- **Secrets**: GitHub Secrets (auto-rotated)
- **Access**: All team members
- **Compliance**: None required
- **Retention**: 7 days

```bash
# .env (LOCAL - NEVER commit)
DB_PASSWORD=dev_password_123456789
JWT_SECRET=dev_jwt_secret_123456789
STRIPE_API_KEY=sk_test_123456789
```

#### 2. Staging (`STAGING_*` prefix)
- **Location**: Hetzner secondary VPS
- **Data**: Production-like, anonymized
- **Secrets**: GitHub Secrets + Vault
- **Access**: DevOps + Tech Lead
- **Compliance**: ISO 27001 lite
- **Retention**: 30 days

```bash
# .env.staging (Vault-managed)
DB_PASSWORD=${VAULT_PATH}/staging/db_password
JWT_SECRET=${VAULT_PATH}/staging/jwt_secret
STRIPE_API_KEY=sk_test_staging_key
```

#### 3. Production (`PROD_*` prefix)
- **Location**: Hetzner primary VPS (157.90.234.158)
- **Data**: Real customer data
- **Secrets**: GitHub Secrets + Vault + KMS
- **Access**: Deployment pipeline only (no humans)
- **Compliance**: ISO 27001 + GDPR + PCI-DSS
- **Retention**: Forever (audit trail)

```bash
# .env.production (KMS-encrypted)
DB_PASSWORD=${AWS_KMS_DECRYPTED_VALUE}
JWT_SECRET=${AWS_KMS_DECRYPTED_VALUE}
STRIPE_API_KEY=sk_live_production_key
```

### Segregation Rules

1. **No cross-environment secrets**
   - ❌ Don't use PROD secret in DEV
   - ✅ Each environment has unique secrets

2. **No secret reuse**
   - ❌ Don't reuse JWT_SECRET for HMAC
   - ✅ Generate unique secrets per purpose

3. **Environment-specific configuration**
   - ❌ Don't use same docker-compose.yml for all envs
   - ✅ Use environment-specific overrides

4. **Audit trail separation**
   - ❌ Don't mix logs from different environments
   - ✅ Separate log streams with tags

---

## Compliance & Best Practices

### Standards & Frameworks

| Framework | Requirement | Implementation |
|-----------|-------------|-----------------|
| **ISO 27001** | Information Security | Vault, encrypted secrets, audit logs |
| **OWASP Top 10** | Secret Management | No hardcoding, rate limiting, WAF |
| **GDPR** | Personal Data Protection | PII redaction, encryption at rest/transit |
| **PCI-DSS** | Payment Data Security | TLS 1.3, tokenization, secret rotation |
| **SOC 2** | Audit Compliance | Access logs, change tracking, incident response |

### Best Practices Checklist

#### Development Phase
- ✅ Use `.env.example` as template
- ✅ Generate secrets with `openssl rand`
- ✅ Never commit `.env` files
- ✅ Use strong passwords (32+ chars, mixed case)
- ✅ Scan code with Gitleaks before commit

#### Build Phase
- ✅ Run all security gates in CI/CD
- ✅ Fail fast on secret detection
- ✅ Generate SBOM + sign container image
- ✅ Upload SARIF reports to GitHub
- ✅ Generate SLSA provenance

#### Deployment Phase
- ✅ Verify image signature before deployment
- ✅ Verify SBOM matches deployment
- ✅ Rotate old secrets after deploy
- ✅ Enable audit logging in production
- ✅ Set up monitoring + alerting

#### Runtime Phase
- ✅ Monitor secret access patterns
- ✅ Alert on unauthorized reads
- ✅ Log all configuration changes
- ✅ Rotate secrets on schedule (90 days)
- ✅ Respond to breaches within 4 hours

### Technology Stack for Secret Management

**Current:**
- GitHub Actions Secrets (CI/CD)
- `.env` files (local development)
- docker-compose with `${VAR}` syntax

**Recommended (Future):**
- HashiCorp Vault (centralized secret store)
- AWS Secrets Manager (cloud provider integration)
- Sealed Secrets or External Secrets Operator (Kubernetes)
- Cosign + Rekor (container image signing)

### Incident Response Plan

**Scenario 1: Secret Exposed in Git**
1. Find commit hash with `git log -S "secret_value"`
2. Revoke secret immediately
3. Force-push to remove (or BFG tool)
4. Generate new secret
5. Deploy within 1 hour
6. Audit access logs
7. Notify affected users

**Scenario 2: Unauthorized Access**
1. Revoke all related secrets
2. Review access logs (last 7 days)
3. Change all credentials
4. Deploy hardening changes
5. Enable 2FA / MFA
6. Notify security team + users
7. Post-mortem meeting

**Scenario 3: Supply Chain Attack**
1. Isolate affected services
2. Perform deep vulnerability scan
3. Generate new SBOMs for all images
4. Rebuild and redeploy from clean state
5. Verify integrity with Cosign
6. Communicate to customers + vendors

---

## 📊 Metrics & Monitoring

### Security Scorecard

Track these metrics weekly:

```
┌─────────────────────────────────┬────────┐
│ Metric                          │ Target │
├─────────────────────────────────┼────────┤
│ Secrets detected in CI/CD       │ 0      │
│ Vulnerabilities (CRITICAL)      │ 0      │
│ Vulnerabilities (HIGH)          │ < 2    │
│ Policy violations (Conftest)    │ 0      │
│ Secret rotation completion      │ 100%   │
│ Audit log retention (days)      │ 90+    │
│ SBOM coverage                   │ 100%   │
│ Container image signatures      │ 100%   │
│ Incident response time (hours)  │ < 4    │
│ Security training completion    │ 100%   │
└─────────────────────────────────┴────────┘
```

### Dashboard

Integrate with Grafana:
- Secret rotation calendar
- CVE trend analysis
- Policy violation heatmap
- Audit log volume by service
- Incident timeline

---

## ✅ Sign-Off

**Document Owner:** Security Team  
**Last Review Date:** December 18, 2025  
**Next Review Date:** March 18, 2026  
**Approved By:** DevSecOps Lead  

---

## 📞 Support & Questions

- **Security Issues**: security@clisonix-cloud.com
- **Environment Setup**: devops@clisonix-cloud.com
- **Incident Reporting**: incidents@clisonix-cloud.com

---

**Remember:** 🔐 **Security is everyone''s responsibility.**
