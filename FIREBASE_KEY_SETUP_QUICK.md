# Firebase Key Setup - Your Project

**Your Project:**
- Project ID: `project-646a8f33-9071-4ebc-b24`
- Project Number: `484895499087`
- Email: `mailabagmbh@gmail.com`

---

## Step 1: Enable Firestore API

1. Go to: https://console.cloud.google.com/apis/library/firestore.googleapis.com
2. Click **ENABLE**
3. Wait 30 seconds for activation

---

## Step 2: Create Firestore Database

1. Go to: https://console.firebase.google.com/
2. Click **Add Project** → Select existing Google Cloud project → `project-646a8f33-9071-4ebc-b24`
3. Continue through setup
4. **Firestore Database** → Create database
5. Location: `us-central1` (or closest to you)
6. Mode: **Start in production mode** ✓

---

## Step 3: Create Service Account & Get Key

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **CREATE SERVICE ACCOUNT**
3. Name: `clisonix-registry`
4. Click **CREATE AND CONTINUE**
5. **Grant roles:**
   - Add role: `Cloud Datastore Owner` ✓
   - Add role: `Cloud Firestore Service Agent` ✓
   - Add role: `Firebase Rules Administrator` (optional)
6. Click **CONTINUE** → **DONE**

---

## Step 4: Generate JSON Key

1. Click on service account: `clisonix-registry@project-...`
2. Go to **KEYS** tab
3. **Add Key** → **Create new key** → JSON
4. Auto-downloads `project-646a8f33-9071-4ebc-b24-xxxxx.json`
5. Rename to: `firebase-key.json`
6. Move to: `c:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json`

---

## Step 5: Set Environment Variable

**Windows PowerShell:**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json"

# Verify
$env:GOOGLE_APPLICATION_CREDENTIALS
# Should show: C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json
```

**Or add to PowerShell profile:**
```powershell
# Edit $PROFILE
notepad $PROFILE

# Add this line:
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json"

# Save and reload PowerShell
```

---

## Step 6: Test Connection

```bash
cd c:\Users\Admin\Desktop\Clisonix-cloud

# Install Firebase (if not already)
pip install firebase-admin

# Test
python -c "
from services.registry import ServiceRegistry
import asyncio

async def test():
    reg = ServiceRegistry()
    success = await reg.register_service(
        name='test-service',
        port=9999,
        capabilities=['test']
    )
    print('✅ Firestore connected!' if success else '❌ Failed')

asyncio.run(test())
"
```

---

## Step 7: Start Ocean Core (Auto-Registration)

```bash
cd c:\Users\Admin\Desktop\Clisonix-cloud\ocean-core
python ocean_api.py
```

**Expected output:**
```
✅ Firebase initialized from credentials
✅ Ocean Core registered in Google Firestore
💓 Heartbeat started for ocean-core (interval=30s)
```

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### ❌ "GOOGLE_APPLICATION_CREDENTIALS not set"
```powershell
# Check it's set
$env:GOOGLE_APPLICATION_CREDENTIALS

# Set it
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json"

# Restart Python/Ocean
```

### ❌ "Permission denied" on firebase-key.json
- Right-click file → Properties → Security → Run as Administrator
- Or move to different location and retry

### ❌ "Firestore not found in project"
- You skipped Step 1 or Step 2
- Go to https://console.firebase.google.com/ and enable Firestore

---

## Check Firestore Data

1. Go to: https://console.firebase.google.com/
2. Select your project
3. **Firestore Database** → **Data**
4. Should see `services` collection with your registered services

---

**Next:** Start Ocean Core, then test the registry with:
```bash
curl -X POST http://localhost:8000/api/v1/service-discovery \
  -H "Content-Type: application/json" \
  -d "{\"capability\": \"nlp-generation\"}"
```

Should return Ocean Core's URL.
