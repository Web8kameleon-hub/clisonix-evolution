# 📋 CLISONIX OFFICE SCRIPTS

## 🗂️ Struktura e Kolonave në Excel

| Kolona | Index | Emri | Përshkrimi |
|--------|-------|------|------------|
| A | 0 | Row_ID | Numri i rreshtit |
| B | 1 | Folder | Folder në Postman |
| C | 2 | Method | GET, POST, PUT, DELETE |
| **D** | **3** | **Endpoint** | URL e API (lexohet) |
| E | 4 | Përshkrimi | Emri i request-it |
| **F** | **5** | **Status_Testimi** | ✅/❌ (shkruhet) |
| G | 6 | Autentikimi | OAuth2, JWT, API Key |
| H | 7 | Dokumentacioni | ✅ Full Docs |
| I | 8 | Monitorimi | Prometheus, Grafana |
| J | 9 | Siguria | SSL/TLS, Pen Test |
| K | 10 | Versioni_API | v1.0, v2.0 |
| L | 11 | Data_Publikimit | DD/MM/YYYY |
| M | 12 | Owner | Ekipi përgjegjës |
| N | 13 | Status_Publikimi | Ready, Pending |
| O | 14 | Komente | Shënime |
| P | 15 | cURL | Command cURL |
| Q | 16 | Python_Snippet | Kod Python |
| **R** | **17** | **Response_Sample** | (shkruhet) |
| **S** | **18** | **Last_Check** | Timestamp (shkruhet) |

---

## 📜 Scripts

### 1. UpdateStatusFromAPI.ts
**Qëllimi:** Kontrollon të gjitha endpoints dhe përditëson statusin.

**Si ta përdorësh:**
1. Hap Excel Online
2. Kliko `Automate` → `New Script`
3. Paste kodin nga `UpdateStatusFromAPI.ts`
4. Kliko `Run`

**Variablat që duhet të ndryshosh:**
```typescript
const BASE_URL = "https://api.clisonix.com";  // Ndryshoje me URL-në tënde
const TOKEN = "YOUR_API_TOKEN";                // Vendos token-in
```

### 2. PowerAutomateConnector.ts
**Qëllimi:** Integrim me Power Automate për HTTP requests të vërteta.

**Flow në Power Automate:**
1. **Trigger:** Recurrence (çdo 5 minuta)
2. **Action:** Run Office Script → merr listën e endpoints
3. **Loop:** Për çdo endpoint:
   - HTTP Action → thirr API
   - Run Office Script → shkruan rezultatin

---

## 🔧 Konfigurimi

### Në Excel:
- Sheet-i duhet të quhet: `API_Endpoints`
- Endpoints fillojnë nga rreshti 2 (rreshti 1 = headers)
- Kolonat duhet të jenë në renditjen e dhënë

### Në Power Automate:
```
Trigger: Recurrence
  ↓
Run script: PowerAutomateConnector.ts
  ↓
Apply to each: endpoints
  ↓
  HTTP: GET/POST endpoint
  ↓
  Run script: updateResult()
```

---

## 📊 Rezultatet

Script-i shkruan:
- **F (Status_Testimi):** `✅ Unit Test` ose `❌ Failed`
- **R (Response_Sample):** JSON response
- **S (Last_Check):** Timestamp i kontrollit

---

## ⚠️ Kufizime

1. **Excel Scripts** nuk mbështet `fetch()` direkt për external URLs
2. Përdor **Power Automate** për HTTP requests të vërteta
3. Ose përdor **Python in Excel** me `=PY()` formulas

---

## 🚀 Quick Start

```bash
# Gjenero Excel template
python production_ready_template.py

# Hap Excel
# Automate → New Script → Paste kod
# Run
```
