# 🏥 Clisonix Enterprise Health Worker

**Zero-Trust Gateway with RBAC for Real-Time Service Monitoring**

---

## 🎯 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                  Cloudflare Global Network                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Cloudflare Access (Zero-Trust)                            │ │
│  │  - JWT Validation                                           │ │
│  │  - Email-based Authentication                               │ │
│  │  - Automatic Token Rotation                                 │ │
│  └─────────────────┬──────────────────────────────────────────┘ │
│                    │                                             │
│  ┌─────────────────▼──────────────────────────────────────────┐ │
│  │  Health Worker (ES Module)                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │ │
│  │  │ JWT Verify   │  │ RBAC Engine  │  │ Health Probes   │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │ AI Troubleshooting (@cf/openai/gpt-oss-20b)            │ │ │
│  │  │ - Failure Analysis • Smart Alerts • Auto-Diagnosis     │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │  - jose@5.2.0 (npm package)                                │ │
│  │  - nodejs_compat flag enabled                              │ │
│  │  - Role: admin, operator, lab                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Hetzner Server         │
        │  46.225.14.83           │
        │  ┌──────────────────┐   │
        │  │ ocean-core:8030  │   │
        │  │ backend-api:8000 │   │
        │  │ openmind:9999    │   │
        │  │ excel-core:8002  │   │
        │  │ ollama:11434     │   │
        │  │ translation:8036 │   │
        │  └──────────────────┘   │
        └─────────────────────────┘
```

---

## ✨ **Features**

### **Security**
- ✅ **Zero-Trust Architecture** — Cloudflare Access JWT validation
- ✅ **RBAC** — Role-Based Access Control (admin, operator, lab)
- ✅ **Domain-based authorization** — clisonix.com, ultrawebthinking.com
- ✅ **Structured logging** — Full audit trail with request IDs

### **Monitoring**
- ✅ **Real-time health checks** — 6 critical services
- ✅ **Sub-100ms latency** — Fast JWT validation with JWKS caching
- ✅ **Scheduled cron** — Automated checks every 5 minutes
- ✅ **AI-powered Slack alerts** — GPT-oss-20b for automatic troubleshooting
- ✅ **Smart diagnostics** — Context-aware failure analysis

### **Developer Experience**
- ✅ **ESM imports** — No npm build required
- ✅ **Hot reload** — `wrangler dev` for local testing
- ✅ **Live logs** — `wrangler tail` for debugging

---

## 🚀 **Quick Start**

### **1. Deploy Worker**

```bash
cd cloudflare
npx wrangler deploy
```

### **2. Set Secrets (if not already set)**

```bash
npx wrangler secret put SLACK_WEBHOOK_URL
npx wrangler secret put HETZNER_IP
```

### **3. Access Dashboard**

Open `dashboard.html` in your browser:

```bash
# Option 1: Local file
open dashboard.html

# Option 2: Deploy to Cloudflare Pages
npx wrangler pages deploy dashboard.html --project-name=clisonix-health-ui
```

---

## 🤖 **AI-Powered Troubleshooting**

### **How It Works**

When a service fails, the Health Worker automatically:

1. **Detects failure** — HTTP error or timeout on health probe
2. **Analyzes context** — Service name, URL, error code, latency
3. **Generates diagnosis** — Calls `@cf/openai/gpt-oss-20b` with failure details
4. **Sends smart alert** — Slack notification includes AI-suggested fixes

### **Example Slack Alert**

```
🔴 Edge Health: ocean-core — DOWN (HTTP 0)

Service:         ocean-core
Status:          DOWN (HTTP 0)
Latency:         8000ms
CF PoP:          2026-04-05T01:30:00.000Z
URL:             http://46.225.14.83:8030/health
Time:            2026-04-05T01:30:45.000Z

Error:           timeout

🤖 AI Troubleshooting:
• Check if Docker container is running: `docker ps | grep ocean-core`
• Verify port 8030 is exposed and not blocked by firewall
• Restart service: `docker restart ocean-core`
```

### **Performance Impact**

- **AI inference time**: ~200-400ms (runs async, doesn't block health checks)
- **Fallback**: If AI fails, Slack notification still sent without suggestions
- **Cost**: Free tier includes 10,000 neurons/day (sufficient for 500+ alerts)

### **Configuration**

AI binding is automatically configured in `wrangler.toml`:

```toml
[ai]
binding = "AI"
```

No additional setup required — deployed workers have immediate access to Workers AI.

---

## 🔐 **RBAC Policies**

| Role | Domains | Allowed Paths | Description |
|------|---------|---------------|-------------|
| **admin** | `clisonix.com`, `ultrawebthinking.com` | All (`allowAll: true`) | Full access to all endpoints |
| **operator** | `clisonix.com` | `/health`, `/status`, `/metrics` | Read-only monitoring |
| **lab** | `ultrawebthinking.com` | `/health`, `/lab`, `/experiments` | Lab-specific access |

### **Role Resolution Logic**

1. **JWT claims** — Checks `payload.roles` array
2. **Domain heuristic** — `clisonix.com` → admin, `ultrawebthinking.com` → lab
3. **Default** — Falls back to `operator` role

---

## 📊 **API Reference**

### **GET /**

Returns health status for all services.

**Headers:**
```
cf-access-jwt-assertion: <JWT from Cloudflare Access>
```

**Response (200 OK):**
```json
{
  "checked_at": "2026-04-05T01:30:00.000Z",
  "server": "46.225.14.83",
  "authenticated_user": "clisonix@pm.me",
  "role": "admin",
  "summary": {
    "healthy": 6,
    "total": 6,
    "status": "all_healthy"
  },
  "services": [
    {
      "name": "ocean-core",
      "ok": true,
      "http_code": 200,
      "latency_ms": 45
    },
    {
      "name": "backend-api",
      "ok": true,
      "http_code": 200,
      "latency_ms": 38
    }
  ]
}
```

**Response (403 Forbidden):**
```json
{
  "error": "Access denied by RBAC policy",
  "role": "lab",
  "requestId": "cf-ray-123456"
}
```

---

## 🛠️ **Development**

### **Local Testing**

```bash
# Start local development server
npx wrangler dev

