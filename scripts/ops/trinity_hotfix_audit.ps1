param(
    [string]$HostAlias = "hetzner-neu",
    [int]$LoadRequests = 120,
    [switch]$RunQueueProbe
)

$ErrorActionPreference = "Stop"

function Invoke-Remote([string]$Command) {
    ssh -o BatchMode=yes -o ConnectTimeout=10 $HostAlias $Command
}

Write-Host "=== Trinity Hotfix Audit ($HostAlias) ==="

Write-Host "[1/6] Service baseline"
Invoke-Remote "cd /root/Clisonix-cloud && docker compose ps jona api redis postgres ocean-core reporting"

Write-Host "[2/6] JONA + API + Signals"
Invoke-Remote "curl -fsS http://localhost:7777/health && echo"
Invoke-Remote "curl -fsS http://localhost:8000/api/asi/jona/metrics && echo"
Invoke-Remote "curl -fsS http://localhost:8030/api/v1/signals/status && echo"

Write-Host "[3/6] Idle CPU top containers"
Invoke-Remote "docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}' | sort -t'|' -k2 -r | head -n 20"

if ($RunQueueProbe) {
    Write-Host "[4/6] Queue probe (no destructive clear endpoint exists)"
    Invoke-Remote "curl -fsS http://localhost:8030/api/v1/signals/recent?limit=20 && echo"
}

Write-Host "[5/6] Load test against JONA status endpoint"
Invoke-Remote "python3 - << 'PY'
import requests, time
N = $LoadRequests
url = 'http://localhost:7777/status'
ok = 0
start = time.time()
for _ in range(N):
    try:
        r = requests.get(url, timeout=2)
        ok += 1 if r.status_code == 200 else 0
    except Exception:
        pass
elapsed = time.time() - start
print({'requests': N, 'ok': ok, 'elapsed_s': round(elapsed,2), 'rps': round(N/max(elapsed,0.001),2)})
PY"

Write-Host "[6/6] Post-load health"
Invoke-Remote "curl -fsS http://localhost:7777/health && echo"
Invoke-Remote "curl -fsS http://localhost:8000/api/asi/jona/metrics && echo"

Write-Host "=== Audit complete ==="
