# GITHUB SECRETS CONFIGURATION GUIDE
## Secure Credential Management for Production Deployment

**Repository:** Web8kameleon-hub/clisonix.com  
**Purpose:** Store encrypted secrets for GitHub Actions CI/CD  
**Sensitivity:** CRITICAL - Never expose these values

---

## ✅ SETUP INSTRUCTIONS

### **Step 1: Navigate to Repository Settings**

```
1. Go to: https://github.com/Web8kameleon-hub/clisonix.com
2. Click: Settings (gear icon, top right)
3. Left sidebar: Security → Secrets and variables → Actions
4. Button: "New repository secret"
```

### **Step 2: Add Each Secret**

Copy from your `.env.monetization` file and create these secrets:

---

## 📋 REQUIRED SECRETS

### **Stripe Payments**
```
Secret Name: STRIPE_PUBLIC_KEY
Value: pk_live_51234567890abcdef...

Secret Name: STRIPE_SECRET_KEY
Value: sk_live_98765432100fedcba...

Secret Name: STRIPE_WEBHOOK_SECRET
Value: whsec_1234567890abcdef...
```

### **TikTok Content**
```
Secret Name: TIKTOK_CLIENT_ID
Value: xxxxxxxxxxxxx

Secret Name: TIKTOK_CLIENT_SECRET
Value: xxxxxxxxxxxxx

Secret Name: TIKTOK_ACCESS_TOKEN
Value: xxxxxxxxxxxxx

Secret Name: TIKTOK_BUSINESS_ACCOUNT_ID
Value: xxxxxxxxxxxxx
```

### **YouTube**
```
Secret Name: YOUTUBE_API_KEY
Value: AIzaSyD_YOUR_API_KEY_HERE

Secret Name: YOUTUBE_CLIENT_ID
Value: xxxxx.apps.googleusercontent.com

Secret Name: YOUTUBE_CLIENT_SECRET
Value: xxxxxxxxxxxxx

Secret Name: YOUTUBE_CHANNEL_ID
Value: UCxxxxxxxxxxxxx

Secret Name: YOUTUBE_ACCESS_TOKEN
Value: ya29.a0AfH6xxxxxxxxxxxxx
```

### **LinkedIn**
```
Secret Name: LINKEDIN_CLIENT_ID
Value: xxxxxxxxxxxxx

Secret Name: LINKEDIN_CLIENT_SECRET
Value: xxxxxxxxxxxxx

Secret Name: LINKEDIN_ACCESS_TOKEN
Value: xxxxxxxxxxxxx
```

### **Analytics & Tracking**
```
Secret Name: GOOGLE_ADSENSE_PUBLISHER_ID
Value: ca-pub-xxxxxxxxxxxxxxxx

Secret Name: GA_MEASUREMENT_ID
Value: G-XXXXXXXXXX

Secret Name: MIXPANEL_TOKEN
Value: xxxxxxxxxxxxxxxxxxxxx
```

### **Email & Notifications**
```
Secret Name: SENDGRID_API_KEY
Value: SG.1234567890XXXXXXXXXXXX

Secret Name: SENDGRID_FROM_EMAIL
Value: clisonix@pm.me
```

### **Database**
```
Secret Name: DATABASE_URL
Value: postgresql://user:password@hostname:5432/clisonix_monetization

Secret Name: REDIS_URL
Value: redis://hostname:6379
```

### **Cloud Storage**
```
Secret Name: AWS_ACCESS_KEY_ID
Value: AKIAIOSFODNN7EXAMPLE

Secret Name: AWS_SECRET_ACCESS_KEY
Value: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

Secret Name: AWS_REGION
Value: eu-west-1

Secret Name: AWS_S3_BUCKET
Value: clisonix-videos
```

---

## 🔧 USING SECRETS IN GITHUB ACTIONS

### **Example: .github/workflows/deploy.yml**

