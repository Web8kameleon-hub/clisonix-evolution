# Clisonix AI Newsroom v5.0 - Deployment Guide

## Status: READY FOR DEPLOYMENT ✅

**Service**: Newsroom Service v5.0  
**Port**: 9800  
**Container**: `clisonix-newsroom`  
**Technology**: Python 3.11 + aiohttp + AsyncIO  
**Architecture**: 200 AI Labs + Ethics Gate + Multi-Category Publishing  
**Deployment Target**: Hetzner (Docker Compose)  

**Publishing Mode**: Automatic after all ethics gates pass

---

## 🚀 Quick Deploy (Hetzner)

### Prerequisites
- [ ] SSH access to Hetzner server (162.125.18.133)
- [ ] Docker + Docker Compose installed
- [ ] Facebook Page Token obtained
- [ ] Blog API running on port 8041

### Step 1: SSH into Hetzner
```bash
ssh root@162.125.18.133
cd /root/Clisonix-cloud
```

### Step 2: Update Configuration
```bash
# Update .env with real Facebook token
sed -i 's/YOUR_FACEBOOK_PAGE_TOKEN_HERE/YOUR_REAL_TOKEN_HERE/g' \
  services/newsroom/.env

# Verify environment
cat services/newsroom/.env
```

### Step 3: Deploy Service
```bash
# Pull latest code from GitHub
git pull origin blackboxai/fix-slo-sli-gate-errors

# Build and start newsroom service
docker compose up -d --build newsroom

# Verify status
docker ps | grep newsroom
docker logs -f clisonix-newsroom
```

### Step 4: Health Check
```bash
# Endpoint: /health
curl http://localhost:9800/health

# Expected response:
# {"status":"healthy","labs_active":200,"articles_published":0}
```

### Step 5: View Audit Log
```bash
# Endpoint: /audit?limit=10
curl http://localhost:9800/audit?limit=10

# Expected response:
# {
#   "total_articles": 0,
#   "logs": []
# }
```

---

## 🔧 Configuration Reference

### Environment Variables (in `.env`)

```dotenv
# Blog Publishing
BLOG_API_URL=http://blog-api:8041/api/publish
FB_PAGE_ID=61580581211241
FB_PAGE_TOKEN=YOUR_FACEBOOK_PAGE_TOKEN_HERE

# Service Settings
NEWSROOM_PORT=9800
PUBLISH_INTERVAL=1800              # Publish every 30 minutes
MAX_LABS=200                        # Number of parallel AI labs
POSTS_PER_DAY=10                    # Target daily article count
AUTO_PUBLISH_AFTER_ETHICS=true      # Publish automatically after ethics approval

# Redis
REDIS_URL=redis://redis:6379/1

# Ethics Enforcement
MIN_SOURCES_REQUIRED=2
ALLOW_SPECULATION=false
ALLOW_EMOTIONAL_LANGUAGE=false
ALLOW_UNVERIFIED_CLAIMS=false
```

---

## 📊 API Reference

### Health Check
```
GET /health
Response: {"status":"healthy","labs_active":200,"articles_published":N}
```

### Service Status
```
GET /status
Response: {"service":"newsroom","version":"5.0","uptime_seconds":N}
```

### Publish Config

```http
GET /publish-config
Response: {
  "auto_publish_after_ethics": true,
  "posts_per_day": 10,
  "facebook_ready": true,
  "cycle_running": false
}
```

### Audit Log
```
GET /audit?limit=10
Response: {
  "total_articles": N,
  "logs": [
    {
      "id": "article_hash",
      "timestamp": "2026-03-20T10:58:00Z",
      "category": "Technology",
      "source": "Lab-42",
      "status": "published_blog",
      "platforms": ["blog", "facebook"]
    }
  ]
}
```

### Immediate Publish Trigger (Same Ethics Gates)

```http
POST /publish-now
Response: {"status":"completed","trigger":"publish-now"}
```

This endpoint does not bypass ethics. It starts one immediate cycle using the same automatic validation and publishing flow.

---

## 📋 Article Flow

### Per Publishing Cycle:
1. **Generate** (200 labs in parallel)
   - Each lab creates 1 article
   - Random category selected
   - Sources + timestamps auto-generated
   - Ethics validation applied

2. **Validate**
   - Min 2 sources verified
   - No banned keywords found
   - No speculation detected
   - Language tone appropriate
  - All ethics instances must approve (`source_integrity`, `content_policy`, `publication_readiness`)

3. **Publish**
  - Auto-publish starts only after all ethics gates pass
  - Blog API: Send article JSON
  - Facebook: Post to page (with image + link)
   - Audit Log: Record SHA256 hash + timestamp

4. **Log**
   - Store in immutable audit trail
   - Track: category, source, platform, status, hash

---

## 📂 Article Categories & Icons

