# 🚀 Clisonix AI Agents - Complete Integration & Testing Guide

**Date:** December 10, 2025  
**Status:** Production-Ready  
**Version:** 1.0

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Thunder Client Testing](#thunder-client-testing)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Dashboard](#grafana-dashboard)
5. [Testing Procedures](#testing-procedures)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

Primary local workflow: Thunder Client + Kitchen + Excel Core.
Postman collection is optional/public only and not required for operation.

### Prerequisites
```bash
# Services already running:
✅ Frontend: http://localhost:3000
✅ Backend: http://localhost:8000
⚠️  Prometheus: http://localhost:9090 (Docker optional)
⚠️  Grafana: http://localhost:3001 (Docker optional)
```

### Files Available
```
📄 POSTMAN_AI_AGENTS_COLLECTION.json       - Optional public API testing collection
📄 prometheus-ai-agents.yml                - Prometheus config
📄 GRAFANA_AI_AGENTS_DASHBOARD.json        - Dashboard
📄 AI_AGENT_FRAMEWORKS.md                  - Documentation
📄 N8N_WORKFLOWS.json                      - n8n templates
```

---

## 🔧 Thunder Client Testing (Primary)

### Step 1: Open Thunder Client
```
1. Open Thunder Client in VS Code
2. Use existing local requests/collection
3. Set base URL to http://localhost:8000
4. Run requests directly
```

### Step 2: Set Environment Variables
```
1. Open Thunder Client environments
2. Create/select: "Clisonix Local"
3. Add variable:
  - base_url: http://localhost:8000
4. No paid AI key required

### Optional: Public Postman Collection
```
POSTMAN_AI_AGENTS_COLLECTION.json is kept for public sharing/import,
but local development/testing is not dependent on Postman.
```
```

### Step 3: Test Each Endpoint

#### Group 1: AI Agent Frameworks
```
✓ GET  /api/ai/agents-status
  - Description: Check which frameworks are available
  - Expected: 200 OK with frameworks status
  
✓ POST /api/ai/trinity-analysis
  - Body: {"query": "...", "detailed": true}
  - Description: Full CrewAI analysis (ALBA→ALBI→JONA)
  - Expected: 200 OK with analysis results
  
✓ POST /api/ai/curiosity-ocean
  - Body: {"question": "...", "conversation_id": "..."}
  - Description: Multi-turn LangChain conversation
  - Expected: 200 OK with response + conversation_id
  
✓ POST /api/ai/quick-interpret
  - Body: {"query": "...", "context": "..."}
  - Description: Fast Claude interpretation
  - Expected: 200 OK with interpretation
```

#### Group 2: Real Data
```
✓ GET /api/asi/status
  - Real Prometheus metrics for ALBA, ALBI, JONA
  
✓ GET /api/external/crypto
  - CoinGecko real cryptocurrency prices
  
✓ GET /api/external/weather
  - Open-Meteo real weather data
```

#### Group 3: Local Neural Analysis
```
✓ POST /api/ai/analyze-neural
  - Local neural analysis (no paid key)
  
✓ POST /api/ai/eeg-interpretation
  - Local EEG interpretation
  
✓ GET /api/ai/health
  - Check local AI engine status
```

---

## 📊 Prometheus Setup

### Option 1: Using Docker (Recommended)
```bash
cd C:\clisonix-cloud
docker-compose -f docker-compose.yml up prometheus -d
```

### Option 2: Manual Setup
```bash
# 1. Download Prometheus from: https://prometheus.io/download/
# 2. Copy configuration
copy prometheus-ai-agents.yml C:\prometheus\prometheus.yml

# 3. Start Prometheus
C:\prometheus\prometheus.exe --config.file=prometheus.yml

# 4. Access at http://localhost:9090
```

### Prometheus Queries for Testing
```promql
# AI Agent Status
up{job="ai-agents"}

# CrewAI Tasks
rate(crewai_tasks_completed_total[5m])

# LangChain Chains
rate(langchain_chains_executed_total[5m])

# API Response Time
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# ALBA Network Connections
alba_network_connections

# ALBI EEG Analysis
albi_eeg_alpha_band

# JONA Synthesis Confidence
jona_synthesis_confidence_score
```

---

## 📈 Grafana Dashboard

### Step 1: Add Prometheus Data Source
```
1. Grafana: http://localhost:3001
2. Default login: admin / admin
3. Settings → Data Sources → Add Prometheus
4. URL: http://localhost:9090
5. Click "Save & Test"
```

### Step 2: Import AI Agents Dashboard
```
1. Click "+" (Create)
2. Select "Import"
3. Paste: GRAFANA_AI_AGENTS_DASHBOARD.json
4. Select Prometheus data source
5. Click "Import"
```

### Step 3: View Dashboards
```
✓ Panel 1: AI Agent Frameworks Status
✓ Panel 2: CrewAI Agent Activity
✓ Panel 3: LangChain Conversations
✓ Panel 4: Claude API Requests
✓ Panel 5: API Response Times
✓ Panel 6: ALBA Network Metrics
✓ Panel 7: ALBI EEG Frequency Bands
✓ Panel 8: JONA Neural Synthesis
✓ Panel 9: Local AI Engine Status
✓ Panel 10: Error Rates by Component
```

---

## 🧪 Testing Procedures

### Test 1: Basic Agent Status
```bash
# Terminal Command
curl -X GET http://localhost:8000/api/ai/agents-status

# Expected Response
{
  "timestamp": "2025-12-10T...",
  "frameworks": {
    "crewai": {"available": true/false, "agents": ["alba", "albi", "jona"]},
    "langchain": {"available": true/false},
    "claude_tools": {"available": true}
  }
}
```

### Test 2: CrewAI Trinity Analysis
```bash
curl -X POST http://localhost:8000/api/ai/trinity-analysis \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze system performance", "detailed": true}'

# Expected: Coordinated analysis from 3 agents
```

### Test 3: LangChain Conversation Chain
```bash
# First message
curl -X POST http://localhost:8000/api/ai/curiosity-ocean \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is consciousness?",
    "conversation_id": "conv-001"
  }'

# Follow-up (same conversation_id)
curl -X POST http://localhost:8000/api/ai/curiosity-ocean \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does it relate to information?",
    "conversation_id": "conv-001"
  }'

# Expected: Both responses, with context preserved
```

### Test 4: Real Data Endpoints
```bash
# Crypto prices
curl http://localhost:8000/api/external/crypto

# Weather
curl http://localhost:8000/api/external/weather

# ASI Trinity status (Prometheus-backed)
curl http://localhost:8000/api/asi/status

# Expected: Real data from external APIs + Prometheus
```

### Test 5: Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/ai/agents-status

# Using wrk (if installed)
wrk -t4 -c100 -d30s http://localhost:8000/api/ai/agents-status
```

---

## 📊 Performance Benchmarks

### Expected Response Times
```
/api/ai/agents-status        ~50ms    (status check)
/api/ai/quick-interpret      ~500ms   (Claude API)
/api/ai/analyze-neural       ~1000ms  (local AI call)
/api/ai/trinity-analysis     ~3000ms  (Multi-agent orchestration)
/api/ai/curiosity-ocean      ~1500ms  (LangChain reasoning)
```

### Expected CPU/Memory
```
Backend (idle):      ~5-10% CPU, 100-150 MB RAM
CrewAI (active):     ~20-30% CPU, 200-300 MB RAM
LangChain (active):  ~10-15% CPU, 150-200 MB RAM
Claude Tools:        ~5-10% CPU, 100-150 MB RAM
```

---

## 🐛 Troubleshooting

### Issue: "CrewAI not available"
**Solution:**
```bash
pip install crewai langchain
# Restart backend: npm run dev
```

### Issue: "AI engine unavailable"
**Solution:**
```bash
# Restart backend
npm run dev
```

### Issue: "Prometheus connection refused"
**Solution:**
```bash
# This is OK - Prometheus is optional for AI agents
# AI endpoints work without Prometheus
# To enable: docker-compose up prometheus -d
```

### Issue: "Timeout on /api/ai/trinity-analysis"
**Solution:**
```
# CrewAI takes time for multi-agent coordination
# Normal: 2-5 seconds
# If longer: Check local model/container resources
```

### Issue: "Grafana dashboard not showing data"
**Solution:**
```
1. Check Prometheus is running: http://localhost:9090
2. Verify data source URL: http://localhost:9090
3. Run test query: up{job="ai-agents"}
4. Check metric names match dashboard
```

---

## 🔗 Integration Checklist

- [ ] **Postman Collection Imported**
  - [ ] All 15 endpoints visible
  - [ ] Environment variables set
  - [ ] Can execute GET /api/ai/agents-status

- [ ] **Prometheus Setup Complete**
  - [ ] Running on http://localhost:9090
  - [ ] Configuration file: prometheus-ai-agents.yml
  - [ ] Backend metrics accessible: http://localhost:8000/metrics

- [ ] **Grafana Dashboard Imported**
  - [ ] Data source: Prometheus connected
  - [ ] Dashboard visible at: http://localhost:3001/d/clisonix-ai-agents
  - [ ] All 10 panels displaying data

- [ ] **API Testing Complete**
  - [ ] [x] CrewAI Trinity Analysis working
  - [ ] [x] LangChain Curiosity Ocean working
  - [ ] [x] Claude Tools Quick Interpret working
  - [ ] [x] Real data endpoints (Crypto, Weather) working
  - [ ] [x] Local AI integration configured

- [ ] **Documentation Ready**
  - [ ] This integration guide
  - [ ] AI_AGENT_FRAMEWORKS.md
  - [ ] N8N_WORKFLOWS.json
  - [ ] POSTMAN_AI_AGENTS_COLLECTION.json

---

## 📚 Additional Resources

### Framework Documentation
- **CrewAI**: https://github.com/joaomdmoura/crewai
- **LangChain**: https://python.langchain.com
- **Claude Tools**: https://docs.anthropic.com

### Testing Tools
- **Postman**: https://www.postman.com
- **Prometheus**: https://prometheus.io
- **Grafana**: https://grafana.com

### Clisonix Documentation
- **AI Frameworks**: AI_AGENT_FRAMEWORKS.md
- **n8n Workflows**: N8N_WORKFLOWS.json
- **Real Data API**: API_DOCS.md

---

## 🎯 Next Steps

1. **Immediate (Today)**
   - Import Postman collection
   - Test all 5 AI endpoints
   - Verify real data endpoints work

2. **Short-term (This Week)**
   - Set up Prometheus + Grafana
   - Import Grafana dashboard
  - Configure local AI runtime
   - Deploy n8n workflows

3. **Medium-term (This Month)**
   - Fine-tune agent prompts
   - Optimize response times
   - Set up alerting
   - Document custom workflows

4. **Long-term (Production)**
   - Deploy to cloud infrastructure
   - Set up monitoring/alerting
   - Implement rate limiting
   - Scale with load balancing

---

**Document Version:** 1.0  
**Last Updated:** December 10, 2025  
**Status:** ✅ Production-Ready
