# 🌟 CLISONIX BLOG PLATFORM - WITH PAYWALL & MONETIZATION

## Executive Summary

A complete blog platform with **user authentication**, **micropayments**, **subscriptions**, and **non-intrusive advertising** to create sustainable revenue streams.

**Revenue Model:**
- 💰 **Micropayments**: €0.10 per article
- 🔄 **Monthly Subscription**: €4.99/month (unlimited access)
- 📅 **Yearly Subscription**: €49/year (unlimited access + ad-free)
- 📢 **Ad Revenue**: Contextual health/wellness ads (only for free tier users)

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (HTML/CSS/JavaScript)                              │
│ - Modern, responsive design                                 │
│ - Article previews with paywall indicators                 │
│ - User authentication with Clerk                           │
│ - Stripe payment integration                               │
│ - Ad display system                                         │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ Blog API Service (FastAPI - Port 8050)                      │
│ ✅ Authentication (/api/v1/auth/*)                         │
│ ✅ Article Management (/api/v1/articles/*)                 │
│ ✅ Payments & Subscriptions (/api/v1/payments/*)            │
│ ✅ Advertisements (/api/v1/ads/*)                          │
│ ✅ Analytics (/api/v1/admin/*)                             │
│ ✅ Stripe Webhooks (payment confirmations)                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────┐
             │                                                 │
             ▼                                                 ▼
    ┌──────────────────┐                           ┌──────────────────┐
    │ Content Sources  │                           │ db: blog_api.db  │
    │                  │                           │ (SQLite/PostgreSQL)
    │ - Dr. Albana     │                           │                  │
    │ - Blerina        │                           │ Tables:          │
    │ - Blerina Ocean  │                           │ - Users          │
    └──────────────────┘                           │ - UserArticleAccess
                                                   │ - Payments       │
                                                   │ - Advertisements │
                                                   └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Environment Variables

Create `.env` file in `services/blog_api/`:

```env
# Portfolio API Service
BLOG_API_PORT=8050

# Clerk Authentication (OAuth2)
CLERK_SECRET_KEY=sk_test_your_clerk_secret_here
CLERK_PUBLISH_KEY=pk_test_your_clerk_publish_key_here

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_here
STRIPE_PUBLISH_KEY=pk_test_your_stripe_publish_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Database
DATABASE_URL=sqlite:////app/blog_api.db
# Or for PostgreSQL: postgresql://user:password@localhost/blog_db

# Content Sources
DR_ALBANA_URL=http://dr_albana:8040
BLERINA_URL=http://blerina:8039
```

### 2. Docker Compose Configuration

Add to `docker-compose.yml`:

```yaml
  blog-api:
    build: ./services/blog_api
    container_name: clisonix-blog-api
    ports:
      - "8050:8050"
    environment:
      - BLOG_API_PORT=8050
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - DATABASE_URL=sqlite:////app/blog_api.db
      - DR_ALBANA_URL=http://dr_albana:8040
      - BLERINA_URL=http://blerina:8039
    volumes:
      - ./blog_api_data:/app
    networks:
      - clisonix
    depends_on:
      - dr_albana
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8050/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Build & Deploy

```bash
# Build image
docker build -t clisonix-blog-api ./services/blog_api

# Run locally
docker run -p 8050:8050 \
  -e STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY \
  -e CLERK_SECRET_KEY=$CLERK_SECRET_KEY \
  clisonix-blog-api

# Or with docker-compose
docker-compose up blog-api
```

---

## 🔐 Authentication Flow

### Using Clerk (OAuth2)

1. **Frontend**: User clicks "Hyr" button
2. **Clerk Widget**: Opens sign-in modal (email/Google/GitHub)
3. **Backend**: Receives JWT token from Clerk
4. **Registration**: Auto-creates user in `users` table + Stripe customer
5. **Session**: Token stored in localStorage

```javascript
// Frontend - Get token after login
const userToken = localStorage.getItem('clerk_token');

// Make authenticated API call
fetch('http://localhost:8050/api/v1/auth/profile', {
    headers: { 'Authorization': `Bearer ${userToken}` }
})
```

---

## 💳 Payment Features

### 1. Micropayment (€0.10 per article)

Users can buy individual articles:

```bash
POST /api/v1/payments/article
{
    "article_id": "article_123",
    "source": "dr_albana"
}

Response:
{
    "client_secret": "pi_1234_secret_...",
    "payment_intent_id": "pi_1234...",
    "amount_cents": 10
}
```

**Flow:**
1. Click article → paywall modal appears
2. User enters card details (Stripe Elements)
3. Payment confirmed → article access granted
4. Recording in `UserArticleAccess` table

### 2. Monthly Subscription (€4.99/month)

Unlimited article access + no ads:

```bash
POST /api/v1/payments/subscribe
{ "tier": "monthly" }
```

**Benefits:**
- ✅ Access to ALL articles
- ✅ No advertisements
- ✅ Email digests
- ✅ Archive access

### 3. Yearly Subscription (€49/year)

Best value with 17% discount:

```bash
POST /api/v1/payments/subscribe
{ "tier": "yearly" }
```

**Benefits:**
- ✅ All monthly benefits
- ✅ Priority support
- ✅ 17% savings vs. monthly
- ✅ Valid for 365 days

### 4. Stripe Webhook Integration

Updates payment status in real-time:

```python
# Webhook endpoint
POST /api/v1/payments/webhook
{
    "type": "payment_intent.succeeded",
    "data": {
        "object": {
            "id": "pi_1234...",
            "status": "succeeded"
        }
    }
}
```

**Actions:**
1. Payment marked as "completed"
2. User granted access to article/subscription
3. `total_spent_cents` incremented
4. Subscription tier updated
5. `subscription_expires` calculated

---

## 📰 Article Management

### List Articles (with previews)

```bash
GET /api/v1/articles?skip=0&limit=12
```

**Response:**
```json
[
    {
        "id": "med_123",
        "title": "Inteligjenca Artificiale në Mjekësi",
        "author": "Dr. Albana",
        "date": "2026-03-12",
        "preview": "Përshkrimi i llojeve të re të teknologjisë AI në diagnostikun mjekësor...",
        "source": "dr_albana",
        "category": "medical",
        "read_time": 8,
        "requires_payment": true
    }
]
```

### Get Full Article (requires access)

```bash
GET /api/v1/articles/{article_id}
Authorization: Bearer {token}
```

**Returns full content** if user:
- Has article-specific purchase, OR
- Has active subscription

---

## 📢 Advertisement System

### Display Ads

```bash
GET /api/v1/ads?limit=3
```

**Rules:**
- Premium users (subscription) see NO ads
- Free users see up to 3 rotating ads
- Only serious health/wellness ads
- No pop-ups or auto-play videos

### Track Ad Clicks

```bash
POST /api/v1/ads/{ad_id}/click
```

**Metrics collected:**
- Impressions (views)
- Clicks (engagement)
- Click-through rate (CTR)

---

## 📊 Revenue Analytics

### Admin Dashboard Endpoint

```bash
GET /api/v1/admin/analytics?admin_token={token}
```

**Returns:**
```json
{
    "total_users": 1250,
    "total_revenue_eur": 845.50,
    "micropayment_transactions": 8450,
    "active_subscribers": 120,
    "monthly_revenue_eur": 599.80,
    "currency": "EUR"
}
```

### Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| MRR (Monthly Recurring Revenue) | Subscriptions × 30 days | €600+ |
| Transaction Volume | Micropayments + Subscriptions | 1000+/month |
| Average Revenue Per User | Total Revenue / Users | €0.50+ |
| Churn Rate | Cancelled Subscriptions / Active | <5% |
| Free to Paid Conversion | Paid Users / Total Users | 15%+ |

---

## 🗄️ Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id VARCHAR PRIMARY KEY,          -- Clerk user ID
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    stripe_customer_id VARCHAR,
    subscription_tier VARCHAR,             -- free, monthly, yearly
    subscription_expires DATETIME,
    total_spent_cents INTEGER,
    total_articles_purchased INTEGER,
    created_at DATETIME,
    updated_at DATETIME,
    is_active BOOLEAN
);
```

### UserArticleAccess Table

```sql
CREATE TABLE user_article_access (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    article_id VARCHAR NOT NULL,           -- Purchased article
    article_title VARCHAR NOT NULL,
    source VARCHAR NOT NULL,               -- dr_albana, blerina
    access_date DATETIME,
    payment_method VARCHAR,                -- micropayment, subscription
    stripe_payment_id VARCHAR
);
```

### Payments Table

```sql
CREATE TABLE payments (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    stripe_payment_id VARCHAR UNIQUE,
    amount_cents INTEGER,
    currency VARCHAR,                      -- eur
    payment_type VARCHAR,                  -- micropayment, subscription
    article_id VARCHAR,                    -- NULL for subscriptions
    status VARCHAR,                        -- pending, completed, failed
    created_at DATETIME,
    completed_at DATETIME
);
```

### Advertisements Table

```sql
CREATE TABLE advertisements (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    image_url VARCHAR NOT NULL,
    click_url VARCHAR NOT NULL,
    advertiser_id VARCHAR,                 -- Advertiser's company
    category VARCHAR,                      -- medical, wellness, health-tech
    is_active BOOLEAN,
    impressions INTEGER,
    clicks INTEGER,
    created_at DATETIME
);
```

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Health Check
curl http://localhost:8050/health

# 2. Status
curl http://localhost:8050/status

# 3. List Articles
curl http://localhost:8050/api/v1/articles

# 4. Create Payment Intent (requires auth token)
curl -X POST http://localhost:8050/api/v1/payments/article \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"article_id":"med_123","source":"dr_albana"}'

# 5. Subscribe
curl -X POST http://localhost:8050/api/v1/payments/subscribe \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"tier":"monthly"}'
```

### Unit Tests

```python
# tests/test_blog_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_articles():
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_purchase_article_unauthorized():
    response = client.post("/api/v1/payments/article",
        json={"article_id": "test", "source": "dr_albana"}
    )
    assert response.status_code == 401
```

---

## 🔒 Security Considerations

### API Security

1. **Authentication**: Verify Clerk JWT tokens on every request
2. **CORS**: Configure allowed origins
3. **Rate Limiting**: Implement per-user request limits
4. **HTTPS**: Enforce in production
5. **CSRF Protection**: Use SameSite cookies

### Payment Security

1. **PCI Compliance**: Never handle raw card data (Stripe handles it)
2. **Webhook Verification**: Validate Stripe webhook signatures
3. **Idempotent Payments**: Use Idempotency-Keys
4. **No Logging**: Never log sensitive payment info

### Data Privacy

1. **GDPR Compliance**: Implement data export/deletion
2. **Data Retention**: Delete user data after 3 years per GDPR
3. **Encryption**: Encrypt sensitive fields in database

---

## 📱 Frontend Components

### Header Navigation

```
┌─────────────────────────────────────────┐
│ 🔵 Clisonix Blog  [Artikujt] [Abonim] [Hyr]
└─────────────────────────────────────────┘
```

### Main Content Area

```
┌──────────────────────────────────────────────────┐  ┌────────────────┐
│  Article 1  | Article 2 | Article 3             │  │    Abonim      │
│  [Preview]  | [Preview] | [Preview]             │  │  €4,99/muaj    │
│  €0,10      | Falas     | €0,10                 │  │  [Subscribe]   │
├──────────────────────────────────────────────────┤  ├────────────────┤
│  [More Articles...]                            │  │   Profili      │
└──────────────────────────────────────────────────┘  │  Përdoruesit    │
                                                      └────────────────┘
```

### Payment Modal

```
┌──────────────────────────────────────┐
│ 🔒 Siguri Pagese                    │
├──────────────────────────────────────┤
│ [Stripe Payment Element]             │
│  Card / Apple Pay / Google Pay       │
├──────────────────────────────────────┤
│ [€0,10] Përfundo Pagesen            │
└──────────────────────────────────────┘
```

---

## 📈 Growth Strategy

### Phase 1: Launch (Month 1)
- ✅ Deploy blog API
- ✅ Integrate Stripe
- ✅ Launch with 50 articles
- ✅ Target: 500 users

### Phase 2: Expansion (Month 2-3)
- Add email newsletter
- Implement analytics dashboard
- A/B testing on pricing
- Target: 2000 users, €300 MRR

### Phase 3: Optimization (Month 4+)
- Premium features (API access)
- Corporate subscriptions
- Affiliate program
- Target: 5000+ users, €1000+ MRR

---

## 🛠️ Troubleshooting

### Common Issues

**1. Stripe payment fails**
- Check `STRIPE_SECRET_KEY` environment variable
- Verify webhook secret is correct
- Test with Stripe test cards

**2. Articles not loading**
- Check DR_ALBANA_URL is reachable
- Verify JWT token is valid
- Check database connection

**3. Ads not displaying**
- Ensure advertisements are marked `is_active=true`
- Check user subscription tier
- Verify ad image URLs are valid

---

## 📞 Support & Contact

**Developer**: Ledjan Ahmati (CEO, ABA GmbH)
**Email**: clisonix@pm.me
**Documentation**: https://docs.clisonix.com/blog

---

**Version**: 2.0.0  
**Last Updated**: March 12, 2026  
**License**: Proprietary © 2026 ABA GmbH