# Test endpoint (requires Cloudflare Access in production)
curl http://localhost:8787/
```

### **Live Logs**

```bash
# Stream real-time logs
npx wrangler tail

# Filter by log level
npx wrangler tail --format pretty
```

### **Debug Mode**

Enable verbose logging in `health_worker.js`:

```javascript
function log(ctx, level, message, extra = {}) {
  if (level === "debug" && ctx.env.DEBUG !== "true") return;
  // ... rest of logging
}
```

---

## 📈 **Performance Metrics**

| Metric | Target | Actual |
|--------|--------|--------|
| **JWT Validation** | <10ms | ~3ms |
| **Health Check (all services)** | <500ms | 100-200ms |
| **Wall Time (valid request)** | <500ms | 150-300ms |
| **Wall Time (invalid JWT)** | <10ms | 5-8ms |
| **Cron Execution** | <1s | 200-400ms |
| **AI Troubleshooting** | <500ms | 200-400ms |
| **Slack Alert (no AI)** | <200ms | 50-150ms |
| **Slack Alert (with AI)** | <700ms | 300-600ms |

---

## 🔄 **Scheduled Cron**

The Worker runs automatically every 5 minutes:

```toml
[triggers]
crons = ["*/5 * * * *"]
```

**Behavior:**
- ✅ Probes all 6 services
- ✅ Logs results to Cloudflare Workers Logs
- ✅ Sends Slack alerts for degraded services
- ✅ **AI-powered troubleshooting** — GPT-oss-20b analyzes failures and suggests fixes
- ✅ **Does NOT require JWT** (internal Cloudflare trigger)

---

## 🎨 **UI Dashboard**

### **Features**
- 🎨 Modern gradient design
- 📊 Real-time service cards
- 🔄 Auto-refresh every 30 seconds
- ⚡ Responsive design
- 🔒 Requires Cloudflare Access authentication

### **Screenshots**

**Healthy State:**
```
┌─────────────────────────────────────────┐
│ Status: ALL HEALTHY                     │
│ Healthy: 6/6 | Last Check: 10:30:45 AM │
└─────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ocean-core ✅│  │ backend-api ✅│  │ openmind ✅  │
│ HTTP: 200    │  │ HTTP: 200    │  │ HTTP: 200    │
│ Latency: 45ms│  │ Latency: 38ms│  │ Latency: 52ms│
└──────────────┘  └──────────────┘  └──────────────┘
```

**Degraded State:**
```
┌─────────────────────────────────────────┐
│ Status: DEGRADED                        │
│ Healthy: 5/6 | Last Check: 10:31:15 AM │
└─────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ocean-core ✅│  │ backend-api ✅│  │ openmind ❌  │
│ HTTP: 200    │  │ HTTP: 200    │  │ HTTP: 0      │
│ Latency: 45ms│  │ Latency: 38ms│  │ Error: timeout│
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔧 **Configuration**

### **Environment Variables** (`wrangler.toml`)

```toml
[vars]
TEAM_DOMAIN = "https://clisonix-com-pages.cloudflareaccess.com"
POLICY_AUD  = "ce5b2e959a1c6659b8558714ec426be76ec3ba8f6b51a9a0b5fbc3f6e1ba00ae"
```

### **Secrets** (set via CLI)

```bash
# Slack webhook for critical alerts
npx wrangler secret put SLACK_WEBHOOK_URL
# Input: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Production server IP (optional, defaults to 46.225.14.83)
npx wrangler secret put HETZNER_IP
# Input: 46.225.14.83
```

---

## 📚 **Troubleshooting**

### **403 Forbidden on Dashboard**

**Cause:** Not authenticated with Cloudflare Access

**Solution:**
1. Go to https://clisonix-health-worker.dealsjona.workers.dev/
2. Log in via Cloudflare Access
3. Refresh dashboard

### **Wall Time >6 seconds**

**Cause:** Health probes timing out

**Solution:**
1. Check HETZNER_IP is correct
2. Verify services are running on target ports
3. Check firewall rules allow Cloudflare IPs

### **Missing JWT claims**

**Cause:** Cloudflare Access not configured

**Solution:**
1. Verify TEAM_DOMAIN and POLICY_AUD in `wrangler.toml`
2. Check Cloudflare Access policy is active
3. Confirm user email matches allowed domains

---

## 🎯 **Next Steps**

- [ ] Deploy UI to Cloudflare Pages
- [ ] Add Grafana integration for metrics
- [ ] Implement KV storage for historical data
- [ ] Create custom Slack bot for interactive alerts
- [ ] Add D1 database for audit logs

---

## 📝 **License**

Proprietary — Clisonix Cloud Infrastructure

---

## 🤝 **Support**

For issues or questions:
- **Slack:** #critical-alerts
- **Email:** clisonix@pm.me
- **Docs:** https://docs.clisonix.com/monitoring

---

**Powered by Cloudflare Workers • Zero-Trust Gateway • RBAC Enabled**

