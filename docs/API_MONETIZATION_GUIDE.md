# 💰 Clisonix API Monetization Guide

## Overview

Three-tier API monetization system for Clisonix with rate limiting, usage tracking, and subscription management.

---

## 📋 API Plans

### Free Plan
- **Requests/Day**: 1,000
- **Requests/Month**: 20,000
- **Price**: €0/month
- **Features**: Public API, Basic endpoints, Community support

### Pro Plan
- **Requests/Day**: 10,000
- **Requests/Month**: 200,000
- **Price**: €29/month
- **Features**: Full API access, Priority support, Usage analytics

### Enterprise Plan
- **Requests/Day**: 50,000
- **Requests/Month**: 1,000,000
- **Price**: €99/month (custom)
- **Features**: Unlimited access, Dedicated support, SLA, Custom integration

---

## 🔑 API Key Management

### Get Available Plans
```bash
GET /api/v1/api-access/plans

Response:
{
  "free": {
    "name": "Free",
    "requests_per_day": 1000,
    "requests_per_month": 20000,
    "price_monthly": 0,
    "features": ["Public API", "Basic endpoints", "Community support"]
  },
  ...
}
```

### Create API Key
```bash
POST /api/v1/api-access/keys/create
Headers:
  X-User-ID: user_123

Body:
{
  "name": "My App Key",
  "plan": "pro"  # free, pro, enterprise
}

Response:
{
  "status": "created",
  "api_key": "clx_pro_abc123def456xyz789...",
  "key_prefix": "clx_pro_abc1",
  "plan": "pro",
  "message": "Save this key securely. You won't see it again."
}
```

**⚠️ Important**: API key shown only ONCE. Store safely!

### List API Keys
```bash
GET /api/v1/api-access/keys
Headers:
  X-User-ID: user_123

Response:
[
  {
    "id": "key_abc123",
    "key_prefix": "clx_pro_abc1",
    "plan": "pro",
    "name": "My App Key",
    "created_at": "2026-03-12T15:00:00Z",
    "is_active": true
  }
]
```

### Revoke API Key
```bash
POST /api/v1/api-access/keys/{key_id}/revoke
Headers:
  X-User-ID: user_123

Response:
{
  "status": "revoked"
}
```

### Check API Usage
```bash
GET /api/v1/api-access/usage/{key_id}
Headers:
  X-User-ID: user_123

Response:
{
  "plan": "pro",
  "today": {
    "requests": 2345,
    "limit": 10000,
    "percentage": 23.45
  },
  "month": {
    "requests": 45678,
    "limit": 200000,
    "percentage": 22.84
  }
}
```

---

## 🔐 Using API Keys

### Authenticate Request
```bash
GET /api/v1/articles?limit=10
Headers:
  X-API-Key: clx_pro_abc123def456xyz789...
  Content-Type: application/json
```

### Error Responses

**Invalid Key**:
```json
{
  "detail": "API key not found"
}
```
Status: `401 Unauthorized`

**Rate Limited**:
```json
{
  "detail": "Rate limit exceeded for today"
}
```
Status: `429 Too Many Requests`

**Revoked Key**:
```json
{
  "detail": "API key has been revoked"
}
```
Status: `401 Unauthorized`

---

## 📊 Admin Endpoints

### Get User Monetization Summary
```bash
GET /api/v1/api-access/admin/users/{user_id}/summary
Headers:
  X-Admin-Token: admin_secret_token

Response:
{
  "user_id": "user_123",
  "subscription": {
    "plan": "pro",
    "is_active": true,
    "renews_at": "2026-04-12T15:00:00Z"
  },
  "api_keys_active": 3,
  "total_api_requests": 450000
}
```

### Validate API Key (Internal)
```bash
POST /api/v1/api-access/validate
Headers:
  X-API-Key: clx_pro_abc123...

Response:
{
  "valid": true,
  "plan": "pro",
  "user_id": "user_123",
  "requests_today": 2345,
  "daily_limit": 10000,
  "rate_limited": false
}
```

---

## 💳 Integration with Stripe

### Upgrade Plan (TODO)
```bash
POST /api/v1/api-access/upgrade
Headers:
  X-User-ID: user_123

Body:
{
  "plan": "pro"  # Free → Pro: €29/month
}

Response:
{
  "status": "checkout_created",
  "stripe_checkout_url": "https://checkout.stripe.com/pay/cs_..."
}
```

---

## 📈 Monetization Roadmap

### Implemented ✅
- [x] 3-tier plan system
- [x] API key generation & revocation
- [x] Rate limiting per plan
- [x] Usage tracking (daily/monthly)
- [x] Admin monitoring

### Phase 2 (Stripe Integration)
- [ ] Automatic billing per Stripe
- [ ] Plan upgrades/downgrades
- [ ] Invoice management
- [ ] Refund handling

### Phase 3 (Analytics & Alerts)
- [ ] Per-endpoint usage breakdown
- [ ] Usage alerts (80%, 100% limits)
- [ ] Revenue dashboard
- [ ] Custom API restrictions per key

### Phase 4 (Enterprise)
- [ ] White-label plans
- [ ] SLA enforcement
- [ ] Dedicated IP support (optional)
- [ ] Custom rate limits

---

## 🚀 Quick Start

1. **Get your API key**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/api-access/keys/create \
     -H "X-User-ID: your-user-id" \
     -H "Content-Type: application/json" \
     -d '{"name": "My App", "plan": "free"}'
   ```

2. **Make authenticated request**:
   ```bash
   curl http://localhost:8000/api/v1/articles \
     -H "X-API-Key: clx_free_..."
   ```

3. **Monitor usage**:
   ```bash
   curl http://localhost:8000/api/v1/api-access/usage/key_abc123 \
     -H "X-User-ID: your-user-id"
   ```

---

## 💡 Best Practices

1. **Secure Storage**: Store API keys in environment variables, not in code
2. **Rotation**: Rotate keys periodically (every 90 days recommended)
3. **Scoping**: Create separate keys for each app/service
4. **Monitoring**: Set up alerts for 80% of limit reached
5. **Version**: Always include API version in requests (`/api/v1/...`)

---

## 📞 Support

- **Free Plan**: Community forum, email support (48h response)
- **Pro Plan**: Priority email support (4h response), Slack channel
- **Enterprise**: Dedicated account manager, SLA guarantee

For issues: clisonix@pm.me

