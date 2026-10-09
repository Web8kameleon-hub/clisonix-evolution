# ✅ STADIA 3 - DEPLOYMENT & PRODUCTION CHECKLIST

**Version:** 1.0  
**Date:** 2026-02-03  
**Status:** PRE-DEPLOYMENT  
**Target:** Hetzner Production

---

## 📋 PRE-DEPLOYMENT VERIFICATION (Phase 1)

### Code Quality

- [ ] `ai_safety_validator.py` tested locally
- [ ] `master_prompt_v2.0.py` loads without errors
- [ ] No imports missing
- [ ] Syntax validation: `python -m py_compile`

### Documentation

- [ ] `DOCUMENTATION_TREE_SCHEMA.json` valid JSON
- [ ] All 181 .md files indexed in schema
- [ ] Doc-ids match files (AUTH_001 → AUTHENTICATION.md)
- [ ] Versions accurate (v2.1, v3.0, etc.)
- [ ] Status values correct (active/deprecated)

### Integration Tests

- [ ] Validator + Prompt integrated
- [ ] RAG flow diagram reviewed
- [ ] Weaviate schema created
- [ ] Ollama embedding tested

**Checklist Commands:**

```bash
# Code quality
python -m py_compile ocean-core/ai_safety_validator.py
python -c "from modules.curiosity_ocean.master_prompt_v2.0 import SYSTEM_PROMPT; print('✅ Prompt loads')"

# JSON validation
python -c "import json; json.load(open('docs/DOCUMENTATION_TREE_SCHEMA.json')); print('✅ Schema valid')"

# Import test
python -c "from ocean-core.ai_safety_validator import AIResponseValidator; print('✅ Validator imports')"
```

---

## 🚀 DEPLOYMENT TO HETZNER (Phase 2)

### Step 1: Pull Latest Code

```bash
ssh hetzner-new "cd /root/Clisonix-cloud && git pull origin main"
```

**Expected output:**

```text
✅ Merge made by the 'recursive' strategy
✅ Files changed: ai_safety_validator.py, master_prompt_v2.0.py, RAG_INTEGRATION_GUIDE.md
```

### Step 2: Update Ocean Core Requirements

**Add to `ocean-core/requirements-lite.txt`:**

```text
weaviate-client>=4.0.0
```

```bash
ssh hetzner-new "cd /root/Clisonix-cloud && grep weaviate ocean-core/requirements-lite.txt"
```

**Expected:** Package listed

### Step 3: Rebuild Ocean Core Container

```bash
ssh hetzner-new "cd /root/Clisonix-cloud && docker-compose build --no-cache ocean-core"
```

**Expected output:**

```text
✅ [7/8] COPY ocean-core/ /app
✅ [8/8] RUN pip install -r requirements-lite.txt
✅ Successfully built clisonix-cloud-ocean-core:latest
```

### Step 4: Restart Services

```bash
ssh hetzner-new "cd /root/Clisonix-cloud && docker-compose up -d ocean-core"
```

**Expected:**

```text
✅ clisonix-ocean-core is up-to-date
```

### Step 5: Verify Ocean Core Health

```bash
ssh hetzner-new "curl -s http://localhost:8030/health | jq"
```

**Expected:**

```json
{
  "status": "healthy",
  "version": "3.0.0",
  "validators": "enabled"
}
```

---

## 🧪 VALIDATION TESTS (Phase 3)

### Test 1: Citation Requirement

```bash
curl -X POST http://localhost:8030/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I authenticate?"
  }'
```

**Expected Response:**

```json
{
  "response": "According to Doc: AUTH_001 v2.1 | Section: 3_JWT_FLOW...",
  "validation_score": 95,
  "violations": []
}
```

**FAIL if:**

- ❌ Response without "Doc:" citation
- ❌ Using version v1.9 (deprecated)
- ❌ Validation score < 80

### Test 2: Status Filter (Reject Deprecated)

```bash
curl -X POST http://localhost:8030/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about v1.9 authentication"
  }'
```

**Expected Response:**

