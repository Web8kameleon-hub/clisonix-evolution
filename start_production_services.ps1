#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start all Clisonix Cloud services with PRODUCTION environment configuration
.DESCRIPTION
Launches all 7 microservices using centralized config/settings.py with .env.production
Services: ALBA (5555), ALBI (6680), JONA (7777), Main API (8000), Ocean (8030), Excel/Idle (8031), Frontend (3000)
.NOTES
All services load from .env.production by default
#>

$ErrorActionPreference = "Continue"
$WarningPreference = "SilentlyContinue"

# Color functions
function Write-Header {
    param([string]$Text)
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Text".PadRight(61) + "║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-Service {
    param([string]$Name, [int]$Port, [string]$Status)
    $color = if ($Status -eq "STARTED") { "Green" } else { "Yellow" }
    Write-Host "  [$Status] $Name on port $Port" -ForegroundColor $color
}

# Clear any previous processes
Write-Host "`nCleaning up any existing processes..." -ForegroundColor Yellow
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Header "CLISONIX CLOUD - PRODUCTION STARTUP"
Write-Host "Environment: Production | Config: .env.production" -ForegroundColor Green
Write-Host ""

# Track PIDs for monitoring
$services = @(
    @{Name="ALBA Collector"; Port=5555; Script="alba_service_5555.py"; Type="python"}
    @{Name="ALBI Processor"; Port=6680; Script="albi_service_6680.py"; Type="python"}
    @{Name="JONA Coordinator"; Port=7777; Script="jona_service_7777.py"; Type="python"}
    @{Name="Main API"; Port=8000; Script="apps\api\main.py"; Type="uvicorn"}
    @{Name="Ocean Core"; Port=8030; Script="ocean-core\ocean_api.py"; Type="python"}
    @{Name="Alba Idle Chat"; Port=8031; Script="alba_idle_chat.py"; Type="python"}
    @{Name="Frontend"; Port=3000; Script="apps\web\package.json"; Type="npm"}
)

Write-Host "Starting services:" -ForegroundColor Cyan
Write-Host ""

foreach ($service in $services) {
    $name = $service.Name
    $port = $service.Port
    $script = $service.Script
    $type = $service.Type
    
    try {
        if ($type -eq "python") {
            Start-Process -FilePath "python" -ArgumentList $script -NoNewWindow -RedirectStandardError "$env:TEMP\${name}_error.log" -RedirectStandardOutput "$env:TEMP\${name}_output.log" -PassThru | Out-Null
            Write-Service $name $port "STARTED"
            Start-Sleep -Milliseconds 500
        }
        elseif ($type -eq "uvicorn") {
            $dir = Split-Path -Path $script -Parent
            Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", $port -WorkingDirectory $dir -NoNewWindow -RedirectStandardError "$env:TEMP\${name}_error.log" -RedirectStandardOutput "$env:TEMP\${name}_output.log" -PassThru | Out-Null
            Write-Service $name $port "STARTED"
            Start-Sleep -Milliseconds 500
        }
        elseif ($type -eq "npm") {
            $dir = Split-Path -Path $script -Parent
            Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $dir -NoNewWindow -RedirectStandardError "$env:TEMP\${name}_error.log" -RedirectStandardOutput "$env:TEMP\${name}_output.log" -PassThru | Out-Null
            Write-Service $name $port "STARTED"
            Start-Sleep -Milliseconds 500
        }
    }
    catch {
        Write-Service $name $port "FAILED"
    }
}

Write-Host ""
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Health Check:" -ForegroundColor Cyan

$ports = @(5555, 6680, 7777, 8000, 8030, 8031, 3000)
$operational = 0

foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] Port $port - OPERATIONAL" -ForegroundColor Green
            $operational++
        }
        else {
            Write-Host "  [?] Port $port - RESPONDING" -ForegroundColor Yellow
            $operational++
        }
    }
    catch {
        Write-Host "  [X] Port $port - NOT RESPONDING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║ STARTUP COMPLETE: $operational / 7 SERVICES OPERATIONAL".PadRight(61) + "║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://127.0.0.1:3000" -ForegroundColor White
Write-Host "  API:       http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Ocean:     http://127.0.0.1:8030" -ForegroundColor White
Write-Host ""
Write-Host "Configuration: PRODUCTION - .env.production loaded" -ForegroundColor Green
Write-Host "Database: 46.224.203.89:5432 (real Hetzner server)" -ForegroundColor White
Write-Host ""
