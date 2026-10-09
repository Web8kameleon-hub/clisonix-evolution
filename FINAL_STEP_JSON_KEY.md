# Generate Firebase Key - Final Step

Your service account is ready:
```
clisonix-registry@project-646a8f33-9071-4ebc-b24.iam.gserviceaccount.com
```

---

## Generate JSON Key (5 minutes)

### Option A: Google Cloud Console (Recommended)

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Find: `clisonix-registry@project-646a8f33-9071-4ebc-b24.iam.gserviceaccount.com`
3. Click on it
4. Go to **KEYS** tab
5. Click **ADD KEY** → **Create new key**
6. Select **JSON** format
7. Click **CREATE**
8. Auto-downloads: `project-646a8f33-9071-4ebc-b24-xxxxx.json`

### Option B: Firebase Console

1. Go to: https://console.firebase.google.com/
2. Select: **My First Project**
3. Settings (⚙️) → **Service Accounts** tab
4. Click **Generate New Private Key**
5. Auto-downloads JSON file

---

## Save the Key

1. Locate downloaded file (usually: `C:\Users\Admin\Downloads\`)
2. Rename to: `firebase-key.json`
3. Move to: `C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json`

---

## Set Environment Variable

Open PowerShell and run:

```powershell
cd c:\Users\Admin\Desktop\Clisonix-cloud

# Set the environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json"

# Verify
echo $env:GOOGLE_APPLICATION_CREDENTIALS
# Output: C:\Users\Admin\Desktop\Clisonix-cloud\firebase-key.json
```

---

## Test Connection

```powershell
# Install Firebase SDK
pip install firebase-admin

# Test
python -c "
from services.registry import ServiceRegistry
import asyncio

async def test():
    reg = ServiceRegistry()
    print('✅ Firebase initialized successfully!')

asyncio.run(test())
"
```

**Expected output:** `✅ Firebase initialized successfully!`

---

## Start Ocean Core (Auto-Registers to Firestore)

```powershell
cd ocean-core
python ocean_api.py
```

**Expected logs:**
```
✅ Firebase initialized from credentials
✅ Ocean Core registered in Google Firestore
💓 Heartbeat started for ocean-core (interval=30s)
[OCEAN] Server running on http://localhost:8030
```

---

## Verify Registration

Check Firestore console:
1. Go to: https://console.firebase.google.com/
2. Select: **My First Project**
3. Click: **Firestore Database**
4. Go to: **Data** tab
5. Should see: `services` collection with `ocean-core` document

---

**You're almost there!** Just download the JSON key (2 min) and you're done. 🚀
