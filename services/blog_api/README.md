# 🌐 Clisonix Blog Platform - Setup & Deployment Guide

## Quick Overview

A full-featured blog platform with:
- ✅ **Modern UI** - Responsive HTML/CSS with Bootstrap 5
- ✅ **User Authentication** - Clerk OAuth2
- ✅ **Payment System** - Stripe micropayments (€0.10/article) + subscriptions
- ✅ **Monetization** - Multiple revenue streams
- ✅ **Ad System** - Non-intrusive, contextual health ads
- ✅ **Database** - SQLite (dev) / PostgreSQL (production)

**Revenue Model:**
| Plan | Price | Features |
|------|-------|----------|
| Free | €0 | Preview + Ads |
| Per Article | €0.10 | Single article |
| Monthly | €4.99/month | Unlimited + No Ads |
| Yearly | €49/year | Unlimited + No Ads + Support |

---

## 📁 Project Structure

```
services/blog_api/
├── main.py                 # FastAPI backend (8050)
├── index.html              # Modern responsive frontend
├── app.js                  # Frontend JavaScript
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container config
└── README.md              # This file
```

---

## 🚀 Setup & Deployment

### 1. Local Development (Without Docker)

```bash
cd services/blog_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Export environment variables
export STRIPE_SECRET_KEY="sk_test_..."
export CLERK_SECRET_KEY="sk_test_..."
# ... other env vars

# Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8050 --reload
```

Access at: http://localhost:8050

### 2. Docker Deployment (Local)

```bash
# Build image
docker build -t clisonix-blog-api ./services/blog_api

# Run container
docker run -p 8050:8050 \
  -e STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY}" \
  -e CLERK_SECRET_KEY="${CLERK_SECRET_KEY}" \
  -v $(pwd)/blog_api_data:/app \
  clisonix-blog-api
```

### 3. Docker Compose (Full Stack)

```bash
# From project root
docker-compose up blog_api --build

# With logs
docker-compose up blog_api --build --attach blog_api
```

### 4. Production Deployment

```bash
# On Hetzner or similar
docker pull your-registry/clisonix-blog-api:latest

docker run -d \
  --name blog-api \
  -p 8050:8050 \
  -e STRIPE_SECRET_KEY="sk_live_..." \
  -e CLERK_SECRET_KEY="sk_live_..." \
  -e DATABASE_URL="postgresql://user:pass@db:5432/blog_db" \
  -v /app/blog_api_data:/app \
  --restart always \
  your-registry/clisonix-blog-api:latest

# Or with nginx reverse proxy
sudo systemctl restart nginx
```

---

## 🔧 Environment Variables

Create `.env` file:

```env
# Blog API
BLOG_API_PORT=8050

# Clerk (Get from https://dashboard.clerk.com/)
CLERK_SECRET_KEY=sk_test_abc123...
CLERK_PUBLISH_KEY=pk_test_abc123...

# Stripe (Get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_abc123...
STRIPE_PUBLISH_KEY=pk_test_abc123...
STRIPE_WEBHOOK_SECRET=whsec_abc123...

# Database
DATABASE_URL=sqlite:////app/blog_api.db
# Or: postgresql://clisonix:password@postgres:5432/blog_db

# Content Sources
DR_ALBANA_URL=http://dr_albana:8040
BLERINA_URL=http://blerina:8039

# GitHub (for publishing)
GITHUB_TOKEN=ghp_abc123...
GITHUB_REPO=ledjanahmati/clisonix-blog
```

---

## 🔌 Integration with Other Services

### Connect to Dr. Albana (Medical Articles)

Already configured! The Blog API automatically fetches articles from:
- `/api/v1/medical/pillars` (list)
- `/api/v1/medical/pillars/{id}` (detail)

### Connect to Blerina (General Content)

Update `BLERINA_URL` environment variable pointing to Blerina service.

### Connect to Blog Publisher (GitHub Sync)

Articles are automatically published to GitHub Pages via blog_publisher service (port 8041)

---

## 📚 API Endpoints

