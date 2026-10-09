import json
import time
import urllib.request

base = "http://localhost:8030"

# Test 1: status
r = urllib.request.urlopen(f"{base}/api/v1/status", timeout=10)
print("STATUS:", json.loads(r.read()).get("status"))

# Test 2: chat
payload = json.dumps({"message": "kush je ti", "enable_companion": True}).encode()
req = urllib.request.Request(
    f"{base}/api/v1/chat",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
t0 = time.time()
try:
    r = urllib.request.urlopen(req, timeout=45)
    data = json.loads(r.read())
    print("CHAT keys:", list(data.keys()))
    print("RESPONSE:", str(data.get("response", data.get("reply", "")))[:300])
    print(f"Time: {time.time()-t0:.1f}s")
except Exception as e:
    print(f"CHAT ERROR after {time.time()-t0:.1f}s: {e}")
