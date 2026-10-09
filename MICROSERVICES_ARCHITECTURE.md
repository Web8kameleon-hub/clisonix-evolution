# 🚀 CLISONIX CLOUD MICROSERVICES ARCHITECTURE

## Përmbledhje

Arkitekturë e plotë me **50+ containers** Docker, pa konflikte portash.

## 🏗️ Arkitektura

...
┌────────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASES & CACHE                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐                      │
│  │ Postgres │  │  Redis   │  │  Neo4j   │  │ VictoriaMetrics│                      │
│  │  :5432   │  │  :6379   │  │ :7474    │  │    :8428       │                      │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘                      │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                         ASI TRINITY (Super Intelligence)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│  │  ALBA    │  │  ALBI    │  │  JONA    │  │   ASI    │                            │
│  │  :5555   │  │  :6666   │  │  :7777   │  │  :9094   │                            │
│  │ Collector│  │ Learner  │  │ Sandbox  │  │ Combined │                            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                            │
│       └─────────────┴─────────────┴─────────────┘                                  │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                          OCEAN CORE + INTELLIGENCE                                  │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Ocean Core  │  │  AGIEM   │  │ Personas │  │ Blerina  │  │Alba IDLE │          │
│  │    :8030     │  │  :9300   │  │  :9200   │  │  :8035   │  │  :8031   │          │
│  │  61 Layers   │  │ Manager  │  │14 Experts│  │ Doc Intel│  │Status Chat│         │
│  └──────────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                       DATA SOURCES (7 Regions - 5000+ Sources)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  Europe  │ │ Americas │ │Asia+China│ │India+SA  │ │Africa+ME │ │ Oceania  │    │
│  │  :9301   │ │  :9302   │ │  :9303   │ │  :9304   │ │  :9305   │ │  :9306   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                          23 LABORATORIES (City-Named)                               │
│  Albania (7): Elbasan│Tirana│Durrës│Vlorë│Shkodër│Korçë│Sarandë                   │
│  Kosovo (1): Prishtina                                                              │
│  N.Macedonia (1): Kostur                                                            │
│  Greece (1): Athens                                                                 │
│  Italy (1): Rome                                                                    │
│  Switzerland (1): Zurich                                                            │
│  Serbia (1): Beograd                                                                │
│  Bulgaria (1): Sofia                                                                │
│  Croatia (1): Zagreb                                                                │
│  Slovenia (1): Ljubljana                                                            │
│  Austria (1): Vienna                                                                │
│  Czech (1): Prague                                                                  │
│  Hungary (1): Budapest                                                              │
│  Romania (1): Bucharest                                                             │
│  Turkey (1): Istanbul                                                               │
│  Egypt (1): Cairo                                                                   │
│  Palestine (1): Jerusalem                                                           │
│  Ports: 9101-9123                                                                   │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                            SaaS & SERVICES                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│  │SaaS API  │ │Marketplace│ │Reporting │ │  Excel   │ │Behavioral│                 │
│  │  :8040   │ │  :8004   │ │  :8001   │ │  :8002   │ │  :8003   │                  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                            │
│  │ Economy  │ │ Aviation │ │API+Web   │                                            │
│  │  :9093   │ │  :8080   │ │:8000+3000│                                            │
│  └──────────┘ └──────────┘ └──────────┘                                            │
└────────────────────────────────────────────────────────────────────────────────────┘
...

## 📦 Lista e Plotë e Containers (50+)

### Databases (4)

| Container | Port | Funksioni |
| --------- | ---- | --------- |
| postgres | 5432 | PostgreSQL 16 Database |
| redis | 6379 | Redis 7 Cache |
| neo4j | 7474/7687 | Graph Database |
| victoriametrics | 8428 | Time-series Database |

### ASI Trinity (4)

| Container | Port | Funksioni |
| --------- | ---- | --------- |
| alba | 5555 | Data Collector & Signal Processing |
| albi | 6666 | Adaptive Learning & Analytics |
| jona | 7777 | Sandbox & Synthesis Coordinator |
| asi | 9094 | Artificial Super Intelligence |

### Core Intelligence (5)

| Container | Port | Funksioni |
| --------- | ---- | --------- |
| ocean-core | 8030 | 61 Alphabet Layers + Binary Algebra |
| agiem | 9300 | AGI Ecosystem Manager |
| personas | 9200 | 14 Specialist Personas |
| blerina | 8035 | Document Intelligence |
| alba-idle | 8031 | Technical Status Chat |

### Data Sources (7)

| Container | Port | Region | Sources |
| --------- | ---- | ------ | ------- |
| datasource-europe | 9301 | Europe | 1600+ |
| datasource-americas | 9302 | Americas | 800+ |
| datasource-asia-china | 9303 | Asia+China | 1400+ |
| datasource-india-south-asia | 9304 | India+SA | 800+ |
| datasource-africa-middle-east | 9305 | Africa+ME | 500+ |
| datasource-oceania-pacific | 9306 | Oceania | 300+ |
| datasource-central-asia | 9307 | Central Asia | 200+ |

### 23 Laboratories (9101-9123)