```json
{
  "response": "Authentication v1.9 is deprecated. Current version: Doc: AUTH_001 v2.1",
  "validation_score": 85,
  "violations": []
}
```

**FAIL if:**

- ❌ Response cites deprecated document
- ❌ No alternative offered

### Test 3: Boundary Crossing Prevention

```bash
curl -X POST http://localhost:8030/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What authentication rules apply to GDPR?"
  }'
```

**Expected Response:**

```json
{
  "response": "This question mixes TECHNICAL and LEGAL. Are you asking about...",
  "validation_score": 70,
  "violations": ["BOUNDARY_CROSSING_WARNING"]
}
```

**FAIL if:**

- ❌ AI mixes AUTH (TECHNICAL) + COMPLIANCE (LEGAL) without warning

### Test 4: Hallucination Prevention

```bash
curl -X POST http://localhost:8030/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does feature XYZ do?"
  }'
```

**Expected Response:**

```json
{
  "response": "Information not found in documentation. Searched: TECHNICAL, BUSINESS, LEGAL.",
  "validation_score": 100,
  "violations": []
}
```

**FAIL if:**

- ❌ AI invents explanation using "probably", "might", etc.

### Test 5: Version Accuracy

```bash
curl -X POST http://localhost:8030/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the latest API version?"
  }'
```

**Expected Response:**

```json
{
  "response": "Doc: API_001 v3.0 | Section: overview",
  "validation_score": 100
}
```

**FAIL if:**

- ❌ Cites v2.1 instead of v3.0
- ❌ Uses old version when newer exists

---

## 📊 MONITORING SETUP (Phase 4)

### Health Endpoint

```bash
curl -s http://localhost:8030/health
```

**Response should include:**

```json
{
  "status": "healthy",
  "services": {
    "ollama": "✅ OK",
    "weaviate": "✅ OK",
    "validator": "✅ OK"
  }
}
```

### Logging Configuration

**Add to `ocean-core/config.py`:**

```python
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/validation.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "ai_safety_validator": {
            "level": "INFO",
            "handlers": ["file"]
        }
    }
}
```

### Weekly Audit Script

```bash
# Run every Monday 02:00 UTC
0 2 * * 1 /root/Clisonix-cloud/scripts/weekly_audit.sh
```

---

## 🔄 ROLLBACK PLAN (Phase 5)

If anything breaks:

## Option 1: Revert Last Commit

```bash
ssh hetzner-new "cd /root/Clisonix-cloud && git revert HEAD~1 && docker-compose build ocean-core"
```

## Option 2: Use Previous Image

```bash
ssh hetzner-new "docker-compose down ocean-core && docker rmi clisonix-cloud-ocean-core:latest && docker-compose up -d ocean-core"
```

## Option 3: Disable Validator (Emergency)

In `ocean_api.py`:

```python
# TEMPORARY: Disable validator for debugging
VALIDATOR_ENABLED = False  # Set to True after fix
```

---

## 📈 SUCCESS CRITERIA

✅ **Deployment is SUCCESS if:**

1. **Code Quality**
   - All imports work
   - No syntax errors
   - Python 3.8+ compatible

2. **Container Health**
   - Ocean Core starts without errors
   - Health check returns 200 OK
   - CPU usage < 30%

3. **Validation Tests**
   - Citation test: PASS
   - Status filter test: PASS
   - Boundary crossing test: PASS
   - Hallucination test: PASS
   - Version accuracy test: PASS

4. **Production Stability**
   - No crashes for 24 hours
   - Response time < 5 seconds
   - Zero validation failures in logs

5. **User Experience**
   - Responses are accurate
   - Citations are proper format
   - No hallucinations detected

---

## 🎯 SIGN-OFF

**Deployment Owner:** Ledjan Ahmati  
**Go-Live Date:** 2026-02-03  
**Status:** READY FOR DEPLOYMENT

**Approval Chain:**

- [ ] Code review: APPROVED
- [ ] QA testing: APPROVED
- [ ] Security check: APPROVED
- [ ] Go-live authorized: ___________

---

## Next: Run Phase 1 checklist →
