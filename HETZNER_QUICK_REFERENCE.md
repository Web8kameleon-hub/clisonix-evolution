# ═══════════════════════════════════════════════════════════════════════════════
# CLISONIX CLOUD - HETZNER DEPLOYMENT QUICK REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Server: cpx62 @ 46.62.210.251 (Helsinki, Finland)
# Microservices: 75+ via docker-compose.75-services.yml
# Total Resource: 16 vCPU, 32 GB RAM, 640 GB SSD
#
# Created: May 28, 2026
# ═══════════════════════════════════════════════════════════════════════════════

## 🔑 SERVER CREDENTIALS
```
IP Address:     46.62.210.251
IPv6:           2a01:4f9:c014:5603::/64
Hostname:       cpx62-hel1-2
Region:         Helsinki, Finland
User:           root
SSH Port:       22
```

## 📋 MICROSERVICES TIERS

| Tier             | Services                                         | Count  | Status      |
| ---------------- | ------------------------------------------------ | ------ | ----------- |
| Infrastructure   | PostgreSQL, Redis, Neo4j, MinIO, VictoriaMetrics | 5      | ✅           |
| AI/LLM           | Ollama, Ocean, Kloud, Curiosity, OpenMind, CLX   | 11+    | ✅           |
| Trinity (ASI)    | ALBA, ALBI, JONA, ASI                            | 4      | ✅           |
| Core Engines     | Alphabet, LIAM, ALDA, Blerina, Cycle, SaaS       | 12+    | ✅           |
| Distributed Labs | European Tech Hubs (23+)                         | 23+    | ✅           |
| Global Data      | Continental DataSources (8)                      | 8      | ✅           |
| Business         | Marketplace, Economy, Reporting, Analytics       | 5+     | ✅           |
| Content          | Dr. Albana, Blog Publisher, Aviation, Media      | 7+     | ✅           |
| Frontend         | Web, API, Auth, Billing, Nginx                   | 7      | ✅           |
| Observability    | Prometheus, Grafana, Loki, Jaeger, Tempo         | 5      | ✅           |
| **TOTAL**        | **75+ microservices**                            | **89** | **✅ READY** |

## 🚀 QUICK START COMMANDS

### 1. SSH to Server
```bash
ssh root@46.62.210.251
cd /opt/clisonix
```

### 2. Prepare System
```bash
bash HETZNER_DEPLOY_SETUP.sh
```

### 3. Update Secrets
```bash
nano .env.hetzner
# Edit: POSTGRES_PASSWORD, STRIPE keys, GITHUB_TOKEN, etc.
```

### 4. Start All Services (75+)
```bash
docker-compose -f docker-compose.75-services.yml \
  --env-file .env.hetzner \
  up -d
```

### 5. Monitor Startup
```bash
watch -n 2 'docker compose ps | grep -E "clisonix" | wc -l'
# Target: 89 running containers
```

### 6. Verify Core Services
```bash
# Check if key services are healthy
curl http://localhost:8000/health      # API
curl http://localhost:8030/health      # Ocean Core
curl http://localhost:5555/health      # ALBA
curl http://localhost:6680/health      # ALBI
curl http://localhost:11434/api/tags   # Ollama
```

## 📊 SERVICE PORTS REFERENCE

### Core Infrastructure
```
PostgreSQL       5432    (Internal only)
Redis            6379    (Internal only)
Neo4j UI         7474    (Graph DB console)
MinIO Console    9001    (Object storage UI)
VictoriaMetrics  8428    (Metrics DB)
```

### Public APIs
```
Main API         8000    ← Primary endpoint
Web Frontend     3000    ← Next.js app
Ocean Core       8030    ← AI Engine
Ollama           11434   ← LLM server
OpenMind         9999    ← Gateway Intel
```

### Observability
```
Grafana          3001    ← Dashboards
Prometheus       9090    ← Metrics
Jaeger           16686   ← Tracing
Loki             3100    ← Logs
Tempo            3200    ← Distributed traces
```

### Specialty Services
```
Dr. Albana       8040    ← Medical content
Blog Publisher   8041    ← Blog automation
JONA             7777    ← Coordinator
ALBA             5555    ← Analysis
ALBI             6680    ← Creativity
ASI              9094    ← Super Intelligence
```

### Labs (Sample)
```
Lab Elbasan      9101    ← AI/ML (Albania)
Lab Tirana       9102    ← Medical (Albania)
Lab Athens       9110    ← Classical (Greece)
Lab Rome         9111    ← Architecture (Italy)
Lab Zurich       9112    ← Finance (Switzerland)
... 18+ more labs across Europe, Mediterranean, Africa
```

## 🔧 COMMON OPERATIONS

### View All Running Services
```bash
docker-compose -f docker-compose.75-services.yml ps

# Count running services
docker ps | grep clisonix | wc -l
```