### Health & Status
```bash
GET /health                    # Simple health check
GET /status                    # Detailed status
```

### Authentication
```bash
POST /api/v1/auth/register     # Register new user
GET  /api/v1/auth/profile      # Get user profile
```

### Articles
```bash
GET  /api/v1/articles                    # List articles
GET  /api/v1/articles/{article_id}       # Get full article
```

### Payments
```bash
POST /api/v1/payments/article            # Buy single article
POST /api/v1/payments/subscribe          # Start subscription
POST /api/v1/payments/webhook            # Stripe webhook
```

### Advertisements
```bash
GET  /api/v1/ads                         # Get ads
POST /api/v1/ads/{ad_id}/click          # Track ad click
```

### Admin
```bash
GET  /api/v1/admin/analytics             # Revenue analytics
```

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8050/health

# Response
{
  "status": "healthy",
  "service": "blog-api",
  "port": 8050,
  "timestamp": "2026-03-12T14:30:00+00:00"
}
```

### List Articles
```bash
curl http://localhost:8050/api/v1/articles?limit=5
```

### Create Stripe Test Payment

1. Visit: http://localhost:8050
2. Sign in with test account
3. Click article → enters €0.10 payment
4. Use test card: `4242 4242 4242 4242`
5. Any future date, any CVC

---

## 🔐 Security Checklist

- [ ] Use HTTPS in production
- [ ] Verify Clerk JWT tokens on every request
- [ ] Validate Stripe webhook signatures
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Store secrets in environment variables (never hardcode)
- [ ] Enable CORS only for your domain
- [ ] Implement rate limiting
- [ ] Use CSRF protection
- [ ] Regular security audits

---

## 📊 Monitoring

### Metrics to Track

```bash
# Total revenue
curl http://localhost:8050/api/v1/admin/analytics | grep total_revenue_eur

# Active subscribers
curl http://localhost:8050/api/v1/admin/analytics | grep active_subscribers

# Micropayment transactions
curl http://localhost:8050/api/v1/admin/analytics | grep micropayment_transactions
```

### Log Monitoring
```bash
# Docker logs
docker logs -f clisonix-blog-api

# Follow specific service
docker-compose logs -f blog_api
```

---

## 🐛 Troubleshooting

### Issue: Stripe payments not working
**Solution:**
1. Check `STRIPE_SECRET_KEY` is set
2. Verify webhook secret matches
3. Test with Stripe test card

### Issue: Articles not loading
**Solution:**
1. Verify `DR_ALBANA_URL` is reachable
2. Check Clerk token is valid
3. Ensure database is accessible

### Issue: Ads not displaying
**Solution:**
1. Check ads are marked `is_active=true` in database
2. Verify user is not a subscriber (ads hide for paid users)
3. Test with curl: `curl http://localhost:8050/api/v1/ads`

### Issue: Database errors
**Solution:**
1. Check `DATABASE_URL` is correct
2. For SQLite: ensure `/app` directory exists
3. For PostgreSQL: verify connection string

---

## 📈 Performance Tips

1. **Caching**: Add Redis caching for article lists
2. **CDN**: Use CloudFront for frontend assets
3. **Database**: Add indexes on frequently queried columns
4. **API**: Implement request debouncing on frontend
5. **Images**: Compress and optimize with WebP

---

## 🚢 Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure backup strategy (3 copies, 3 different locations)
- [ ] Set up monitoring and alerting
- [ ] Enable SSL/TLS certificates
- [ ] Implement CI/CD pipeline
- [ ] Set up automated deployments
- [ ] Configure logging and audit trails
- [ ] Implement disaster recovery plan
- [ ] Regular security audits

---

## 📞 Support

**Issues?** Check the main documentation:
- Read: `BLOG_PLATFORM_COMPLETE.md`
- API Docs: http://localhost:8050/docs (when running)
- Email: clisonix@pm.me

---

**Version**: 2.0.0  
**Updated**: March 12, 2026  
**License**: Proprietary © 2026 Clisonix (registered legal entity: ABA GmbH)
