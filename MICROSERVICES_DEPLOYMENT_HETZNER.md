# CLISONIX CLOUD - MICROSERVICES INVENTORY & DEPLOYMENT GUIDE
## Server: Hetzner CPX62 (Helsinki, Finland)
**Date:** May 28, 2026  
**IP:** 46.62.210.251  
**Resources:** 16 vCPU, 32 GB RAM, 640 GB SSD

---

## 📋 MICROSERVICES BREAKDOWN

### **TIER 1: INFRASTRUCTURE (5 services)**
| #   | Service         | Port      | Purpose                 |
| --- | --------------- | --------- | ----------------------- |
| 1   | PostgreSQL      | 5432      | Primary database        |
| 2   | Redis           | 6379      | Cache & session storage |
| 3   | Neo4j           | 7474-7687 | Graph database          |
| 4   | VictoriaMetrics | 8428      | Time-series metrics     |
| 5   | MinIO           | 9000-9001 | S3-compatible storage   |

### **TIER 2: AI & LLM ENGINES (10+ services)**
| #   | Service               | Port  | Purpose                    |
| --- | --------------------- | ----- | -------------------------- |
| 6   | Ollama                | 11434 | Local LLM server           |
| 7   | Ollama Multi-API      | 4444  | Multi-model orchestration  |
| 8   | Ocean Core            | 8030  | Primary AI engine          |
| 9   | Ocean Core Multimodal | 8033  | Multimodal capabilities    |
| 10  | CLX Agent             | 7778  | Independent learning agent |
| 11  | Kloud Upstream        | 9080  | Upstream runtime           |
| 12  | Kloud Bridge          | 8889  | Bridge layer               |
| 13  | Curiosity             | 8011  | Curiosity engine           |
| 14  | OpenMind              | 9999  | Gateway intelligence       |
| 15  | Cognitive Engine      | 8010  | Cognitive signatures       |
| 16  | Adaptive Router       | 8011  | Persona routing            |

### **TIER 3: TRINITY STACK - ASI (4 services)**
| #   | Service | Port | Purpose                       |
| --- | ------- | ---- | ----------------------------- |
| 17  | ALBA    | 5555 | Analytical Intelligence       |
| 18  | ALBI    | 6680 | Creative Intelligence         |
| 19  | JONA    | 7777 | Master Coordinator            |
| 20  | ASI     | 9094 | Artificial Super Intelligence |

### **TIER 4: CORE ENGINES (12+ services)**
| #   | Service           | Port | Purpose                 |
| --- | ----------------- | ---- | ----------------------- |
| 21  | Alphabet Layers   | 8061 | Layer abstraction       |
| 22  | LIAM              | 8062 | Labor Intelligence      |
| 23  | ALDA              | 8063 | Determined Arrays       |
| 24  | ALBA Idle Chat    | 8031 | Conversational          |
| 25  | Blerina           | 8035 | Document Intelligence   |
| 26  | Cycle Engine      | 8005 | Cycle management        |
| 27  | SaaS Orchestrator | 9998 | SaaS operations         |
| 28  | EAP Engine        | 9501 | Analysis-Proposal       |
| 29  | Lagter            | 9500 | Publishing orchestrator |
| 30  | Personas          | 9200 | 14+ persona APIs        |
| 31  | AGIEM             | 9300 | AGI Ecosystem Manager   |

### **TIER 5: GLOBAL DATA SOURCES (8 services)**
| #     | Service                 | Port | Purpose            |
| ----- | ----------------------- | ---- | ------------------ |
| 32-39 | DataSource EU           | 9301 | European data      |
|       | DataSource Americas     | 9302 | Americas data      |
|       | DataSource Asia         | 9303 | Asian data         |
|       | DataSource India        | 9304 | Indian data        |
|       | DataSource Africa       | 9305 | African data       |
|       | DataSource Oceania      | 9306 | Pacific data       |
|       | DataSource Central Asia | 9307 | Central Asian data |
|       | DataSource Antarctica   | 9308 | Research data      |