### Check Service Logs
```bash
# API logs
docker logs clisonix-api -f

# Ocean Core logs
docker logs clisonix-ocean-core -f

# Ollama startup
docker logs clisonix-ollama -f

# JONA coordinator
docker logs clisonix-jona -f
```

### Resource Usage
```bash
# Real-time CPU/Memory
docker stats

# Specific services
docker stats --no-stream clisonix-api clisonix-ocean-core clisonix-ollama
```

### Restart Services
```bash
# Specific service
docker-compose -f docker-compose.75-services.yml restart clisonix-api

# All services
docker-compose -f docker-compose.75-services.yml restart

# Stop all
docker-compose -f docker-compose.75-services.yml down

# Stop and remove volumes (careful!)
docker-compose -f docker-compose.75-services.yml down -v
```

### Database Operations
```bash
# PostgreSQL shell
docker exec -it clisonix-postgres psql -U clisonix -d clisonixdb

# Redis CLI
docker exec -it clisonix-redis redis-cli

# Neo4j browser
open http://46.62.210.251:7474
# Username: neo4j
# Password: neo4j_secure_hetzner_2026
```

## 📈 DEPLOYMENT PHASES

### Phase 1: Infrastructure (15 min)
- System update & Docker installation
- Network creation
- Database startup

### Phase 2: AI Engines (30 min)
- Ollama initialization
- Ocean Core startup
- Model download

### Phase 3: Trinity Stack (5 min)
- ALBA, ALBI, JONA, ASI

### Phase 4: Labs & DataSources (10 min)
- 23 Distributed Labs
- 8 Global DataSources

### Phase 5: Business Services (10 min)
- Marketplace, SaaS, Economy

### Phase 6: Frontend & Gateway (5 min)
- Web UI, Nginx, Auth

### Phase 7: Observability (5 min)
- Prometheus, Grafana setup

**Total Deployment Time: ~90 minutes (1.5 hours)**

## 🔐 SECURITY ESSENTIALS

```bash
# 1. Secure environment variables
chmod 600 .env.hetzner

# 2. Setup firewall
ufw enable
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS

# 3. Configure Hetzner Floating IP
# Add via console: 46.62.210.251 (static)

# 4. SSL Certificate (Let's Encrypt)
# certbot certonly --standalone -d clisonix.example.com

# 5. Database backups
# Configure PostgreSQL backup scripts
```

## 📞 MONITORING & ALERTS

### Health Endpoints
```bash
# API health
http://46.62.210.251:8000/health

# Ocean Core health
http://46.62.210.251:8030/health

# System health monitor
http://46.62.210.251:8099/health
```

### Grafana Dashboard
```
URL: http://46.62.210.251:3001
User: admin
Pass: clisonix (change immediately)
```

### Alert Rules to Configure
- CPU > 80%
- Memory > 75%
- Disk > 85%
- API response time > 2s
- Service restart count > 3
- Database connection pool exhaustion

## ✅ POST-DEPLOYMENT CHECKLIST

- [ ] All 89 services running
- [ ] Database migrations completed
- [ ] Redis data persistence enabled
- [ ] Backup job running
- [ ] SSL/TLS configured
- [ ] Floating IP assigned
- [ ] DNS records updated
- [ ] Monitoring alerts active
- [ ] Log aggregation working
- [ ] Rate limiting configured
- [ ] API documentation accessible
- [ ] Web frontend responsive
- [ ] Payment processing tested
- [ ] GitHub integration verified
- [ ] Clerk auth working
- [ ] Ollama model loaded
- [ ] Ocean Core responding
- [ ] JONA coordinator active
- [ ] All labs registering
- [ ] DataSources reachable

## 🆘 TROUBLESHOOTING

### Service Not Starting
```bash
docker logs <service_name>
docker inspect <service_name>
docker-compose config
```

### Port Conflicts
```bash
lsof -i :8000
netstat -tulpn | grep LISTEN
```

### Memory Issues
```bash
free -h
docker system prune
docker system prune -a --volumes
```

### Network Issues
```bash
docker network ls
docker network inspect clisonix-net
ping -c 4 <container_name>
```

## 📞 SUPPORT RESOURCES

- **Docs:** `/opt/clisonix/README.md`
- **API Docs:** `http://46.62.210.251:8000/docs`
- **Hetzner Dashboard:** https://console.hetzner.cloud
- **Docker Docs:** https://docs.docker.com
- **GitHub Issues:** https://github.com/Web8kameleon-hub/clisonix.com/issues

---

**Last Updated:** May 28, 2026  
**Status:** ✅ READY FOR DEPLOYMENT  
**Microservices:** 89 confirmed  
**Deployment Time:** ~90 minutes
