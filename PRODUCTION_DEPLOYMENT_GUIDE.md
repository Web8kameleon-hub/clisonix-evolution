# ⚠️ PRODUCTION DEPLOYMENT GUIDE

# CLISONIX LIVE INFRASTRUCTURE - 178.63.89.121

# CRITICAL: Read entire guide before executing any commands

---

## 🔴 SAFETY FIRST

**NEVER deploy during peak usage hours (9-18 UTC)**

### Pre-Deployment Checklist

- [ ] Backup current database
- [ ] Backup current nginx configuration
- [ ] Test new configuration on staging first
- [ ] Have rollback plan ready
- [ ] Notify team 30 minutes before deployment
- [ ] Monitor health endpoints actively during deployment

---

## 📋 CURRENT PRODUCTION STATE (178.63.89.121)

### Active Services

```
✅ nginx-gw:80/443         (Reverse proxy)
✅ clisonix-web:3000       (Next.js frontend)
✅ clisonix-api:8000       (FastAPI backend)
✅ clisonix-postgres:5432  (Database)
✅ clisonix-redis:6379     (Cache)
✅ clisonix-ollama:11434   (LLM inference)
✅ clisonix-ocean-core:8030 (Ocean AI)
✅ clisonix-ocean-multilayer:8031 (Ocean v2.0)
```

### Current DNS/SSL

- Domain: clisonix.com
- SSL: Let's Encrypt (auto-renewal)
- Cloudflare: Flexible SSL mode

---

## 📂 FILE STRUCTURE (PRODUCTION)

```
/opt/clisonix-cloud/
├── docker-compose.production.yml    ← NEW
├── nginx.production.conf             ← NEW
├── .env.production                   ← SECRETS (NOT in git)
├── .env.production.template          ← TEMPLATE
├── certs/                            ← SSL certificates
│   ├── cert.pem
│   └── key.pem
├── backups/                          ← Daily backups
│   ├── db-backup-YYYY-MM-DD.sql
│   └── nginx-backup-YYYY-MM-DD.conf
└── README.md
```

---

## 🚀 STEP 1: PRE-DEPLOYMENT BACKUP

### On Production Server (178.63.89.121)

```bash
# SSH to server
ssh -i ~/.ssh/id_ed25519_nopwd root@178.63.89.121

# Create backup directory
mkdir -p /opt/clisonix-cloud/backups

# Backup PostgreSQL
docker exec clisonix-postgres pg_dump \
  -U clisonix -d clisonixdb > \
  /opt/clisonix-cloud/backups/db-backup-$(date +%Y-%m-%d-%H%M%S).sql

# Backup current nginx config
cp /opt/clisonix-cloud/nginx.conf \
   /opt/clisonix-cloud/backups/nginx-backup-$(date +%Y-%m-%d-%H%M%S).conf

# Backup docker-compose
cp /opt/clisonix-cloud/docker-compose.yml \
   /opt/clisonix-cloud/backups/docker-compose-backup-$(date +%Y-%m-%d-%H%M%S).yml

# Verify backups
ls -lah /opt/clisonix-cloud/backups/
```

---

## 🔧 STEP 2: PREPARE NEW CONFIGURATION

### On Local Machine

```bash
# 1. Copy new production files to server
scp -i ~/.ssh/id_ed25519_nopwd \
    docker-compose.production.yml \
    root@46.225.14.83:/opt/clisonix-cloud/docker-compose.production.yml.new

scp -i ~/.ssh/id_ed25519_nopwd \
    nginx.production.conf \
    root@46.225.14.83:/opt/clisonix-cloud/nginx.production.conf.new

# 2. Copy .env.production.template as template
scp -i ~/.ssh/id_ed25519_nopwd \
  .env.production.template \
  root@46.225.14.83:/opt/clisonix-cloud/.env.production.template
```

---

## 🔐 STEP 3: CONFIGURE SECRETS (.env.production)

### On Production Server

⚠️ **CRITICAL**: Never commit .env.production to git

