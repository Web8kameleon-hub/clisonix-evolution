# CLISONIX MONETIZATION SETUP GUIDE
## March 2026 - Revenue Activation Checklist

---

## ✅ PHASE 1: API MONETIZATION (Week 1)

### Step 1.1: Stripe Setup (15 min)
```bash
# 1. Go to https://stripe.com/onboard
# 2. Create business account (Ledjan Ahmati)
# 3. Get API keys from https://dashboard.stripe.com/apikeys
# 4. Copy to .env.monetization:
#    - STRIPE_PUBLIC_KEY (starts with pk_live_)
#    - STRIPE_SECRET_KEY (starts with sk_live_)

# 5. Test keys first (sandbox):
STRIPE_PUBLIC_KEY=pk_test_xxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxx

# 6. Go live when ready
STRIPE_WEBHOOK_SECRET=whsec_xxxxxx  # From Webhooks page
```

### Step 1.2: Deploy API Monetization
```bash
cd /path/to/clisonix-cloud

# Install Stripe SDK
pip install stripe stripe-cli

# Add endpoints to FastAPI main app
# Location: backend/main.py or backend/api/monetization.py
# Import: from services.api_monetization import router as monetization_router
# app.include_router(monetization_router)

# Test locally
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe

# Deploy to production
git add services/api_monetization.py
git commit -m "🚀 Add API monetization with Stripe integration"
git push origin main
```

### Step 1.3: Create /pricing Page
```bash
# Already created at: apps/web/app/pricing/page.tsx
# Deploy: 
cd apps/web
npm run build
npm run start
# Visit: https://clisonix.com/pricing
```

### Step 1.4: Generate API Keys for Beta Users
```bash
curl -X POST https://clisonix.com/api/v1/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "email": "dev@example.com",
    "plan": "pro"
  }'

# Response:
# {
#   "api_key": "csx_abcd1234efgh5678ijkl9012",
#   "subscription_id": "sub_1234567890",
#   "plan": "pro",
#   "requests_per_day": 10000
# }
```

**Expected Revenue Phase 1: $200-500/month**

---

## ✅ PHASE 2: CONTENT AUTOMATION (Week 1-2)

### Step 2.1: TikTok Setup
```bash
# 1. Go to https://developer.tiktok.com/
# 2. Create app: "Clisonix Content Automation"
# 3. Get credentials:
#    - Client ID
#    - Client Secret
#    - Access Token (from auth flow)

# 4. Add to .env.monetization:
TIKTOK_CLIENT_ID=xxxxx
TIKTOK_CLIENT_SECRET=xxxxx
TIKTOK_ACCESS_TOKEN=xxxxx
TIKTOK_BUSINESS_ACCOUNT_ID=xxxxx

# 5. Test connection
python -c "
from services.content_automation import ContentAutomationManager
manager = ContentAutomationManager()
scripts = manager.get_total_scripts()
print(f'Loaded {scripts} video scripts')
"
```

### Step 2.2: YouTube Setup
```bash
# 1. Go to https://console.cloud.google.com/
# 2. Create new project: "Clisonix Videos"
# 3. Enable YouTube Data API v3
# 4. Create OAuth 2.0 credentials (Desktop app)
# 5. Get credentials:
#    - Client ID
#    - Client Secret

# 6. Add to .env.monetization:
YOUTUBE_API_KEY=AIzaSyD...
YOUTUBE_CLIENT_ID=xxxxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=xxxxx
YOUTUBE_CHANNEL_ID=UCxxxxx
YOUTUBE_ACCESS_TOKEN=ya29...

# 7. Authenticate
python -c "
from services.content_automation import ContentAutomationManager
manager = ContentAutomationManager()
calendar = manager.get_posting_calendar(weeks=4)
print(f'Generated {len(calendar)} posts for next 4 weeks')
"
```

### Step 2.3: Generate Content Calendar
```bash
# Get 4-week posting schedule
curl https://clisonix.com/api/v1/content/calendar?weeks=4

# Example output:
# {
#   "weeks": 4,
#   "schedule": [
#     {
#       "platforms": ["tiktok", "youtube-shorts"],
#       "scheduled_time": "2026-03-16T09:00:00",
#       "script": "How AI Reads Your Brain..."
#     },
#     ...
#   ]
# }
```

### Step 2.4: Video Production Setup
```bash
# Option A: Auto-generate videos using Synthesia/D-ID
pip install synthesia-sdk

# Option B: Use video producer (already available)
python services/content_automation.py --generate-videos

# Option C: Manual YouTube Studio
# 1. Go to https://studio.youtube.com/
# 2. Upload Shorts (< 60 sec videos)
# 3. Add tags: #AI #HealthTech #BrainComputer
```

**Expected Revenue Phase 2: $100-400/month TikTok + $500-1500/month YouTube**

---

## ✅ PHASE 3: BLOG MONETIZATION (Week 2)

### Step 3.1: Google AdSense Setup
```bash
# 1. Go to https://adsense.google.com/
# 2. Sign up with Clisonix domain
# 3. Add to .env.monetization:
GOOGLE_ADSENSE_PUBLISHER_ID=ca-pub-xxxxxxxxxxxxxxxx

# 4. Add AdSense code to blog header
# Location: apps/web/app/layout.tsx or index.html.bak

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-xxxxxxxxxxxxxxxx"
  crossorigin="anonymous"></script>
```

