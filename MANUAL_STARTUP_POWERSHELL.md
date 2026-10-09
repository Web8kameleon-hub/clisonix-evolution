# 🚀 Manual Service Startup Guide (PowerShell)

Instead of using the automated orchestrator, start each service manually in PowerShell so you can see errors clearly.

## Step 1: Activate Virtual Environment

Open **PowerShell** in the Clisonix-cloud directory:

```powershell
cd C:\Users\Admin\Desktop\Clisonix-cloud
.\.venv\Scripts\Activate.ps1
```

## Step 2: Open 5 Separate PowerShell Windows

You'll need 5 PowerShell windows open (or use VS Code terminals). In each one, make sure to:
1. `cd C:\Users\Admin\Desktop\Clisonix-cloud`
2. `.\.venv\Scripts\Activate.ps1` to activate venv

## Step 3: Start Each Service

### Window 1: Ocean Core (Port 8030)

```powershell
cd ocean-core
python ocean_api.py
```

**Expected Output:**
```
🌊 Starting Curiosity Ocean on port 8030...
INFO:     Uvicorn running on http://0.0.0.0:8030
INFO:     Application startup complete
```

### Window 2: Backend API (Port 8000)

```powershell
cd apps/api
python -m uvicorn main:app --port 8000 --host 0.0.0.0
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
✅ backend-api registered in Google Firestore
```

### Window 3: ALBA (Port 5555)

```powershell
python alba_service_5555.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:5555
INFO:     Application startup complete
✅ alba registered in Google Firestore
```

### Window 4: ALBI (Port 6680)

```powershell
python albi_service_6680.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:6680
INFO:     Application startup complete
✅ albi registered in Google Firestore
```

### Window 5: JONA (Port 7777)

```powershell
python jona_service_7777.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:7777
INFO:     Application startup complete
✅ jona registered in Google Firestore
```

---

## Step 4: Verify All Services Are Running

Open a **6th PowerShell window** (or use a terminal in VS Code) and run:

```powershell
# Test each service's health endpoint
curl http://localhost:5555/health
curl http://localhost:6680/health
curl http://localhost:7777/health
curl http://localhost:8000/health
curl http://localhost:8030/health
```

**Expected Output:**
```json
{"status":"ok"}
```

---

## Step 5: Run Test Suite

In another terminal:

```powershell
python test_firestore_discovery_e2e.py
```

**Or run the automated orchestrator** (now fixed):

```powershell
python orchestrate_discovery_tests.py
```

---

## Troubleshooting

### Service won't start?

Check the error message in that PowerShell window. Common issues:

1. **Port already in use:**
   ```powershell
   # Find what's using the port
   netstat -ano | findstr :5555  # (replace 5555 with your port)
   ```

2. **Missing dependencies:**
   ```powershell
   pip install -r requirements.txt
   # or specific service requirements
   ```

3. **Working directory wrong:**
   - Make sure you're in the right directory before running the command
   - Ocean Core must be run from `ocean-core/` subdirectory
   - Backend API must be run from `apps/api/` subdirectory
   - Other services from root directory

4. **Import errors:**
   - Check that `services/registry.py` exists
   - Check that all imports can be resolved

### Services registered but tests still fail?

Check if Firestore is accessible:
- Services should log "registered in Google Firestore" after startup
- If they log "Service Registry unavailable", that's OK - they fall back to local
- Check Google Cloud credentials if using Firestore

### Can't see logging output?

Make sure logging level is set correctly. Check the top of each service file:
```python
logging.basicConfig(level=logging.INFO)
```

---

## Killing All Services

When done testing, press `Ctrl+C` in each PowerShell window to stop the service.

Or use this to kill all Python processes:

```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Or more targeted:
Stop-Process -Name python -Force
```

---

## Next Steps After Services Start

1. **Verify health endpoints:**
   ```powershell
   curl http://localhost:8000/api/v1/services
   ```

2. **Test discovery:**
   ```powershell
   curl -X POST http://localhost:8000/api/v1/service-discovery `
     -ContentType "application/json" `
     -Body '{"capability":"neural-processing"}'
   ```

3. **Run full test suite:**
   ```powershell
   python test_firestore_discovery_e2e.py
   ```

---

## Using the Diagnostic Tool

If services won't start, run the diagnostic:

```powershell
python diagnose_service_startup.py
```

This will test each service individually and show you exactly what's failing.