```bash
ssh -i ~/.ssh/id_ed25519_nopwd root@46.225.14.83

# Create .env.production from template
cp /opt/clisonix-cloud/.env.production.template \
   /opt/clisonix-cloud/.env.production

# Edit with real values (use nano or vim)
nano /opt/clisonix-cloud/.env.production
```

**MUST FILL (Real values):**

```
DB_PASSWORD=STRONG_32_CHAR_PASSWORD_HERE
REDIS_PASSWORD=STRONG_32_CHAR_PASSWORD_HERE
JWT_SECRET=LONG_SECRET_KEY_64_CHARS_MIN
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
PAYPAL_CLIENT_ID=xxxxx
PAYPAL_CLIENT_SECRET=xxxxx
SEPA_API_KEY=xxxxx
```

**Verify file is secure:**

```bash
chmod 600 /opt/clisonix-cloud/.env.production
ls -la /opt/clisonix-cloud/.env.production
```

---

## ✅ STEP 4: VALIDATE CONFIGURATIONS

### On Production Server

```bash
cd /opt/clisonix-cloud

# 1. Test nginx config syntax
docker run --rm -v $(pwd):/etc/nginx:ro nginx:alpine \
  nginx -t -c /etc/nginx/nginx.production.conf

# 2. Test docker-compose syntax
docker-compose -f docker-compose.production.yml.new config > /dev/null && \
  echo "✅ Docker compose config valid" || \
  echo "❌ Docker compose config invalid"

# 2.1 Validate env required variables
bash ./scripts/preflight-env.sh .env.production

# 3. Check certificate chain
test -f /opt/clisonix-cloud/certs/cert.pem && \
  echo "✅ SSL cert exists" || \
  echo "❌ SSL cert missing"

# 4. Verify .env.production exists
test -f /opt/clisonix-cloud/.env.production && \
  echo "✅ .env.production exists" || \
  echo "❌ .env.production missing"
```

---

## 🟡 STEP 5: ZERO-DOWNTIME DEPLOYMENT

### Phase 1: Start New Services (non-disruptive)

```bash
cd /opt/clisonix-cloud

# Load environment
export $(cat .env.production | grep -v '^#' | xargs)

# Start new stack alongside old (on different network)
docker-compose -f docker-compose.production.yml.new \
  up -d postgres redis ollama ocean-core ocean-multilayer

# Wait for services to be healthy
echo "⏳ Waiting for services to stabilize..."
sleep 30

# Health check
curl -f http://localhost:8030/health && echo "✅ ocean-core UP" || echo "❌ ocean-core DOWN"
curl -f http://localhost:8031/api/v2/health && echo "✅ ocean-multilayer UP" || echo "❌ ocean-multilayer DOWN"
curl -f http://localhost:8000/health && echo "✅ api UP" || echo "❌ api DOWN"
```

### Phase 2: Update API (handles requests)

```bash
# Verify API can connect to database
docker logs clisonix-api 2>&1 | tail -20
```

### Phase 3: Update Frontend (static content)

```bash
# Check frontend is serving
curl -I http://localhost:3000/ | grep "200\|301\|302"
```

### Phase 4: Switch Nginx Traffic (CRITICAL)

```bash
cd /opt/clisonix-cloud

# 1. Backup current nginx
cp nginx.conf nginx.conf.backup-$(date +%Y%m%d-%H%M%S).conf

# 2. Replace nginx config
cp nginx.production.conf nginx.conf

# 3. Reload nginx (zero-downtime)
docker exec clisonix-nginx nginx -s reload

# 4. Verify nginx is still running
docker ps | grep nginx-gw | grep -q "Up" && \
  echo "✅ nginx reloaded successfully" || \
  echo "❌ nginx failed - rollback immediately"
```

### Phase 5: Remove Old Containers

```bash
# After 5 minutes of monitoring (see below)
docker-compose -f docker-compose.yml down \
  --remove-orphans \
  --volumes
```

---

## 📊 STEP 6: MONITORING & VALIDATION

### Real-time Health Checks (during deployment)

