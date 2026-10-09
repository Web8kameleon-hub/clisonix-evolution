# 🚀 PRODUCTION DEPLOYMENT CHECKLIST
# CLISONIX LIVE - 46.225.14.83
# Time Required: 30-45 minutes

## PRE-DEPLOYMENT (Local Machine - 5 min)

- [ ] Read entire PRODUCTION_DEPLOYMENT_GUIDE.md
- [ ] Commit changes to git: `git commit -m "Production: docker-compose.production.yml, nginx.production.conf"`
- [ ] Verify no uncommitted changes: `git status`
- [ ] Copy files to server (follow guide)

```bash
scp -i ~/.ssh/id_ed25519_nopwd \
    docker-compose.production.yml \
    nginx.production.conf \
    root@46.225.14.83:/opt/clisonix-cloud/
```

## BACKUP PHASE (Production Server - 10 min)

- [ ] SSH to server: `ssh -i ~/.ssh/id_ed25519_nopwd root@46.225.14.83`
- [ ] Run backup script: `bash /opt/clisonix-cloud/backup.sh`
- [ ] Verify backups: `ls -lah /opt/clisonix-cloud/backups/`
- [ ] Test restore (optional): `head /opt/clisonix-cloud/backups/db-backup-*.sql.gz`

## CONFIGURATION PHASE (Production Server - 5 min)

- [ ] Create .env.production: `cp .env.production.example .env.production`
- [ ] Edit secrets: `nano /opt/clisonix-cloud/.env.production`
  - [ ] Set DB_PASSWORD (32+ chars)
  - [ ] Set REDIS_PASSWORD (32+ chars)
  - [ ] Set JWT_SECRET (64+ chars)
  - [ ] Set STRIPE_SECRET_KEY
  - [ ] Set STRIPE_WEBHOOK_SECRET
  - [ ] Set other API keys
- [ ] Verify permissions: `chmod 600 .env.production`
- [ ] Test loading: `source .env.production && echo $DB_PASSWORD`

## VALIDATION PHASE (Production Server - 3 min)

- [ ] Run validation: `bash /opt/clisonix-cloud/validate.sh`
- [ ] All checks must be GREEN ✅
- [ ] If any RED ❌, fix and re-run

```bash
# Within validate.sh logic:
docker-compose -f docker-compose.production.yml.new config > /dev/null 2>&1
docker run --rm -v /opt/clisonix-cloud:/etc/nginx:ro nginx:alpine \
  nginx -t -c /etc/nginx/nginx.production.conf
test -f /opt/clisonix-cloud/certs/cert.pem
```

## DEPLOYMENT PHASE (Production Server - 10 min)

- [ ] Start new services:
```bash
cd /opt/clisonix-cloud
export $(cat .env.production | grep -v '^#' | xargs)
docker-compose -f docker-compose.production.yml.new up -d postgres redis ollama ocean-core ocean-multilayer
```

- [ ] Wait 30 seconds for services to stabilize
- [ ] Quick health check:
```bash
curl -f http://localhost:8030/health && echo "✅ ocean-core"
curl -f http://localhost:8031/api/v2/health && echo "✅ ocean-multilayer"
```

- [ ] Start API and web:
```bash
docker-compose -f docker-compose.production.yml.new up -d api web
```

- [ ] Wait another 30 seconds
- [ ] Verify API: `curl -f http://localhost:8000/health && echo "✅ api"`

## MONITORING PHASE (Separate Terminal - 10 min)

- [ ] Open new terminal to server
- [ ] Start monitoring: `bash /opt/clisonix-cloud/monitor.sh`
- [ ] Keep this running during traffic switch
- [ ] Watch for any ❌ indicators
- [ ] If failures, stop immediately and rollback (see guide)

## TRAFFIC SWITCH PHASE (Production Server - 2 min)

**⚠️ CRITICAL - Only proceed if monitoring shows all ✅**

```bash
bash /opt/clisonix-cloud/switch-nginx.sh
```

Confirm with: `yes`

Wait for completion:
- [ ] ✅ nginx config backed up
- [ ] ✅ New config installed  
- [ ] ✅ nginx reloaded
- [ ] ✅ Health checks passed

## POST-SWITCH VERIFICATION (2 min)

In browser (or curl):
- [ ] `https://clisonix.com/` → loads website
- [ ] `https://clisonix.com/health` → returns 200 OK
- [ ] `https://clisonix.com/api/v2/health` → Ocean responds
- [ ] Chat feature works: type message in web app

In terminal:
- [ ] `curl https://clisonix.com/api/users/me` → API accessible
- [ ] `docker logs clisonix-nginx | tail -20` → No errors
- [ ] `docker ps` → All services running

## CLEANUP PHASE (Production Server - 2 min)

**Only if all monitoring passes for 5+ minutes:**

```bash
bash /opt/clisonix-cloud/cleanup.sh
```

- [ ] Confirm cleanup with: `yes`
- [ ] Verify no dangling containers/volumes
- [ ] Update documentation

## FINAL CHECKS (5 min)

- [ ] Load website → should be responsive
- [ ] Test API endpoints on all major routes
- [ ] Check server logs for errors: `docker logs clisonix-api 2>&1 | grep ERROR`
- [ ] Monitor resource usage: `docker stats`
- [ ] Cloudflare analytics showing traffic
- [ ] Database queries working (`docker exec clisonix-postgres psql...`)

## ROLLBACK PROCEDURE (If anything goes wrong)

```bash
cd /opt/clisonix-cloud

# 1. Stop new deployment
docker-compose -f docker-compose.production.yml.new down

# 2. Restore nginx
cp nginx.conf.backup-LATEST nginx.conf
docker exec clisonix-nginx nginx -s reload

# 3. Restart old stack
docker-compose -f docker-compose.yml up -d

# 4. Verify
curl -f http://clisonix.com/health
```

## POST-DEPLOYMENT (Next day)

- [ ] Review monitoring dashboards
- [ ] Check error logs: `docker logs clisonix-api | grep -i error`
- [ ] Test critical features end-to-end
- [ ] Document any issues found
- [ ] Set up automated backups
- [ ] Schedule next deployment review

---

## Emergency Contacts

**If stuck at any step:**
1. Stop and rollback immediately
2. Check PRODUCTION_DEPLOYMENT_GUIDE.md for detailed steps
3. Review server logs: `docker logs clisonix-* 2>&1 | tail -50`
4. Production server: 46.225.14.83
5. Git history: `git log --oneline | head -10`

---

**Estimated Total Time: 35-45 minutes**
**Downtime Expected: 0 seconds (zero-downtime deployment)**
**Backup Recovery Time: 5 minutes**

✅ Ready to deploy? Start with PRE-DEPLOYMENT section above.