### **TIER 6: DISTRIBUTED LABS (18+ services)**
| #   | Service       | Port | Location      | Specialty    |
| --- | ------------- | ---- | ------------- | ------------ |
| 40  | Lab Elbasan   | 9101 | 🇦🇱 Albania     | AI/ML        |
| 41  | Lab Tirana    | 9102 | 🇦🇱 Albania     | Medical      |
| 42  | Lab Durrës    | 9103 | 🇦🇱 Albania     | IoT          |
| 43  | Lab Vlorë     | 9104 | 🇦🇱 Albania     | Environment  |
| 44  | Lab Shkodër   | 9105 | 🇦🇱 Albania     | Marine       |
| 45  | Lab Korçë     | 9106 | 🇦🇱 Albania     | Agriculture  |
| 46  | Lab Sarandë   | 9107 | 🇦🇱 Albania     | Underwater   |
| 47  | Lab Prishtina | 9108 | 🇽🇰 Kosovo      | Security     |
| 48  | Lab Kostur    | 9109 | 🇲🇰 Macedonia   | Energy       |
| 49  | Lab Athens    | 9110 | 🇬🇷 Greece      | Classical    |
| 50  | Lab Rome      | 9111 | 🇮🇹 Italy       | Architecture |
| 51  | Lab Zurich    | 9112 | 🇨🇭 Switzerland | Finance      |
| 52  | Lab Beograd   | 9113 | 🇷🇸 Serbia      | Industrial   |
| 53  | Lab Sofia     | 9114 | 🇧🇬 Bulgaria    | Chemistry    |
| 54  | Lab Zagreb    | 9115 | 🇭🇷 Croatia     | Biotech      |
| 55  | Lab Ljubljana | 9116 | 🇸🇮 Slovenia    | Quantum      |
| 56  | Lab Vienna    | 9117 | 🇦🇹 Austria     | Neuroscience |
| 57  | Lab Prague    | 9118 | 🇨🇿 Czech       | Robotics     |
| 58  | Lab Budapest  | 9119 | 🇭🇺 Hungary     | Big Data     |
| 59  | Lab Bucharest | 9120 | 🇷🇴 Romania     | Nano Tech    |
| 60  | Lab Istanbul  | 9121 | 🇹🇷 Turkey      | Trade        |
| 61  | Lab Cairo     | 9122 | 🇪🇬 Egypt       | Archæology   |
| 62  | Lab Jerusalem | 9123 | 🇵🇸 Palestine   | Heritage     |

### **TIER 7: BUSINESS SERVICES (5 services)**
| #   | Service        | Port | Purpose               |
| --- | -------------- | ---- | --------------------- |
| 63  | SaaS API       | 8048 | SaaS signal API       |
| 64  | Marketplace    | 8004 | E-commerce platform   |
| 65  | Economy        | 9093 | Economy engine        |
| 66  | Reporting      | 8001 | Analytics & reporting |
| 67  | Health Monitor | 8099 | System health         |

### **TIER 8: CONTENT & MEDIA (7 services)**
| #   | Service            | Port | Purpose                   |
| --- | ------------------ | ---- | ------------------------- |
| 68  | Excel Core         | 8002 | Excel automation          |
| 69  | Behavioral Science | 8003 | Behavioral analytics      |
| 70  | Advanced Analytics | 8006 | Complex analytics         |
| 71  | NeuroSonix         | 8015 | Brain-computer interfaces |
| 72  | Dr. Albana         | 8040 | Medical content           |
| 73  | Blog Publisher     | 8041 | Blog automation           |
| 74  | Aviation Weather   | 8080 | Aviation data             |

### **TIER 9: INFRASTRUCTURE & HYBRID (3 services)**
| #   | Service      | Port   | Purpose                 |
| --- | ------------ | ------ | ----------------------- |
| 75  | Multi-Tenant | 8007   | Multi-tenancy           |
| 76  | Quantum      | Custom | Quantum computing       |
| 77  | CLX Hybrid   | 8058   | Scanner/Printer gateway |

### **TIER 10: FRONTEND & GATEWAY (7 services)**
| #   | Service         | Port   | Purpose            |
| --- | --------------- | ------ | ------------------ |
| 78  | Backend API     | 8000   | REST API           |
| 79  | Web Frontend    | 3000   | Next.js UI         |
| 80  | User Management | 8070   | Auth + Clerk       |
| 81  | Billing Core    | 8095   | Stripe integration |
| 82  | Blog Paywall    | 8020   | Subscription       |
| 83  | Nginx           | 80/443 | Reverse proxy      |

### **TIER 11: OBSERVABILITY (5+ services)**
| #   | Service    | Port  | Purpose             |
| --- | ---------- | ----- | ------------------- |
| 84  | Prometheus | 9090  | Metrics collection  |
| 85  | Grafana    | 3001  | Dashboards          |
| 86  | Loki       | 3100  | Log aggregation     |
| 87  | Jaeger     | 16686 | Distributed tracing |
| 88  | Tempo      | 3200  | Trace storage       |

### **TIER 12: TELEMETRY & SUPPORT (2 services)**
| #   | Service         | Port | Purpose       |
| --- | --------------- | ---- | ------------- |
| 89  | Agent Telemetry | 8009 | Agent metrics |

---

## 📊 DEPLOYMENT SUMMARY

```
TOTAL CONFIRMED SERVICES: 89
DOCKER-COMPOSE MAIN FILE: docker-compose.75-services.yml
DATABASES: 4 (PostgreSQL, Redis, Neo4j, MinIO)
AI/ML ENGINES: 11+ (Ollama, Ocean, Kloud, Curiosity, etc.)
TRINITY STACK (ASI): 4 (ALBA, ALBI, JONA, ASI)
DISTRIBUTED LABS: 23 (European tech hubs)
GLOBAL DATA SOURCES: 8 (Continental coverage)
FRONTEND & GATEWAY: 7 (Web, API, Auth, Billing)
OBSERVABILITY: 5 (Prometheus, Grafana, Loki, Jaeger, Tempo)
BUSINESS SERVICES: 5+ (Analytics, Marketplace, Economy)
CONTENT & MEDIA: 7+ (Dr. Albana, Blog Publisher, etc.)
```

