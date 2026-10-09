# Google Firestore - Clisonix Service Registry Setup

## Overview
Clisonix now uses **Google Firestore** instead of Redis for service registry. 
- **Cost**: Free tier covers service registry completely (50,000 reads/day, 20,000 writes/day)
- **No infrastructure**: Managed by Google
- **Real-time**: Services query dynamically, no hardcoding needed

---

## Setup Steps

### 1. Create Google Cloud Project

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

gcloud init  # login to Google account
gcloud projects create clisonix-registry
gcloud config set project clisonix-registry
```

### 2. Enable Firestore API

```bash
gcloud services enable firestore.googleapis.com
```

### 3. Create Firestore Database

```bash
gcloud firestore databases create --region=us-central1
```

Or via console: https://console.firebase.google.com/ → Create project → Enable Firestore

### 4. Generate Service Account Key

Option A: **Firebase Console** (Recommended)
1. Go to https://console.firebase.google.com/
2. Select your Google Cloud project
3. Settings → Service Accounts → Generate New Private Key
4. Save as `firebase-key.json`

Option B: **Google Cloud Console**
1. Go to https://console.cloud.google.com/
2. Select your project
3. IAM & Admin → Service Accounts → Create Service Account
4. Grant roles: `Cloud Datastore Owner`, `Cloud Firestore Service Agent`
5. Create Key (JSON)
6. Save as `firebase-key.json`

### 5. Set Environment Variables

**Development** (local):
```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS = "$(Get-Location)\firebase-key.json"

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="./firebase-key.json"
```

**Production** (deployment):
```bash
# Deploy the key securely (GitHub Secrets, Azure Key Vault, etc.)
# Set environment variable in deployment platform
```

### 6. Install Firebase SDK

```bash
pip install firebase-admin
```

Add to `requirements.txt`:
```
firebase-admin>=6.1.0
```

### 7. Verify Setup

```bash
# Test connection
python -c "
from services.registry import ServiceRegistry
import asyncio

async def test():
    reg = ServiceRegistry()
    success = await reg.register_service(
        name='test-service',
        port=8888,
        capabilities=['test']
    )
    print('✅ Firestore connection successful!' if success else '❌ Failed')

asyncio.run(test())
"
```

---

## How It Works

### Service Registration (Automatic)

When Ocean Core starts:
```python
# ocean-core/ocean_api.py startup
registry = await init_registry()  # Uses GOOGLE_APPLICATION_CREDENTIALS
await registry.register_service(
    name="ocean-core",
    port=8030,
    capabilities=["nlp-generation", "multilingual", "reasoning", "knowledge-synthesis"]
)
await registry.start_heartbeat()  # Refresh every 30s
```

### Service Discovery (Dynamic)

Frontend queries:
```typescript
// apps/web/lib/service-resolver.ts
const url = await resolver.resolve("nlp-generation");
// Queries /api/service-discovery → Firestore → Returns http://localhost:8030
```

### Firestore Structure

```
services/ (collection)
├── ocean-core (document)
│   ├── name: "ocean-core"
│   ├── url: "http://localhost:8030"
│   ├── capabilities: ["nlp-generation", "multilingual", "reasoning", "knowledge-synthesis"]
│   ├── registered_at: "2026-02-16T10:30:00.000Z"
│   ├── expires_at: "2026-02-16T11:30:00.000Z"
│   └── ttl_seconds: 3600
├── backend-api
│   └── ...
└── ...
```

---

## Firestore Free Tier Limits

**Daily Quotas:**
- Read operations: **50,000**
- Write operations: **20,000**
- Delete operations: Included in write limit

**Storage:**
- 1 GB free storage
- 50,000 documents free (approximate)

**Sufficient for:**
- Service registry (5-10 services, ~10/min heartbeats)
- Demo/testing
- Production with <1000 services

---

## Deployment Checklist

- [ ] Google Cloud project created
- [ ] Firestore database enabled (us-central1)
- [ ] Service account key generated (`firebase-key.json`)
- [ ] `firebase-admin` installed in requirements.txt
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` set in deployment environment
- [ ] Ocean Core auto-registers on startup
- [ ] Frontend queries resolve services dynamically
- [ ] `/api/v1/status` returns `"backend": "google-firestore"`

---

## Troubleshooting

### ❌ "GOOGLE_APPLICATION_CREDENTIALS not set"
```bash
# Set the environment variable and restart your service
$env:GOOGLE_APPLICATION_CREDENTIALS = "./firebase-key.json"
python ocean_api.py
```

### ❌ "Firebase initialization failed"
- Verify `firebase-key.json` path and permissions
- Check service account has Firestore permissions
- Run: `gcloud auth list` (confirm logged-in)

### ❌ Services not showing up in Firestore
- Check `services.registry` logs for heartbeat messages
- Verify Firestore database exists in us-central1
- Check network connectivity to Google Cloud

### ❌ Performance slow (high latency)
- Firestore may need time to optimize (24-48 hours)
- Add client-side caching in `service-resolver.ts` (already 30-second TTL)
- Consider Firestore indexes if queries are complex

---

## Local Development (No Google Cloud)

If you want to test locally without Firestore:

```python
# services/registry.py - Already has fallback
# Services register to in-memory storage automatically
registry = ServiceRegistry()
await registry.register_service(...)  # Uses local_services dict
```

All functionality works the same way (except persistence across restarts).

---

## Production Scaling

For 100+ services:
- Consider **Firestore collections** per service type (better organization)
- Implement **service load balancing** (round-robin providers per capability)
- Set up **Cloud Monitoring** for registry health
- Enable **Firestore backups** (daily snapshots)

---

## Next Steps

1. ✅ Firestore setup complete
2. Register other services (ALBA, ALBI, JONA, API)
3. Remove hardcoded URLs from all 69 APIs
4. Deploy to production

---

**Questions?** Check `services/registry.py` and `ocean-core/ocean_api.py` for examples.
