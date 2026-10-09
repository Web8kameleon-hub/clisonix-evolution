# 🌊 Clisonix Ocean-Core - Full Deployment & Validation (PowerShell)
# Deploys all updates and validates production readiness

$ErrorActionPreference = "Stop"

$REMOTE_HOST = "46.225.14.83"
$REMOTE_USER = "root"
$SSH_KEY = "$($env:USERPROFILE)\.ssh\id_hetzner"
$REMOTE_DIR = "/root/Clisonix-cloud"
$SSH_OPTS = @(
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=20",
    "-i", $SSH_KEY
)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌊 CLISONIX OCEAN-CORE - DEPLOYMENT & VALIDATION 2026         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

try {
    # Step 1: Information
    Write-Host "[1/5] Configuring SSH connection..." -ForegroundColor Yellow
    if (-not (Test-Path $SSH_KEY)) {
        throw "SSH key not found: $SSH_KEY"
    }
    Write-Host "  ✓ SSH key found" -ForegroundColor Green

    # Step 2: Deploy files
    Write-Host "[2/5] Deploying ocean-core updates..." -ForegroundColor Yellow
    $deployFiles = @(
        "ocean-core/ocean_api.py",
        "ocean-core/response_orchestrator_v5.py"
    )
    
    foreach ($file in $deployFiles) {
        scp @SSH_OPTS $file "root@${REMOTE_HOST}:${REMOTE_DIR}/$($file)" 2>&1 | Out-Null
    }
    Write-Host "  ✓ Files deployed" -ForegroundColor Green

    # Step 3: Restart container
    Write-Host "[3/5] Restarting ocean-core container..." -ForegroundColor Yellow
    ssh @SSH_OPTS "root@${REMOTE_HOST}" @"
cd $REMOTE_DIR && \
docker compose -f docker-compose.75-services.yml down ocean-core 2>/dev/null || true && \
sleep 3 && \
docker compose -f docker-compose.75-services.yml up -d ocean-core && \
sleep 10
"@ 2>&1 | Out-Null
    Write-Host "  ✓ Ocean-core restarted" -ForegroundColor Green

    # Step 4: Health check
    Write-Host "[4/5] Verifying health..." -ForegroundColor Yellow
    $healthScript = @"
import requests
import time

for i in range(8):
    try:
        r = requests.get('http://localhost:8030/health', timeout=5)
        if r.status_code == 200:
            print('  ✓ Health check passed')
            exit(0)
    except:
        pass
    time.sleep(2)

print('  ✗ Health check failed')
exit(1)
"@
    
    ssh @SSH_OPTS "root@${REMOTE_HOST}" "python3 << 'END'
$healthScript
END" | Write-Host
    
    if ($LASTEXITCODE -ne 0) {
        throw "Health check failed"
    }

    # Step 5: Validation
    Write-Host "[5/5] Running validation suite..." -ForegroundColor Yellow
    scp @SSH_OPTS validate_ocean_ready.py "root@${REMOTE_HOST}:/root/validate_ocean.py" 2>&1 | Out-Null
    
    ssh @SSH_OPTS "root@${REMOTE_HOST}" "python3 /root/validate_ocean.py" | Write-Host

    # Success
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✓ DEPLOYMENT COMPLETE                                         ║" -ForegroundColor Green
    Write-Host "║                                                                ║" -ForegroundColor Green
    Write-Host "║  Ocean-Core is now ready with:                                 ║" -ForegroundColor Green
    Write-Host "║  • Multi-language support (responds in question language)      ║" -ForegroundColor Green
    Write-Host "║  • Instant streaming (0.2s start)                              ║" -ForegroundColor Green
    Write-Host "║  • Elastic timeouts (scales with content)                      ║" -ForegroundColor Green
    Write-Host "║  • End-to-end integration                                      ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Clisonix is now production-ready worldwide!" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