---

## 🚀 DEPLOYMENT STRATEGY FOR HETZNER CPX62

### **PHASE 1: INFRASTRUCTURE (Estimated: 15 mins)**
```bash
# Setup SSH & system
ssh root@46.62.210.251
cd /opt/clisonix
bash HETZNER_DEPLOY_SETUP.sh
```

### **PHASE 2: CORE SERVICES (Estimated: 10 mins)**
- Start Databases: PostgreSQL, Redis, Neo4j, MinIO
- Start Infrastructure: Docker network setup
- Health check all DB connections

### **PHASE 3: AI ENGINES (Estimated: 30 mins)**
- Ollama + model download
- Ocean Core initialization
- Kloud ecosystem startup
- CLX Agent learning mode

### **PHASE 4: TRINITY STACK (Estimated: 5 mins)**
- ALBA (Analytical Intelligence)
- ALBI (Creative Intelligence)
- JONA (Coordinator)
- ASI (Orchestrator)

### **PHASE 5: DISTRIBUTED LABS & DATA SOURCES (Estimated: 10 mins)**
- 23 Labs parallel startup
- 8 Global DataSources initialization
- Multi-region read-only replicas

### **PHASE 6: BUSINESS SERVICES (Estimated: 10 mins)**
- API layer (all endpoints)
- SaaS orchestrator
- Marketplace + Economy
- Reporting & Analytics

### **PHASE 7: FRONTEND & GATEWAY (Estimated: 5 mins)**
- Next.js Web Frontend
- Nginx reverse proxy
- SSL/TLS setup

### **PHASE 8: OBSERVABILITY (Estimated: 5 mins)**
- Prometheus metrics
- Grafana dashboards
- Jaeger tracing

**Total Deployment Time: ~90 minutes (1.5 hours)**

---

## 🔧 DEPLOYMENT COMMANDS

### **Start All Services (75 microservices):**
```bash
cd /opt/clisonix

# Export environment
export $(cat .env.hetzner | xargs)

# Start all services
docker-compose -f docker-compose.75-services.yml \
  --env-file .env.hetzner \
  up -d

# Watch startup
watch -n 5 'docker-compose -f docker-compose.75-services.yml ps'
```

### **Start Core Services Only (Test Mode):**
```bash
docker-compose -f docker-compose.yml \
  --env-file .env.hetzner \
  up -d
```

### **Health Check All Services:**
```bash
docker-compose -f docker-compose.75-services.yml \
  ps --filter "status=running"

# Or more detailed:
docker ps | grep clisonix | wc -l
```

### **View Service Status:**
```bash
# All services
docker compose -f docker-compose.75-services.yml ps

# Specific service
docker logs clisonix-ocean-core
docker logs clisonix-api
docker logs clisonix-ollama

# Real-time monitoring
docker stats clisonix-api clisonix-ocean-core
```

---

## 📈 RESOURCE ALLOCATION (16 vCPU, 32 GB RAM)

### **By Tier (Recommended):**
```
Infrastructure (5 services)      → 4 vCPU, 8 GB RAM
AI/LLM Engines (11 services)     → 6 vCPU, 12 GB RAM
Trinity Stack (4 services)       → 2 vCPU, 4 GB RAM
Labs & Data Sources (31 services)→ 2 vCPU, 4 GB RAM
Business & Content (12 services) → 1 vCPU, 2 GB RAM
Frontend & Gateway (7 services)  → 1 vCPU, 2 GB RAM
Observability (5 services)       → 0.5 vCPU, 1 GB RAM
Reserve                          → 0.5 vCPU, 1 GB RAM
```

---

## 🔐 SECURITY CHECKLIST

- [ ] Update `.env.hetzner` with production secrets
- [ ] Configure firewall rules (port 80, 443, 8000, 11434)
- [ ] Setup SSL/TLS certificates (Let's Encrypt)
- [ ] Configure Floating IP & DNS records
- [ ] Enable Hetzner backups
- [ ] Setup monitoring alerts
- [ ] Configure PostgreSQL replication
- [ ] Enable Redis persistence (AOF/RDB)
- [ ] Setup rate limiting (API, Ollama)
- [ ] Configure audit logging

---

## 📞 SUPPORT & MONITORING

**Grafana Dashboard:** http://46.62.210.251:3001  
**Prometheus Metrics:** http://46.62.210.251:9090  
**API Status:** http://46.62.210.251:8000/health  
**Jaeger Traces:** http://46.62.210.251:16686  

---

## 🎯 NEXT STEPS

1. **SSH to server** and run deployment script
2. **Configure secrets** in `.env.hetzner`
3. **Start services** with docker-compose
4. **Verify health** of all 75+ microservices
5. **Setup SSL** for production domains
6. **Configure backups** and monitoring
7. **Test API endpoints** and features
8. **Monitor resource usage** with Grafana

---

**Status:** ✅ READY FOR DEPLOYMENT  
**Last Updated:** May 28, 2026  
**Prepared By:** GitHub Copilot + Clisonix Development Team
