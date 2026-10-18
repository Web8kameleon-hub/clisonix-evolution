# Architecture Runtime Wiring Index (Repo → Backend → Module → Routes)

**Qëllimi**
- Dokument “wiring” që lidh **repo/reverse proxy**, **backend services**, **direktori & entry file**, **routes/endpoints**, dhe **orchestrimin** (kush e thërret kë, dhe cili modul e jep shërbimin).
- Ky dokument është **read-friendly** dhe përdor si burim kryesor inventaret ekzistuese:
  - `docs/production/route-destination-map.md` (dhe `.json`) për **routing/rewrites/redirects**
  - `CLISONIX_MODULE_MAP.md` për **module ↔ route/interface ↔ dependencies**
  - `docs/architecture/XLC_RESONANT_READING_MODEL.md` për **AI reading/inspection logic**

> Shënim: `route-destination-map` përmend "destination" (host/port + prefix), por **nuk e përshkruan gjithmonë file-in konkret në backend repo**. Për këtë pjesë, dokumenti ka "drill-down" shembuj konkretë + template.

---

## 📑 INDEKSI

1. [Single Source of Truth (SSOT)](#1-single-source-of-truth-ssot)
2. [Runtime Topology (Orchestrimi)](#2-runtime-topology-orchestrimi-në-1-minutë)
3. [Route Prefix → Backend Mapping](#3-mapping-route-prefix--backend-service-gateway-rewrites)
4. [Module Wiring](#4-module-wiring-module--routeinterface--dependencies)
5. [End-to-End Wiring Lineage](#5-end-to-end-wiring-lineage-shembuj-të-qartë)
6. [XLC Reading Model](#6-ai-reading-model-xlc-si-pjesë-e-module-logic)
7. [Drill-down Template & Shembuj](#7-drill-down-template-dritare--shembuj-konkretë)
8. [Cross-Repo Orchestration (Clisonix + Ultrawebthinkig-v2)](#8-cross-repo-orchestration-clisonix--ultrawebthinkig-v2)
9. ["Who Calls Whom"](#9-who-calls-whom-reverse-dependency-map)
10. [Deployment Git-friendly](#10-deployment-git-friendly-pa-e-prishur-dokumentin)
11. [TODO & Status](#11-todo--status)

---

## 1) Single Source of Truth (SSOT)

- **Routing gateway (Next/app + rewrites):**
  - `docs/production/route-destination-map.md`
  - `docs/production/route-destination-map.json`
- **Module architecture & dependencies:**
  - `CLISONIX_MODULE_MAP.md`
- **Reading model (për pjesën e AI wiring):**
  - `docs/architecture/XLC_RESONANT_READING_MODEL.md`

---

## 2) Runtime Topology (Orchestrimi në 1 minutë)

### 2.1 Web/Gateway path (user → apps/web → backend service)
1. **Browser/User** kërkon `http(s)://<host>/<route>`
2. **apps/web (Next.js)** e trajton si:
   - *app-page* (UI)
   - ose *app-api* (API route)
3. Për disa path-e, gateway bën **rewrite** (reverse-proxy) drejt një **backend service**:
   - `clisonix-api:8000/...`
   - `clisonix-ocean-core:8030/api/v1/...`
4. Backend service e mapon request-in në **modul** (p.sh. `ocean`, `zurich`, `chat`, etj.) sipas route/interface.
5. Moduli thërret shërbime downstream:
   - `ollama` (për Nanogrid/Ocean)
   - ose module të tjera (p.sh. `chat → ocean`)

### 2.2 Diagram (tekst)
```
User
  └─> apps/web (Next: app pages + api routes)
        └─> rewrites (route-destination-map)
              ├─> clisonix-api:8000  -> modules: alba/albi/jona/asi/chat-fallback/etc (varies)
              └─> clisonix-ocean-core:8030 -> modules: ocean/zurich/trinity/debate (via /api/v1/*)

Backend Module
  └─> dependencies (CLISONIX_MODULE_MAP)
        └─> ollama / intelligence-lab / mali/liam/alda/blerina/etc.
```

---

## 3) Mapping “Route Prefix → Backend Service” (Gateway Rewrites)

Ky seksion është i drejtpërdrejtë nga `docs/production/route-destination-map.json` (rewrites).

### 3.1 Rewrites që dërgojnë direkt te `clisonix-ocean-core:8030`
- `/api/debate` → `http://clisonix-ocean-core:8030/api/v1/debate`
- `/api/debate/:path*` → `http://clisonix-ocean-core:8030/api/v1/debate/:path*`
- `/api/debate/stream` → `http://clisonix-ocean-core:8030/api/v1/debate/stream`
- `/api/ocean` → `http://clisonix-ocean-core:8030/api/v1/health`
- `/api/ocean/:path*` → `http://clisonix-ocean-core:8030/api/v1/:path*`
- `/api/ocean/health` → `http://clisonix-ocean-core:8030/health`
- `/api/zurich` → `http://clisonix-ocean-core:8030/api/v1/zurich`
- `/api/zurich/:path*` → `http://clisonix-ocean-core:8030/api/v1/zurich/:path*`
- `/media/ocean/:path*` → `http://clisonix-ocean-core:8030/media/:path*`
- `/videos/ocean/:path*` → `http://clisonix-ocean-core:8030/videos/:path*`

### 3.2 Rewrites që dërgojnë te `clisonix-api:8000`
- `/api/ai/:path*` → `http://clisonix-api:8000/api/ai/:path*`
- `/api/alba/:path*` → `http://clisonix-api:8000/api/alba/:path*`
- `/api/albi/:path*` → `http://clisonix-api:8000/api/albi/:path*`
- `/api/asi-health` → `http://clisonix-api:8000/asi/health`
- `/api/asi-status` → `http://clisonix-api:8000/asi/status`
- `/api/asi/:path*` → `http://clisonix-api:8000/api/asi/:path*`
- `/api/crypto/:path*` → `http://clisonix-api:8000/api/crypto/:path*`
- `/api/docker-containers` → `http://clisonix-api:8000/api/reporting/docker-containers`
- `/api/docker-stats` → `http://clisonix-api:8000/api/reporting/docker-stats`
- `/api/health` → `http://clisonix-api:8000/health`
- `/api/jona/:path*` → `http://clisonix-api:8000/api/jona/:path*`
- `/api/monitoring/:path*` → `http://clisonix-api:8000/api/monitoring/:path*`
- `/api/realdata/:path*` → `http://clisonix-api:8000/api/realdata/:path*`
- `/api/reporting/:path*` → `http://clisonix-api:8000/api/reporting/:path*`
- `/api/security/:path*` → `http://clisonix-api:8000/api/security/:path*`
- `/api/system-metrics` → `http://clisonix-api:8000/api/reporting/system-metrics`
- `/api/system-status` → `http://clisonix-api:8000/api/system-status`
- `/api/system/:path*` → `http://clisonix-api:8000/api/system/:path*`
- `/api/weather/:path*` → `http://clisonix-api:8000/api/weather/:path*`
- `/asi/:path*` → `http://clisonix-api:8000/asi/:path*`
- `/audio/:path*` → `http://clisonix-api:8000/audio/:path*`
- `/backend/:path*` → `http://clisonix-api:8000/:path*`
- `/backend/status` → `http://clisonix-api:8000/health`
- `/files/:path*` → `http://clisonix-api:8000/files/:path*`
- `/health` → `http://clisonix-api:8000/health`
- `/images/:path*` → `http://clisonix-api:8000/images/:path*`
- `/media/:path*` → `http://clisonix-api:8000/media/:path*`
- `/uploads/:path*` → `http://clisonix-api:8000/uploads/:path*`
- `/video/:path*` → `http://clisonix-api:8000/video/:path*`

---

## 4) Module Wiring (Module → Route/Interface → Dependencies)

Kjo pjesë vjen nga `CLISONIX_MODULE_MAP.md`.

### 4.1 Core modules (të lidhura me Ocean)
- `ocean` → `/api/ocean`
- `chat` → `/api/chat`
- `trinity` → `/api/trinity`
- `zurich` → `/api/zurich`

Dependencies (snippet):
- `chat → ocean → ollama`
- `trinity → ocean → ollama`
- `zurich → ocean → ollama`

### 4.2 Specialized modules
- `alba` → `/api/alba`
- `albi` → `/api/albi`
- `jona` → `/api/jona`

### 4.3 Intelligence/content stack
- `klajdi` → `/klajdi/*` (via intelligence-lab)
- `mali` → `/mali/*` (via intelligence-lab)
- `liam` → `/health`, `/api/v1/*` (LIAM service)
- `alda` → `/tables/alda` (via intelligence-lab)
- `blerina` → content generation pipeline (pillar/blog/social)

### 4.4 Edge/bridge services
- `nanogridata-edge` → secure edge ingestion protocol v1 (binary wire format)
- `bridge-engine` → `/signals/publish`, `/signals/process`, `/routes`
- `kloud-bridge` → `/health`, `/status`, `/signals/publish`, `/fabric/sync`
- `ocean-enterprise-api-v1` → `/api/v1/chat`, `/api/v1/chat/stream`

---

## 5) End-to-End “Wiring Lineage” (shembuj të qartë)

> Këtu lidhim **Route → Backend → Modul → Downstream**.

### 5.1 Ocean chat
- **Route (gateway):** `/api/ocean/*`
- **Backend service (rewrite):** `clisonix-ocean-core:8030/api/v1/*`
- **Modul (interface):** `ocean` (nga `CLISONIX_MODULE_MAP.md`: `ocean -> /api/ocean`)
- **Downstream:** `ollama` (nga dependencies: `chat/trinity/zurich → ocean → ollama`)

**TODO (drill-down në file/directory entry):**
- gjej entry/router file në repo për `clisonix-ocean-core` që mapon `/api/v1/*` → handler i modulit `ocean`.

### 5.2 Zurich deep reasoning
- **Route:** `/api/zurich/*`
- **Backend:** `clisonix-ocean-core:8030/api/v1/zurich/*`
- **Modul:** `zurich` → `zurich → ocean → ollama`

**TODO:** file entry për `zurich` handler brenda `clisonix-ocean-core`.

### 5.3 Debate streaming
- **Route:** `/api/debate` + `/api/debate/:path*` + `/api/debate/stream`
- **Backend:** `clisonix-ocean-core:8030/api/v1/debate*`

**TODO:** konfirmim i saktë: a është “debate” pjesë e `trinity`/variant, dhe cila rrugë brenda ocean router e dispatchon.

### 5.4 ALBA audio/video
- **Route:** `/api/alba/*`
- **Backend:** `clisonix-api:8000/api/alba/*`
- **Modul:** `alba -> /api/alba`

**TODO:** entry file brenda `clisonix-api` për `/api/alba`.

### 5.5 ALBI biosignal
- **Route:** `/api/albi/*`
- **Backend:** `clisonix-api:8000/api/albi/*`
- **Modul:** `albi -> /api/albi`
- **Dependencies:** `albi → klajdi`

**TODO:** entry file + ku thirret `klajdi` (router/handler + orchestrim).

---

## 6) AI Reading Model (XLC) si pjesë e “module logic”

Kur një modul përdor engine-n e leximit/inspektimit, referohet dokumenti:
- `docs/architecture/XLC_RESONANT_READING_MODEL.md`

Pikat e implementuara (nga file):
- `LayerBuilder`
- `XLCInspector.inspect` dhe `inspect_scan`
- `XLCCommandMap`
- `XLCResponseWriter`

**Wiring lineage (conceptual):**
- Modul (p.sh. `ocean/zurich/trinity`) → command/pattern handling → `LayerBuilder/Inspector` → `XLCResponseWriter`.

---

## 7) Drill-down Template & Shembuj Konkretë

### 7.1 Template (për ta plotësuar me file + directory + routes exact)

Për çdo modul/endpoint që do të "full map" (repo + directory + file + routes + orchestrim), përdor këtë format:

#### <ModuleName>
- **Repo:** *(clisonix / ultraweb)*
- **Backend service:** *(p.sh. clisonix-api:8000 ose clisonix-ocean-core:8030)*
- **Backend direktori:** `/<path>` *(në repo)*
- **Entry file:** `<file.py / router.ts>` *(entry point me route handlers)*
- **Route(s):**
  - `/<route prefix>` → `<handler function/class>`
  - Handler e dispatchon te module logic
- **Orchestrimi (call chain):**
  - apps/web (Next) → Nginx rewrite → backend service:port → entry file → handler → module → dependencies (ollama/DB/cache)
- **Dependencies (CLISONIX_MODULE_MAP):**
  - `<dependency chain>` *(p.sh. ocean → ollama)*

---

### 7.2 Shembull Konkret: Ocean Chat Module

- **Repo:** `clisonix` (main repo)
- **Backend service:** `clisonix-ocean-core` (port 8030)
- **Backend direktori:** `ocean-core/` (në root)
- **Entry file:** `ocean-core/ocean_core_full.py` ose `main.py` (FastAPI instance)
- **Route(s):**
  - `/api/v1/chat` → FastAPI handler për chat streaming
  - `/api/v1/health` → health check
  - `/api/v1/stream` → SSE streaming endpoint
- **Orchestrimi:**
  ```
  User Browser
    ↓ POST /api/ocean/[...path]
  apps/web (Next) gateway rewrite
    ↓ (rewrite rule: /api/ocean/* → http://clisonix-ocean-core:8030/api/v1/*)
  Nginx reverse proxy
    ↓
  clisonix-ocean-core:8030 (FastAPI instance)
    ↓ /api/v1/chat handler
  ocean module (ocean_core_full.py logic)
    ↓ (CLISONIX_MODULE_MAP: ocean → ollama)
  ollama:11434 (LLM inference)
    ↓ response token stream
  SSE/WebSocket back to user
  ```
- **Dependencies:**
  - `ocean → ollama` (LLM)
  - `ocean → redis` (cache)
  - `ocean → mongodb` (message history)

---

### 7.3 Shembull Konkret: ALBI Biosignal Module

- **Repo:** `clisonix`
- **Backend service:** `clisonix-api` (port 8000)
- **Backend direktori:** `app/` (FastAPI main app)
- **Entry file (approx):** `app/routers/albi.py` ose `app/main.py` (root router)
- **Route(s):**
  - `/api/albi/eeg/process` → EEG processing handler
  - `/api/albi/settings` → ALBI configuration
- **Orchestrimi:**
  ```
  User
    ↓ GET /api/albi/eeg/live
  apps/web rewrite: /api/albi/* → http://clisonix-api:8000/api/albi/*
    ↓
  clisonix-api:8000 FastAPI
    ↓ /api/albi handler
  albi module
    ↓ (CLISONIX_MODULE_MAP: albi → klajdi)
  klajdi intelligence engine (signal/case logic)
    ↓ (klajdi → mali for diagnostics)
  mali service (findings/analysis)
    ↓ response
  back to user
  ```
- **Dependencies:**
  - `albi → klajdi` (signal intelligence)
  - `klajdi → mali` (diagnostics)
  - `mali → liam/alda` (intake/tables)

---

## 8) Cross-Repo Orchestration (Clisonix + Ultrawebthinkig-v2)

### 8.1 Repo Baseline

| Dimen.           | Clisonix (main)                                  | Ultrawebthinkig-v2 (external)     |
| ---------------- | ------------------------------------------------ | --------------------------------- |
| **Repo path**    | root                                             | `external/Ultrawebthinkig-v2/`    |
| **Compose file** | `compose-hosting.yml` (prod)                     | `docker-compose.production.yml`   |
| **Services**     | 198 (full stack)                                 | ~12 (modular)                     |
| **Backend lang** | Python (FastAPI) + TypeScript                    | TypeScript (Next.js) + Node       |
| **Frontend**     | `apps/web` (Next.js)                             | `ultraweb` (Next.js)              |
| **Core service** | `clisonix-api:8000` + `clisonix-ocean-core:8030` | `web8-app:3000` + `joan-asi:8088` |

### 8.2 Cross-Repo Call Chain (kur Clisonix dërgon të Ultrawebthinkig-v2)

```
Clisonix User
  ↓ /api/kloud-bridge/[...path]
Clisonix apps/web (Next)
  ↓ rewrite: /api/kloud-bridge/* → http://clisonix-kloud-bridge:xxxx/*
Clisonix kloud-bridge service (gateway)
  ↓ (CLISONIX_MODULE_MAP: kloud-bridge → external Kloud sovereign runtime)
Ultrawebthinkig-v2 (isolated deployment - www.ultrawebthinking.com)
  ↓ /api/chat OR /api/vision OR /api/system-status
web8-ultra-app:3000 (Next.js app with JOAN ASI embedded)
  ↓ JOAN architecture (Alba/Albi/Jona):
     - Alba: Real-time monitoring (data collection)
     - Albi: Pattern recognition (intelligence)
     - Jona: Love-driven synthesis (ethical oversight)
Response back through kloud-bridge
  ↓ to Clisonix user
```

**Qëllim:** Ultrawebthinkig-v2 është **sovereign XYZ deployment** - thërret direkt `ollama` (internal instance) + internal PostgreSQL/Redis/MongoDB, jo direct-proxied të Clisonix.

### 8.3 Shembull Konkret: Ultrawebthinkig-v2 JOAN Chat Module

- **Repo:** `external/Ultrawebthinkig-v2` (separate deployment)
- **Frontend service:** `web8-ultra-app` (port 3000)
- **Frontend direktori:** `/pages` (Next.js app-dir)
- **Frontend entry:** `pages/app/page.tsx` ose `/pages/layout.tsx` (root layout)
- **Backend direktori:** `/pages/api` (Next.js API routes)
- **Backend entry file:** `pages/api/chat.ts` (JOAN ASI chat endpoint)
- **Route(s):**
  - `POST /api/chat` → JOAN chat completion
  - `GET /api/system-status` → JOAN health check
  - `POST /api/vision` → JOAN vision processing
  - `POST /api/audio` → JOAN audio analysis
- **Orchestrimi (call chain):**
  ```
  Browser (ultrawebthinking.vercel.app)
    ↓ POST /api/chat { message, context }
  web8-app:3000 (Next.js Server)
    ↓ /pages/api/chat.ts handler
  JOAN ASI Engine (embedded logic)
    ├─> Alba (trupi - body): Collects context, session data
    ├─> Albi (shpirti - spirit): Intelligence processing, pattern recognition
    └─> Jona (zemra - heart): Love-driven synthesis, ethical oversight
    ↓ (call to internal ollama if available)
  ollama:11434 (internal or external LLM)
    ↓ response
  Formatted JSON back to frontend
  ```
- **Dependencies:**
  - `JOAN chat → postgres` (session/chat history)
  - `JOAN chat → redis` (cache)
  - `JOAN chat → mongodb` (long-term storage)
  - `JOAN chat → ollama` (LLM inference - optional, may use OpenAI-compatible)
- **Key Files in Ultrawebthinkig-v2:**
  - `pages/api/chat.ts` - Chat completions endpoint
  - `pages/api/vision.ts` - Vision/image analysis
  - `pages/api/system-status.ts` - Health check + metrics
  - `components/JOAN/` - JOAN logic (likely; Alba/Albi/Jona components)
  - `lib/agi/` - AGI core (likely)

---

## 9) "Who Calls Whom" (Reverse Dependency Map)

### 9.1 Tabela: Service Call Dependencies

| Caller (Frontend)  | Path                  | Rewrite Rule                       | Backend Service       | Handler/Module            | Downstream                    |
| ------------------ | --------------------- | ---------------------------------- | --------------------- | ------------------------- | ----------------------------- |
| apps/web           | `/api/ocean/*`        | rewrite to `:8030/api/v1/*`        | clisonix-ocean-core   | ocean                     | ollama                        |
| apps/web           | `/api/debate*`        | rewrite to `:8030/api/v1/debate*`  | clisonix-ocean-core   | trinity/debate            | ollama                        |
| apps/web           | `/api/zurich/*`       | rewrite to `:8030/api/v1/zurich/*` | clisonix-ocean-core   | zurich                    | ollama                        |
| apps/web           | `/api/albi/*`         | rewrite to `:8000/api/albi/*`      | clisonix-api          | albi                      | klajdi, mali                  |
| apps/web           | `/api/alba/*`         | rewrite to `:8000/api/alba/*`      | clisonix-api          | alba                      | recorder/handler              |
| apps/web           | `/api/jona/*`         | rewrite to `:8000/api/jona/*`      | clisonix-api          | jona                      | neural handler                |
| apps/web           | `/api/asi/*`          | rewrite to `:8000/api/asi/*`       | clisonix-api          | asi                       | trinity brain                 |
| apps/web           | `/api/chat`           | direct handler (no rewrite)        | apps/web              | chat (Next route)         | clisonix-ocean-core:8030      |
| apps/web           | `/api/kloud-bridge/*` | rewrite to kloud-bridge            | clisonix-kloud-bridge | kloud-bridge              | Ultrawebthinkig-v2 (isolated) |
| Ultrawebthinkig-v2 | `/api/v1/chat`        | internal (joan-asi)                | joan-asi:8088         | JOAN ASI (Alba/Albi/Jona) | ollama:11434                  |

### 9.2 Dependency Graph (text)
```
clisonix-api:8000
  ├─> alba (audio/video)
  ├─> albi (biosignal)
  │   └─> klajdi (intelligence)
  │       └─> mali (findings)
  │           └─> liam/alda (tables)
  ├─> jona (neural)
  └─> asi (general reasoning)
      └─> trinity

clisonix-ocean-core:8030
  ├─> ocean (conversational)
  │   └─> ollama:11434
  ├─> zurich (deep reasoning)
  │   └─> ollama:11434
  ├─> trinity (debate/multi-perspective)
  │   └─> ollama:11434
  └─> debate (variant)
      └─> ollama:11434

ollama:11434 (shared)
  └─> llama3.1:8b (model)

clisonix-kloud-bridge (gateway)
  └─> Ultrawebthinkig-v2 (isolated sovereign deployment)
      └─> joan-asi:8088 (JOAN ASI: Alba/Albi/Jona)
          └─> ollama:11434 (internal)

redis (cache layer)
  ↑ (shared by all services)

postgres/mongodb (data)
  ↑ (shared storage)
```

---

## 10) Deployment Git-friendly (pa e prishur dokumentin)

### 10.1 Strategjia: Reference Ekzistojnë, Dokumenti Vetëm Link + Drill-down

Ky dokument mban **linkime këmbuese** (referencë) drejt SSOT-ve Ekzistuese:
- `docs/production/route-destination-map.(md|json)` ← **source of truth për routing**
- `CLISONIX_MODULE_MAP.md` ← **source of truth për modul orchestration**
- `docs/architecture/XLC_RESONANT_READING_MODEL.md` ← **source of truth për AI wiring**

**Deployment workflow:**
1. Kur **ndryshon routing** (reverse proxy rewrite):
   - Update `route-destination-map.json` (manual ose generator skript)
   - Sinkronizo seksionin "3) Mapping..." këtu (copy/paste + format)
2. Kur **ndryshon modul architecture** (new service / dependency):
   - Update `CLISONIX_MODULE_MAP.md` (YAML ose JSON)
   - Refresh seksionin "4) Module Wiring..." këtu
3. Kur **shton drill-down konkret**:
   - Add në seksionin "7) Drill-down..." (format standardizuar)
   - Refere për fajllin konkret në repo

### 10.2 Change Log (Çdo Deploy Duhet Rregjistrim)

```markdown
## Change Log

### Deploy [DATE] - [VERSION]
- **Routing Changes:** [path_prefix: from → to ]
- **Service Changes:** [service_name: action (added/removed/updated)]
- **Module Changes:** [module_name : dependency_graph_change]
- **Files Modified:**
  - route-destination-map.json
  - CLISONIX_MODULE_MAP.md
  - This document (sections: 3, 4, 7, 9)
- **Verified:**
  - [ ] Docker Compose syntax (docker-compose config)
  - [ ] Routes reachable (curl tests)
  - [ ] Module endpoints respond (/health)
  - [ ] Downstream services available
```

### 10.3 Audit Checklist para Deployment

- [ ] Updated `route-destination-map.json` (if routing change)
- [ ] Updated `CLISONIX_MODULE_MAP.md` (if modul/dependency change)
- [ ] Updated seksionin 3 (routing mapping) këtu
- [ ] Updated seksionin 4 (modul wiring) këtu
- [ ] Added drill-down në seksionin 7 (if new endpoint)
- [ ] Verified in `docker-compose` (syntax ✓, port conflicts ✗, env vars ✓)
- [ ] Tested rewrite rules (curl ↔ Nginx logs)
- [ ] Tested module endpoints (/health endpoint returns 200)
- [ ] Four-eyes review (kush bën: kush apruvon) - për production

---

## 11) TODO & Status Tracker

### 11.1 Document Maturity Status

| Task                                   | Status | Owner   | Target | Notes                                                                 |
| -------------------------------------- | ------ | ------- | ------ | --------------------------------------------------------------------- |
| Index & navigation                     | ✅ DONE | Copilot | v1.0   | Index with anchors added                                              |
| Template (sec. 7)                      | ✅ DONE | Copilot | v1.0   | Template + 2 concrete examples (Ocean, ALBI)                          |
| Cross-repo section                     | ✅ DONE | Copilot | v1.0   | Clisonix ↔ Ultrawebthinkig-v2 wiring                                  |
| "Who Calls Whom"                       | ✅ DONE | Copilot | v1.0   | Reverse dependency map + call chain table                             |
| Deployment strategy                    | ✅ DONE | Copilot | v1.0   | Git-friendly workflow + change log template                           |
| **File path validation**               | ⏳ TODO | DevOps  | v1.1   | Verify ocean-core entry file, albi router, asi endpoints actual paths |
| **Service healthcheck paths**          | ⏳ TODO | DevOps  | v1.1   | Confirm /health, /status, /api/v1/health endpoint actual paths        |
| **Performance baseline**               | ⏳ TODO | DevOps  | v1.2   | Document latency SLAs (ocean → ollama, albi → klajdi, etc.)           |
| **Troubleshooting section**            | ⏳ TODO | DevOps  | v1.2   | "Route not found? Check...", "Module timeout? Check..."               |
| **Ultrawebthinkig-v2 Full Drill-down** | ⏳ TODO | DevOps  | v1.1   | Add concrete joan-asi entry file + routes + call chain                |
| **One-click deploy companion**         | ⏳ TODO | DevOps  | v2.0   | Generate shell script to validate this doc against live system        |

### 11.2 Known Limitations & Gaps

- **entry file paths:** Dokumenti thotë "ocean-core/ocean_core_full.py" - por nuk e ka verified aktualin exact filenames (main.py? __init__.py?)
- **router structure (clisonix-api):** Dokumenti supozon `app/routers/albi.py` - verify file structure
- **Ultrawebthinkig-v2 detail:** Joan ASI + Ollama integration is documented broadly, not file-by-file drill-down
- **Latency profiling:** No SLA baselines for each call chain (p.sh. user → ocean → ollama latency)
- **Error handling:** Not documented: what happens when ocean → ollama timeout? What does user see?

### 11.3 Validation Scripts (FUTURE — not yet written)

```bash
#!/bin/bash
# validate-wiring-index.sh — verify this document against live system

# Check 1: Docker Compose services exist
docker-compose -f compose-hosting.yml config | grep -E "services:" -A 200 | grep "clisonix-api:" >/dev/null && echo "✅ clisonix-api found"

# Check 2: Routes are reachable
curl -s http://localhost:8000/health | jq .status && echo "✅ clisonix-api:8000 health OK"
curl -s http://localhost:8030/health | jq .status && echo "✅ clisonix-ocean-core:8030 health OK"

# Check 3: Module endpoints respond
curl -s http://localhost:8000/api/albi/settings | jq . && echo "✅ ocean module endpoint works"

# Check 4: Rewrite rules are correct
curl -s -H "X-Forwarded-Proto: https" -H "X-Forwarded-Host: app.example.com" http://localhost:3000/api/ocean/health | jq .status && echo "✅ rewrite rule /api/ocean →  :8030 works"

# Output: [PASSED|FAILED] + summary
```

### 11.4 Next Steps (Production Readiness)

1. **Week 1:**
   - [ ] File path validation (confirm entry files, routers in both repos)
   - [ ] Healthcheck endpoint audit (test each /health path)
   - [ ] Add Ultrawebthinkig-v2 drill-down concrete example

2. **Week 2:**
   - [ ] Latency baselines (benchmark ocean → ollama, albi → klajdi chains)
   - [ ] Error scenarios (document timeout/500/404 handling per module)
   - [ ] Troubleshooting guide (decision tree for common issues)

3. **Week 3+:**
   - [ ] Write validation script (shell/Python to verify doc vs. live system)
   - [ ] Integrate into CI/CD (run validation on every docker-compose change)
   - [ ] Generate "deploy checklist" pull-request template
  - dhe seksioni “Module Wiring” rishikohet.

---

## 9) Gjendja aktuale (Status)
- ✅ Repo-level routing → backend service është i mbuluar (nga route-destination-map rewrites)
- ✅ Module → route/interface + dependencies është i mbuluar (nga CLISONIX_MODULE_MAP)
- ⚠️ Drill-down “direktori + file entry handler” për `clisonix-api` dhe `clisonix-ocean-core` është ende TODO derisa të bëhet search në code.

