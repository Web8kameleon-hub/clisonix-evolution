#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Megalayer integration launcher - starts all services and runs tests
.DESCRIPTION
    Kills old processes, starts Ocean Core + Backend API, waits for health, runs megalayer tests
#>

param(
    [switch]$SkipFrontend,
    [switch]$TestOnly,
    [int]$WaitSeconds = 5
)

$ErrorActionPreference = "Continue"
$ProjectRoot = "c:\Users\Admin\Desktop\Clisonix-cloud"
$PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
$NodeExe = "node"

Write-Host "`n🚀 MEGALAYER COMPLETE LAUNCH SCRIPT" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Function to check if port is listening
function Test-PortListening {
    param([int]$Port)
    try {
        $null = [System.Net.Sockets.TcpClient]::new().Connect("127.0.0.1", $Port)
        return $true
    } catch {
        return $false
    }
}

# Function to wait for service health
function Wait-ServiceReady {
    param([string]$Url, [string]$ServiceName, [int]$MaxWait = 30)
    
    Write-Host "`n⏳ Waiting for $ServiceName to be ready..." -ForegroundColor Yellow
    
    $elapsed = 0
    while ($elapsed -lt $MaxWait) {
        try {
            $response = curl.exe -s -m 2 "$Url" 2>$null
            if ($response) {
                Write-Host "✅ $ServiceName is ready!" -ForegroundColor Green
                return $true
            }
        } catch {}
        
        Start-Sleep -Seconds 1
        $elapsed += 1
    }
    
    Write-Host "⚠️  $ServiceName timeout after $MaxWait seconds" -ForegroundColor Yellow
    return $false
}

# ============================================
# STEP 1: Kill existing processes
# ============================================
Write-Host "`n[1/5] Killing existing processes..." -ForegroundColor Cyan

$ports = @(8000, 8030, 3000)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($process) {
        $pid = $process.OwningProcess
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Killed process on port $port (PID: $pid)"
    }
}

Start-Sleep -Seconds 2

# ============================================
# STEP 2: Start Ocean Core (8030)
# ============================================
Write-Host "`n[2/5] Starting Ocean Core on port 8030..." -ForegroundColor Cyan

Push-Location "$ProjectRoot\ocean-core"
Start-Process -FilePath $PythonExe -ArgumentList "ocean_core_full.py" -NoNewWindow -RedirectStandardOutput "$ProjectRoot\logs\ocean-core.log" -RedirectStandardError "$ProjectRoot\logs\ocean-core-err.log"
Pop-Location

Write-Host "  ✓ Ocean Core process started" -ForegroundColor Green
Wait-ServiceReady "http://localhost:8030/health" "Ocean Core" 15

# ============================================
# STEP 3: Start Backend API (8000)
# ============================================
Write-Host "`n[3/5] Starting Backend API on port 8000..." -ForegroundColor Cyan

$env:OCEAN_CORE_URL = "http://localhost:8030"
Push-Location "$ProjectRoot\apps\api"
Start-Process -FilePath $PythonExe -ArgumentList "main.py" -NoNewWindow -RedirectStandardOutput "$ProjectRoot\logs\backend-api.log" -RedirectStandardError "$ProjectRoot\logs\backend-api-err.log"
Pop-Location

Write-Host "  ✓ Backend API process started" -ForegroundColor Green
Wait-ServiceReady "http://localhost:8000/api/health" "Backend API" 15

# ============================================
# STEP 4: Start Frontend (optional)
# ============================================
if (-not $SkipFrontend -and -not $TestOnly) {
    Write-Host "`n[4/5] Starting Frontend on port 3000..." -ForegroundColor Cyan
    
    Push-Location "$ProjectRoot\apps\web"
    Start-Process -FilePath $NodeExe -ArgumentList "node_modules\.bin\next dev" -NoNewWindow -RedirectStandardOutput "$ProjectRoot\logs\frontend.log" -RedirectStandardError "$ProjectRoot\logs\frontend-err.log"
    Pop-Location
    
    Write-Host "  ✓ Frontend process started" -ForegroundColor Green
    Wait-ServiceReady "http://localhost:3000" "Frontend" 15
}

# ============================================
# STEP 5: Run Megalayer Integration Tests
# ============================================
Write-Host "`n[5/5] Running Megalayer Integration Tests..." -ForegroundColor Cyan

Start-Sleep -Seconds 2
cd $ProjectRoot

Write-Host ""
& $PythonExe test_megalayer_integration.py

# ============================================
# Summary
# ============================================
Write-Host "`n" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "✨ MEGALAYER LAUNCH COMPLETE" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running on:" -ForegroundColor Yellow
Write-Host "  🌊 Ocean Core:   http://localhost:8030" -ForegroundColor White
Write-Host "  🔀 Backend API:  http://localhost:8000" -ForegroundColor White
if (-not $SkipFrontend -and -not $TestOnly) {
    Write-Host "  🌐 Frontend:     http://localhost:3000" -ForegroundColor White
}
Write-Host ""
Write-Host "Log files:" -ForegroundColor Yellow
Write-Host "  📄 Ocean Core:   $ProjectRoot\logs\ocean-core.log" -ForegroundColor White
Write-Host "  📄 Backend API:  $ProjectRoot\logs\backend-api.log" -ForegroundColor White
if (-not $SkipFrontend -and -not $TestOnly) {
    Write-Host "  📄 Frontend:     $ProjectRoot\logs\frontend.log" -ForegroundColor White
}
Write-Host ""
Write-Host "Test megalayer with:" -ForegroundColor Yellow
Write-Host "  curl -X POST http://localhost:8000/api/ocean/megalayer -H 'Content-Type: application/json' -d '{\"query\": \"What is consciousness?\"}'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all services:" -ForegroundColor Yellow
Write-Host "  Get-Process python, node | Stop-Process -Force" -ForegroundColor Cyan
Write-Host ""