| Category    | Icon | Description          |
|-------------|------|----------------------|
| Politics    | 🏛   | Government/Policy    |
| Economy     | 📈   | Markets/Business     |
| Technology  | 💻   | Tech/AI/Innovation    |
| Health      | 🏥   | Medical/Wellness     |
| Sports      | ⚽   | Athletic Events      |
| Crisis      | 🚨   | Breaking/Emergency   |
| Environment | 🌍   | Climate/Natural      |
| Education   | 🎓   | Learning/Schools     |
| Business    | 💼   | Corporate/Finance    |
| Innovation  | 🚀   | Startups/R&D         |

---

## 🛡️ Ethics Enforcement

### Banned Keywords (Hard Filters)
- `miracle`, `cure`, `secret`, `conspiracy`, `exposed`, `shocking`
- Any unverified health claims
- Speculation markers: `might`, `could`, `rumor`, `allegedly`

### Required Elements
- ✅ Minimum 2 verified sources
- ✅ Timestamp + author attribution
- ✅ Neutral language tone
- ✅ Factual backing

### Violations
- Articles failing ethics checks → logged but NOT published
- Violations tracked in audit trail with reason code
- No manual approval is required when all ethics gates have approved the article

---

## 🔍 Monitoring

### Log Files
```bash
# Real-time logs
docker logs -f clisonix-newsroom

# Last 100 lines
docker logs --tail 100 clisonix-newsroom

# With timestamps
docker logs --timestamps clisonix-newsroom
```

### Metrics to Track
- **Publishing Rate**: Articles/hour (target: ~10/day = 0.4/hour)
- **Ethics Pass Rate**: % passing validation (target: >95%)
- **Platform Success**: Blog vs Facebook publish failures
- **Lab Utilization**: Active/idle labs (target: 200 active)

### Performance Check
```bash
# See resource usage
docker stats clisonix-newsroom

# Expected:
# CPU: <5% | Memory: 150-200MB | Network: <1KB/s average
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check Docker build logs
docker compose build --no-cache newsroom 2>&1 | tail -50

# Check Python syntax
python -m py_compile services/newsroom/main.py
```

### Health endpoint returns "unhealthy"
```bash
# Check Redis connection
docker exec clisonix-newsroom python -c "import redis; r=redis.Redis.from_url('redis://redis:6379/1'); print(r.ping())"

# Check blog API routes
curl -v http://blog-api:8041/health
```

### Facebook publishing fails
```bash
# Verify token in .env
cat services/newsroom/.env | grep FB_PAGE_TOKEN

# Check token validity (requires manual FB API test)
# Token should be 200+ chars, starts with EAAB...
```

### Articles not showing in audit log
```bash
# Trigger manual publish (bypass interval)
curl -X POST http://localhost:9800/publish -d '{"trigger":"manual","posts":1}'

# Check logs for errors
docker logs clisonix-newsroom | grep -i error
```

---

## 📈 Phase 1 Milestones (Days 1-30)

- [x] Service v5.0 code written
- [x] Docker container created + tested
- [x] docker-compose.yml integration
- [ ] Deploy to Hetzner
- [ ] First 10 articles published
- [ ] Blog integration verified
- [ ] Facebook posting active
- [ ] Audit log populated (100+ articles)
- [ ] Zero ethics violations
- [ ] 50 articles/day baseline

---

## 🔗 Related Documentation

- **Service Code**: [services/newsroom/main.py](services/newsroom/main.py)
- **Docker Config**: [services/newsroom/Dockerfile](services/newsroom/Dockerfile)
- **Dependencies**: [services/newsroom/requirements.txt](services/newsroom/requirements.txt)
- **Blog Publisher**: [services/blog_publisher/main.py](services/blog_publisher/main.py)
- **Docker Compose**: [docker-compose.yml](docker-compose.yml)
- **Blog Platform**: [https://news.clisonix.com](https://news.clisonix.com)

---

## ✅ Pre-Deployment Checklist

Before deploying to Hetzner, ensure:

- [x] main.py: 376 lines, all functions defined
- [x] Dockerfile: Multi-stage build, healthcheck configured
- [x] requirements.txt: All dependencies listed
- [x] .env: Template with all required variables
- [x] docker-compose.yml: Newsroom service added with dependencies
- [ ] Facebook Page Token obtained from Meta Business Suite
- [ ] Blog API endpoint verified (health check returns 200)
- [ ] Redis accessible on hetzner-new:6379
- [ ] SSH access to Hetzner confirmed
- [ ] Disk space available (>5GB estimated)

---

## 🎯 Success Criteria

Deployment is successful when:

1. ✅ Service container running (status: "healthy")
2. ✅ `/health` endpoint returns `{"status":"healthy"}`
3. ✅ First article published within 30 minutes of deployment
4. ✅ Article visible on blog (https://news.clisonix.com)
5. ✅ Audit log shows entry with SHA256 hash
6. ✅ No errors in docker logs
7. ✅ Memory usage <300MB, CPU <10%

---

**Last Updated**: 2026-03-20  
**Deployed By**: [Pending]  
**Deployment Date**: [Pending]  
**Status**: 🟡 READY FOR DEPLOYMENT