### Step 3.2: Affiliate Programs
```bash
# 1. Sign up for:
#    - Amazon Associates (link to EEG devices)
#    - OpenAI Affiliate (link to API docs)
#    - HuggingFace (link to models)
#    - Stripe (link to payments)

# 2. Add affiliate links to blog articles
# 3. Add to .env.monetization:
BLOG_AFFILIATE_PROGRAMS=openai,huggingface,stripe,amazon

# 4. Track clicks/conversions
# Location: apps/web/components/AffiliateLink.tsx
```

**Expected Revenue Phase 3: $50-150/month AdSense + $100-500/month Affiliates**

---

## ✅ PHASE 4: ANALYTICS & TRACKING (Week 2-3)

### Step 4.1: Setup Google Analytics
```bash
# 1. Go to https://analytics.google.com/
# 2. Create property: "Clisonix Monetization"
# 3. Get Measurement ID: G-XXXXXXXXXX
# 4. Add to .env.monetization:
GA_PROPERTY_ID=G-XXXXXXXXXX

# 5. Add to blog header
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Step 4.2: Setup Mixpanel (Event Tracking)
```bash
# 1. Go to https://mixpanel.com/
# 2. Create project: "Clisonix Revenue"
# 3. Get Write Key
# 4. Add to .env.monetization:
MIXPANEL_TOKEN=xxxxxxxxxxxxxxxxxxxxx

# 5. Track key events:
#    - API_KEY_CREATED
#    - API_REQUEST_MADE
#    - SUBSCRIPTION_STARTED
#    - VIDEO_VIEWED
#    - AFFILIATE_CLICKED
```

### Step 4.3: Revenue Dashboard
```bash
# Create tracking endpoint
curl https://clisonix.com/api/v1/monetization/dashboard

# Response includes:
# {
#   "api_revenue": {
#     "total": "$2,340",
#     "subscriptions": 45,
#     "plan_breakdown": {
#       "free": 1200,
#       "pro": 45,
#       "enterprise": 0
#     }
#   },
#   "content_revenue": {
#     "tiktok_views": 285000,
#     "youtube_views": 95000,
#     "estimated_earnings": "$1,200"
#   },
#   "blog_revenue": {
#     "adsense": "$67",
#     "affiliates": "$234"
#   },
#   "total_monthly": "$3,841"
# }
```

---

## ✅ PHASE 5: DEPLOYMENT & AUTOMATION (Week 3)

### Step 5.1: Docker Deployment
```bash
# Create Monetization Service Dockerfile
cat > Dockerfile.monetization << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY services/ ./services/
COPY backend/ ./backend/

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build & run
docker build -f Dockerfile.monetization -t clisonix-monetization .
docker run -d \
  --env-file .env.monetization \
  --name clisonix-monetization \
  clisonix-monetization
```

### Step 5.2: GitHub Actions CI/CD
```yaml
# .github/workflows/monetization-deploy.yml
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
      - uses: actions/checkout@v2
      
      - name: Deploy to production
        env:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
          TIKTOK_ACCESS_TOKEN: ${{ secrets.TIKTOK_ACCESS_TOKEN }}
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        run: |
          docker build -f Dockerfile.monetization -t clisonix-monetization .
          docker push clisonix-monetization:latest
          # Deploy to production cluster
```

### Step 5.3: Scheduled Content Posts
```bash
# Add to crontab or use Celery
# Post videos every 48 hours

# Using APScheduler:
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=content_manager.schedule_tiktok_post,
    trigger="cron",
    day_of_week="0,2,4",  # Mon, Wed, Fri
    hour=9,
    minute=0
)
scheduler.start()
```

---

## 📊 REVENUE PROJECTIONS

### Month 1 (March 2026)
- API (Free users testing): $200-300
- TikTok (ramp up): $100-200
- Blog AdSense: $30-50
- **Total: $330-550**

### Month 2 (April 2026)
- API (Some converting to Pro): $500-800
- TikTok (50k+ views): $200-400
- YouTube Shorts: $300-500
- Blog: $50-100
- **Total: $1,050-1,800**

### Month 3-6 (May-August 2026)
- API: $1,000-2,000/month (scaling)
- TikTok/YouTube: $1,000-3,000/month (viral potential)
- Blog/Affiliates: $200-500/month
- Brand Deals: $500-2,000/month
- **Total: $2,700-7,500/month**

---

## 🚀 QUICK START (TL;DR)

```bash
# 1. Copy environment template
cp .env.monetization.template .env.monetization

# 2. Fill in your keys from Stripe, TikTok, YouTube
# nano .env.monetization

# 3. Deploy API monetization
git add services/
git commit -m "🚀 Activate monetization: API + content + analytics"
git push origin main

# 4. Check revenue dashboard
curl https://clisonix.com/api/v1/monetization/dashboard

# 5. Start posting videos!
python scripts/auto_post_videos.py
```

---

## 📞 SUPPORT

- Stripe Support: https://support.stripe.com/
- TikTok Developers: https://developer.tiktok.com/
- YouTube Support: https://www.youtube.com/watch?v=help
- Revenue Tracking: Check dashboard at https://clisonix.com/monetization

**Status: READY FOR ACTIVATION** ✅
