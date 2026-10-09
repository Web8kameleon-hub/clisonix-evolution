# ⛔ NO FAKE DATA POLICY — CLISONIX CLOUD

## E NDALUAR RREPTËSISHT

Ky projekt analizon **trurin e njeriut, EEG-në, audioin, shëndetin mendor dhe biologjik**.  
Dhënia e të dhënave të rreme për një sistem të tillë është e papranueshme dhe e rrezikshme.

---

## RREGULLA ABSOLUTE — PA PËRJASHTIME

### 1. NO FAKE DATA

```
❌ NDALOHET gjithçka e tipit:
   - fake data / mock data
   - placeholder responses
   - fallback tokens / instant tokens
   - "Analyzing your request..." (para se AI të ketë përgjigjur)
   - "Po e analizoj pyetjen..." (fallback i rremë)
   - hardcoded demo values
   - simulated results
   - random-generated health scores
   - dummy EEG readings
   - synthetic audio analysis
```

### 2. NO DATA = NO DATA

...

✅ RREGULLI I VETËM I PRANUESHËM:
   Nëse nuk ka të dhëna reale → kthe përgjigje të sinqertë:
   - { "result": null, "reason": "no data available"}
   - { "error": "model not responding" }
   - HTTP 503 / 204 / ngarko gabimin real

   ASNJËHERË mos plotëso boshllëkun me të dhëna të shpikura.

...

### 3. STREAMING — ZERO FALLBACK TOKENS

...
❌ NDALOHET:
   - Çdo yield/emit para se modeli të ketë kthyer token real
   - "Analyzing..." / "Please wait..." si token i parë i rremë
   - asyncio.wait_for me timeout për fake first-token
   - STREAM_FALLBACK_ENABLED = True
   - _build_fast_first_token_fallback() ose çdo funksion i ngjashëm

✅ LEJOHET:
   - Pritja reale e modelit (pa timeout fals)
   - Kthimi i gabimit real nëse modeli nuk përgjigjet
   - HTTP streaming vetëm me tokene reale nga AI
```

### 4. ERRORS TË VËRTETË — JO "SUCCESS" FALS

```
❌ NDALOHET:
   - return {"status": "ok"} kur operacioni ka dështuar
   - HTTP 200 me gabim të fshehur brenda JSON
   - try/except që gëlltit gabimin dhe kthen sukses fals
   - "healthy": True kur shërbimi nuk është i lidhur me bazën e të dhënave

✅ KORREKT:
   - HTTP 404  → resursi nuk ekziston
   - HTTP 503  → shërbimi i varur nuk përgjigjet
   - HTTP 500  → gabim i brendshëm real me stack trace në log
   - HTTP 422  → input i pavlefshëm
   Asnjëherë mos fshi gabimin — loge-o dhe kthe kodin e saktë HTTP.
```

### 5. API KEYS — ASNJËHERË HARDCODED

```
❌ NDALOHET:
   - api_key = "sk-abc123..."  (direkt në kod)
   - token = "Bearer xyz..."  (direkt në kod)
   - password = "admin123"    (direkt në kod)
   - Çdo kredencial i vendosur direkt në skedarë .py / .ts / .js

✅ KORREKT:
   - api_key = os.environ.get("MY_API_KEY")  → nëse None → raise / 503
   - Kredencialet vetëm në .env ose GitHub Secrets
   - .env asnjëherë nuk commit-ohet (shiko .gitignore)
```

### 6. HEALTH CHECKS — TESTIM REAL I VARËSIVE

```
❌ NDALOHET:
   - /health që kthen {"status":"healthy"} pa testuar asnjë varësi
   - Health check që nuk kontrollon: DB, Redis, modelin AI
   - Ping vetëm të vetvetes (localhost loopback pa kuptim)

✅ KORREKT:
   - Health check kontrollon: lidhjen me DB, Redis ping, model reachability
   - Nëse ndonjë varësi dështon → {"status":"degraded"} ose 503
   - Docker healthcheck: CMD curl -f http://localhost:PORT/health
```

---

## DOMAINS QË MBROHEN

| Domain | Pse është kritike |
|---|---|
| EEG / Brain Analysis | Të dhëna të rreme = diagnoza e gabuar |
| Audio Health Analysis | Mock = interpretim i rremë shëndetësor |
| Mental Health AI (ALBI/ALBA) | Fake responses = rrezik për përdoruesin |
| Curiosity Ocean Chat | Placeholder = humbje e besimit |
| Shopping Therapy Engine | Demo products = përvojë e rreme |
| Kloud / ASI Metrics | Fake telemetry = vendime të gabuara |

---

## PËR ZHVILLUESIT — CHECKLIST PARA ÇDO COMMIT

Kontrollo para se të commit-osh:

- [ ] A ka ndonjë `fallback` që kthen string statik kur modeli nuk përgjigjet?
- [ ] A ka ndonjë `mock` ose `dummy` ose `placeholder` në output të API-t?
- [ ] A ka ndonjë `hardcoded` vlerë që simulon rezultat real?
- [ ] A ka ndonjë `wait_for` + fake emit para token-it real?
- [ ] A ka ndonjë funksion si `build_fast_first_token_fallback`?
- [ ] A ka ndonjë HTTP 200 që fsheh gabim të brendshëm?
- [ ] A ka ndonjë API key / password / token hardcoded direkt në kod?
- [ ] A ka ndonjë `/health` endpoint që nuk teston varësitë reale (DB / Redis / model)?

**Nëse NJERI nga këto është po → mos commit. Fix it first.**

---

## PËR AI AGENTS / COPILOT

> **PARALAJMËRIM PËR COPILOT DHE ÇDO AI AGENT NË KËTË REPO:**
>
> Ky projekt ka të ndaluara absolute:
>
> - Mos gjenero asnjë funksion `mock_*`, `fake_*`, `fallback_*`, `placeholder_*`
> - Mos gjenero fallback streaming tokens
> - Mos shto `"demo"`, `"sample"`, `"example"` data në endpoint-et e prodhimit
> - Nëse nuk di si ta zbatosh pa fake data → pyet, mos supozoj
>
> **NO DATA = NO DATA. Kjo nuk është dobësi. Është integritet.**

---

## SHEMBUJ KONKRETË

### GABIM ❌

```python
async def stream_response():
    # Emit fake first token for UX
    yield "Analyzing your request..."
    async for token in real_model_stream():
        yield token
```

```python
def get_eeg_score(session_id):
    if not data:
        return {"score": 72, "status": "normal"}  # FAKE
```

```typescript
const result = data ?? { analysis: "Processing...", confidence: 0.85 }; // FAKE
```

### KORREKT ✅

```python
async def stream_response():
    async for token in real_model_stream():
        yield token
    # Nëse modeli nuk kthen asgjë → raise HTTPException(503)
```

```python
def get_eeg_score(session_id):
    if not data:
        return None  # ose raise 404 / 204
```

```typescript
if (!data) return Response.json({ error: "no data" }, { status: 503 });
```

---

## REFERENCA

Ky policy zbatohet në të gjitha shërbimet:
`ocean-core` · `alba` · `albi` · `asi` · `kloud` · `shopping-therapy` · `matia` · `jona` · `api` · `web`

**Çdo PR që shkel këtë policy do të refuzohet.**

---

*Shkruar: Prill 2026 — Clisonix Cloud Engineering*  
*"Një projekt që analizon trurin e njeriut nuk ka të drejtë të gënjejë."*
