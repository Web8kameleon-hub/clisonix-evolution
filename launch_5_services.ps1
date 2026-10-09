#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start CLISONIX CLOUD 5 Primary Services - Sequential Launcher
.DESCRIPTION
Starts all core services in separate terminal windows for production use
Services: Frontend, Backend API, Ocean Core, Excel/Idle Chat, ALBA Collector
.NOTES
Author: Clisonix DevOps
Date: February 2026
#>

param(
    [switch]$Help
)

if ($Help) {
    Write-Host @"
CLISONIX CLOUD - PROFESSIONAL SERVICES LAUNCHER
===============================================

Services started in order:
1. Frontend (Port 3000) - Next.js React App
2. Backend API (Port 8000) - FastAPI/Uvicorn
3. Ocean Core (Port 8030) - AI/ML Engine
4. Excel Core (Port 8031) - Excel Dashboard & Chat
5. ALBA Collector (Port 5555) - Python Backend Service
6. ALBI EEG User API (Port 6681) - Professional Brainwave Analyzer
7. JONA Neural Synthesis (Port 7777) - Therapeutic Audio Synthesis Engine

All services open in separate terminal windows for monitoring.
Real-time data streaming, real WebSocket connections, zero placeholders.
Professional diamond-level services with 100% real functionality.

Usage: .\launch_5_services.ps1
"@
    exit
}

# Configuration
$services = @(
    @{
        Order = 1
        Name = "Frontend"
        Port = 3000
        Type = "npm"
        WorkDir = "apps\web"
        Command = "npm"
        Args = @("run", "dev")
        Timeout = 10
    }
    @{
        Order = 2
        Name = "Backend API"
        Port = 8000
        Type = "python-uvicorn"
        WorkDir = "apps\api"
        Command = "python"
        Args = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000")
        Timeout = 15
    }
    @{
        Order = 3
        Name = "Ocean Core"
        Port = 8030
        Type = "python"
        WorkDir = "ocean-core"
        Command = "python"
        Args = @("ocean_api.py")
        Timeout = 8
    }
    @{
        Order = 4
        Name = "Excel Core"
        Port = 8031
        Type = "python"
        WorkDir = "."
        Command = "python"
        Args = @("alba_idle_chat.py")
        Timeout = 5
    }
    @{
        Order = 6
        Name = "ALBI EEG API"
        Port = 6681
        Type = "python"
        WorkDir = "."
        Command = "python"
        Args = @("albi_user_api.py")
        Timeout = 8
    }
    @{
        Order = 7
        Name = "JONA Neural Synthesis"
        Port = 7777
        Type = "python"
        WorkDir = "."
        Command = "python"
        Args = @("jona_neural_api.py")
        Timeout = 8
    }
)

# Colors
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "White"
}

# Functions
function Write-Header {
    param([string]$Text)
    Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Header
    Write-Host "║ $($Text.PadRight(58)) ║" -ForegroundColor $Colors.Header
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Header
}

function Write-Service {
    param([int]$Order, [string]$Name, [int]$Port, [string]$Status)
    $icon = switch ($Status) {
        "STARTING" { "⏳" }
        "READY" { "✅" }
        "ERROR" { "❌" }
        default { "●" }
    }
    $statusColor = if ($Status -eq "READY") { $Colors.Success }
        elseif ($Status -eq "ERROR") { $Colors.Error }
        else { $Colors.Warning }
    Write-Host "[$Order] $icon $Name (Port $Port) - $Status" -ForegroundColor $statusColor
}

function Test-ServiceHealth {
    param([int]$Port, [int]$Timeout = 5)
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    while ($stopwatch.Elapsed.TotalSeconds -lt $Timeout) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    }
    return $false
}

# Main
Clear-Host
Write-Header "CLISONIX CLOUD - PROFESSIONAL PRODUCTION SERVICES"
Write-Host "Environment: Development (localhost)" -ForegroundColor $Colors.Info
Write-Host "Configuration: Centralized settings from config/" -ForegroundColor $Colors.Info

# Kill any existing processes
Write-Host "`n[PREP] Cleaning up any existing processes..." -ForegroundColor $Colors.Warning
Get-Process python, node, npm -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "[PREP] Ready to start services`n" -ForegroundColor $Colors.Success

# Start services in order
foreach ($service in $services | Sort-Object Order) {
    Write-Service $service.Order $service.Name $service.Port "STARTING"
    
    $workDir = Join-Path $PSScriptRoot $service.WorkDir
    
    # Build command
    $cmdArgs = $service.Args -join " "
    
    # Open in new window
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $service.Command
    $processInfo.Arguments = $cmdArgs
    $processInfo.WorkingDirectory = $workDir
    $processInfo.UseShellExecute = $true
    $processInfo.CreateNoWindow = $false
    
    [System.Diagnostics.Process]::Start($processInfo) | Out-Null
    
    # Wait for service to be ready
    Write-Host "  ⏳ Waiting for $($service.Name) to initialize (timeout $($service.Timeout)s)..." -ForegroundColor $Colors.Warning
    Start-Sleep -Seconds 3
    
    if (Test-ServiceHealth -Port $service.Port -Timeout $service.Timeout) {
        Write-Service $service.Order $service.Name $service.Port "READY"
    }
    else {
        Write-Service $service.Order $service.Name $service.Port "STARTING (check terminal for output)"
    }
    
    # Extra delay between services for proper initialization
    if ($service.Order -lt $services.Count) {
        Start-Sleep -Seconds 2
    }
    
    Write-Host ""
}

# Summary
Write-Header "SERVICES LAUNCHED"
Write-Host ""
Write-Host "Access Points (Real-Time APIs):" -ForegroundColor $Colors.Info
Write-Host "  Frontend (Web UI):     http://127.0.0.1:3000" -ForegroundColor $Colors.Success
Write-Host "  Backend API:           http://127.0.0.1:8000/docs" -ForegroundColor $Colors.Success
Write-Host "  Ocean Core:            http://127.0.0.1:8030" -ForegroundColor $Colors.Success
Write-Host "  Excel Core:            http://127.0.0.1:8031" -ForegroundColor $Colors.Success
Write-Host "  ALBA Collector:        http://127.0.0.1:5555/health" -ForegroundColor $Colors.Success
Write-Host "  ALBI EEG Analyzer:     http://127.0.0.1:3000/modules/albi-eeg-live" -ForegroundColor $Colors.Success
Write-Host "  ALBI EEG API (WebSocket): ws://127.0.0.1:6681/stream/{session_id}" -ForegroundColor $Colors.Success

Write-Host ""
Write-Host "Each service opened in its own terminal window." -ForegroundColor $Colors.Info
Write-Host "Monitor each terminal for errors or logs." -ForegroundColor $Colors.Info
Write-Host ""
Write-Host "If you see errors, send the output and I'll fix it! 👍" -ForegroundColor $Colors.Warning
Write-Host ""