```bash
# Monitor every 5 seconds for 10 minutes (120 checks)
for i in {1..120}; do
  echo "=== Check $i [$(date)] ==="
  curl -s http://clisonix.com/health | jq '.' 2>/dev/null || echo "❌ UNHEALTHY"
  curl -s http://clisonix.com/api/v2/health | jq '.' 2>/dev/null || echo "❌ OCEAN DOWN"
  docker ps -q | wc -l | xargs echo "Active containers:"
  echo ""
  sleep 5
done
```

### Manual Test Checklist

```bash
# 1. Website loads
curl -I https://clisonix.com/ | head -5

# 2. API responds
curl https://clisonix.com/health | jq '.'

# 3. Ocean chat works
curl -X POST https://clisonix.com/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "temperature": 0.7}'

# 4. Database is accessible
docker exec clisonix-postgres psql -U clisonix -d clisonixdb -c "SELECT 1"

# 5. Redis is accessible
docker exec clisonix-redis redis-cli PING
```

---

## 🔴 ROLLBACK PROCEDURE

**If anything goes wrong at ANY point:**

```bash
cd /opt/clisonix-cloud

# 1. Stop current deployment
docker-compose -f docker-compose.production.yml.new down

# 2. Restore old config
cp nginx.conf.backup-* nginx.conf

# 3. Reload nginx
docker exec clisonix-nginx nginx -s reload

# 4. Start old containers
docker-compose -f docker-compose.yml up -d

# 5. Verify old stack
curl -f http://clisonix.com/health

# 6. If DB is corrupted, restore from backup
docker exec clisonix-postgres psql -U clisonix -d clisonixdb < \
  /opt/clisonix-cloud/backups/db-backup-LATEST.sql

# 7. Alert team
echo "⚠️ ROLLBACK COMPLETED - Investigation required"
```

---

## 📝 DEPLOYMENT COMMANDS SUMMARY

```bash
# BEFORE deployment (local machine)
git commit -m "Production deployment: docker-compose.production.yml, nginx.production.conf"

# Phase 1: Backup (production server)
ssh root@46.225.14.83 'bash /opt/clisonix-cloud/backup.sh'

# Phase 2: Copy new configs (local machine)
scp docker-compose.production.yml root@46.225.14.83:/opt/clisonix-cloud/docker-compose.production.yml.new
scp nginx.production.conf root@46.225.14.83:/opt/clisonix-cloud/nginx.production.conf.new

# Phase 3: Configure secrets (production server - MANUAL)
ssh root@46.225.14.83 'nano /opt/clisonix-cloud/.env.production'

# Phase 4: Validate (production server - MANUAL)
ssh root@46.225.14.83 'bash /opt/clisonix-cloud/validate.sh'

# Phase 5: Deploy (production server - MANUAL, one command at a time)
ssh root@46.225.14.83 'cd /opt/clisonix-cloud && docker-compose -f docker-compose.production.yml.new up -d'

# Phase 6: Monitor (production server - MANUAL, in separate terminal)
ssh root@46.225.14.83 'bash /opt/clisonix-cloud/monitor.sh'

# Phase 7: Switch nginx (production server - MANUAL, after 5-10 min monitoring)
ssh root@46.225.14.83 'bash /opt/clisonix-cloud/switch-nginx.sh'

# Phase 8: Cleanup (production server - MANUAL, after all tests pass)
ssh root@46.225.14.83 'bash /opt/clisonix-cloud/cleanup.sh'
```

---

## 🚨 EMERGENCY CONTACTS

If deployment fails:

1. Rollback immediately (see ROLLBACK section above)
2. Check cloudflare dashboard (clisonix.com SSL settings)
3. Review server logs: `docker logs clisonix-nginx 2>&1 | tail -50`
4. Production server: 46.225.14.83
5. Git history: revert to last stable commit

---

## ✨ AFTER DEPLOYMENT

- [ ] Test all endpoints in production
- [ ] Check Cloudflare analytics
- [ ] Monitor server resource usage
- [ ] Review logs for errors
- [ ] Update DNS if needed
- [ ] Document any changes
- [ ] Schedule daily backups
- [ ] Set up monitoring alerts

---

**Version**: 1.0
**Last Updated**: 2026-02-19
**Status**: READY FOR PRODUCTION DEPLOYMENT