```yaml
name: Deploy Monetization

on:
  push:
    branches: [main]
    paths:
      - 'services/api_monetization.py'
      - 'services/content_automation.py'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Create .env.monetization
        run: |
          cat > .env.monetization << EOF
          STRIPE_PUBLIC_KEY=${{ secrets.STRIPE_PUBLIC_KEY }}
          STRIPE_SECRET_KEY=${{ secrets.STRIPE_SECRET_KEY }}
          STRIPE_WEBHOOK_SECRET=${{ secrets.STRIPE_WEBHOOK_SECRET }}
          TIKTOK_CLIENT_ID=${{ secrets.TIKTOK_CLIENT_ID }}
          TIKTOK_CLIENT_SECRET=${{ secrets.TIKTOK_CLIENT_SECRET }}
          TIKTOK_ACCESS_TOKEN=${{ secrets.TIKTOK_ACCESS_TOKEN }}
          YOUTUBE_API_KEY=${{ secrets.YOUTUBE_API_KEY }}
          YOUTUBE_ACCESS_TOKEN=${{ secrets.YOUTUBE_ACCESS_TOKEN }}
          DATABASE_URL=${{ secrets.DATABASE_URL }}
          REDIS_URL=${{ secrets.REDIS_URL }}
          EOF
      
      - name: Deploy to production
        env:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
        run: |
          # Your deployment script here
          docker build -f Dockerfile.monetization -t clisonix-monetization .
          docker push clisonix-monetization:latest
```

---

## ⚠️ SECURITY BEST PRACTICES

### **DO:**
- ✅ Use TEST keys for development (`pk_test_*`, `sk_test_*`)
- ✅ Use LIVE keys only in production (`pk_live_*`, `sk_live_*`)
- ✅ Rotate keys every 90 days
- ✅ Use different keys for different environments
- ✅ Monitor for unauthorized access in Stripe dashboard
- ✅ Review GitHub Actions logs for any exposed values (they're masked)
- ✅ Use branch protection rules on main branch

### **DON'T:**
- ❌ Add secrets to `.env` files in git
- ❌ Log secret values in GitHub Actions output
- ❌ Share secrets in Slack, email, or any communication
- ❌ Use the same keys across environments
- ❌ Forget to add `.env.monetization*` to `.gitignore`
- ❌ Commit `poetry.lock` or `package-lock.json` with embedded keys

---

## 🔍 VERIFICATION

### **Check Secrets Are Set**

```bash
# List all secrets (names only, values hidden)
gh secret list --repo=Web8kameleon-hub/clisonix.com

# Output:
# STRIPE_PUBLIC_KEY          Updated 2026-03-12
# STRIPE_SECRET_KEY          Updated 2026-03-12
# TIKTOK_ACCESS_TOKEN        Updated 2026-03-12
# ... etc
```

### **Test Deployment**

```bash
# Push a test commit to trigger CI/CD
git commit --allow-empty -m "test: verify GitHub Secrets"
git push origin main

# Check Actions tab: https://github.com/Web8kameleon-hub/clisonix.com/actions
# Verify .env.monetization was created without errors
```

---

## 📊 SECRET ROTATION SCHEDULE

| Secret | Rotation | Reason |
|--------|----------|--------|
| Stripe API Keys | Quarterly (90 days) | Standard security practice |
| TikTok Access Token | Annually or on revocation | Less frequent change |
| YouTube API Key | Annually | Standard practice |
| Database Password | Quarterly (90 days) | Critical infrastructure |
| AWS Keys | Quarterly (90 days) | Cloud security best practice |

---

## 🆘 EMERGENCY: KEY COMPROMISE

**If a secret is accidentally exposed:**

1. **Immediately revoke the key** in the service dashboard
2. **Generate a new key**
3. **Update GitHub Secret** with new value
4. **Audit** service logs for unauthorized access
5. **Alert** team members
6. **Review** git history for any commits containing secrets (use `git-secrets` tool)

---

## 📞 RESOURCES

- Stripe API Keys: https://dashboard.stripe.com/apikeys
- GitHub Secrets Docs: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- Security Checklist: https://cheatsheetseries.owasp.org/cheatsheets/githubsecrets_cheatsheet.html

---

**Status: READY FOR PRODUCTION** ✅  
**Last Updated:** March 12, 2026