| Container | Port | City | Type |
| --------- | ---- | ---- | ---- |
| lab-elbasan | 9101 | Elbasan, Albania | AI |
| lab-tirana | 9102 | Tirana, Albania | Medical |
| lab-durres | 9103 | Durrës, Albania | IoT |
| lab-vlore | 9104 | Vlorë, Albania | Environmental |
| lab-shkoder | 9105 | Shkodër, Albania | Marine |
| lab-korce | 9106 | Korçë, Albania | Agricultural |
| lab-saranda | 9107 | Sarandë, Albania | Underwater |
| lab-prishtina | 9108 | Prishtina, Kosovo | Security |
| lab-kostur | 9109 | Kostur, N.Macedonia | Energy |
| lab-athens | 9110 | Athens, Greece | Academic |
| lab-rome | 9111 | Rome, Italy | Architecture |
| lab-zurich | 9112 | Zurich, Switzerland | Finance |
| lab-beograd | 9113 | Beograd, Serbia | Industrial |
| lab-sofia | 9114 | Sofia, Bulgaria | Chemistry |
| lab-zagreb | 9115 | Zagreb, Croatia | Biotech |
| lab-ljubljana | 9116 | Ljubljana, Slovenia | Quantum |
| lab-vienna | 9117 | Vienna, Austria | Neuroscience |
| lab-prague | 9118 | Prague, Czech | Robotics |
| lab-budapest | 9119 | Budapest, Hungary | Data |
| lab-bucharest | 9120 | Bucharest, Romania | Nanotechnology |
| lab-istanbul | 9121 | Istanbul, Turkey | Trade |
| lab-cairo | 9122 | Cairo, Egypt | Archeology |
| lab-jerusalem | 9123 | Jerusalem, Palestine | Heritage |

### SaaS & Services (9)

| Container | Port | Funksioni |
| --------- | ---- | --------- |
| saas-api | 8040 | Production SaaS API |
| marketplace | 8004 | API Keys & Billing |
| reporting | 8001 | Reports Generation |
| excel | 8002 | Excel Processing |
| behavioral | 8003 | Behavioral Science |
| economy | 9093 | Economy & Billing |
| aviation | 8080 | Aviation Weather |
| api | 8000 | API Gateway |
| web | 3000 | Frontend |

## 🚀 Si të Nisësh

### Start të Gjitha (50+ containers)

```powershell
.\START-MICROSERVICES.ps1
```

### Start vetëm Core

```powershell
.\START-MICROSERVICES.ps1 -Profile core
```

### Start vetëm Labs

```powershell
.\START-MICROSERVICES.ps1 -Profile labs
```

### Start një shërbim specifik

```powershell
.\START-MICROSERVICES.ps1 -Service alba
```

### Kontrollo Status

```powershell
.\START-MICROSERVICES.ps1 -Status
```

### Ndalo të Gjitha

```powershell
.\START-MICROSERVICES.ps1 -Stop
```

### Shiko Logs

```powershell
.\START-MICROSERVICES.ps1 -Logs -Service ocean-core
```

## 🔧 Komandat Docker Compose

```bash
# Start all
docker-compose -f docker-compose.microservices.yml up -d

# Status
docker-compose -f docker-compose.microservices.yml ps

# Logs
docker-compose -f docker-compose.microservices.yml logs -f <service>

# Stop
docker-compose -f docker-compose.microservices.yml down

# Rebuild
docker-compose -f docker-compose.microservices.yml build --parallel
```

## 📊 14 Personas

1. **medical_science** - Health, Brain, Biology
2. **lora_iot** - Sensors, Devices, Networks
3. **security** - Security, Crypto, Vulnerability
4. **systems_architecture** - API, Infrastructure
5. **natural_science** - Physics, Energy, Quantum
6. **industrial_process** - Production, Cycles
7. **agi_analyst** - AGI, Cognitive, Consciousness
8. **business_analyst** - Revenue, Strategy, Growth
9. **smart_human** - Understanding, Help, Explain
10. **academic** - Research, Theory, Study
11. **media** - News, Story, Report
12. **culture** - Tradition, Art, Society
13. **hobby** - Hobby, Learn, Practice
14. **entertainment** - Movie, Game, Music

## 🌍 Data Sources (5000+ Free Open Sources)

| Region | Countries | Sources |
| ------ | --------- | ------- |
| Europe | 39 | 1600+ |
| Americas | 44 | 800+ |
| Asia + China | 15 | 1400+ |
| India + South Asia | 8 | 800+ |
| Africa + Middle East | 60 | 500+ |
| Oceania + Pacific | 25 | 300+ |
| Central Asia | 8 | 200+ |
| **TOTAL** | **200+** | **5000+** |

## ⚠️ Kërkesat

- Docker Desktop >= 4.0
- 16GB RAM (rekomanduar 32GB)
- 50GB disk space
- Windows 10/11 ose Linux

## 🐛 Troubleshooting

### Container nuk nis

```powershell
# Shiko logs
docker-compose -f docker-compose.microservices.yml logs <service>

# Restart
docker-compose -f docker-compose.microservices.yml restart <service>
```

### Port konflikt

```powershell
# Gjej procesin që përdor portin
netstat -ano | Select-String ":<port>"

# Kill procesin
Stop-Process -Id <PID> -Force
```

### Memory issues

```powershell
# Rritem limitet Docker
# Docker Desktop > Settings > Resources > Memory
```

## 📝 Shënime

- Çdo container është i pavarur
- Mund të rinis vetëm containerin me error
- Nuk ka nevojë të rindërtosh gjithë projektin
- Logs ruhen në Docker volumes

---

**Clisonix Cloud Team** - 2026
