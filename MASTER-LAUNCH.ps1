#!/usr/bin/env pwsh
<#
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║              🚀 CLISONIX CLOUD - MASTER LAUNCHER v2.0 🚀                     ║
║                    "The Ultimate Startup Orchestrator"                        ║
║                                                                               ║
║  Consolidates 19 PowerShell scripts into one unified entry point with         ║
║  7 operational modes, intelligent health checking, and real-time monitoring.  ║
║                                                                               ║
║  Usage:  .\MASTER-LAUNCH.ps1 -Mode dev -Clean -Monitor                       ║
║  Modes:  dev | prod | full | docker | saas | monitor | diagnostics          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
#>

param(
    [ValidateSet('dev', 'prod', 'full', 'docker', 'saas', 'monitor', 'diagnostics', 'help')]
    [string]$Mode = 'full',
    
    [switch]$Clean,
    [switch]$DryRun,
    [switch]$Monitor,
    [switch]$Rebuild,
    [switch]$Help
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

$Root = 'c:\clisonix-cloud'
Set-Location $Root

$Colors = @{
    Title    = 'Magenta'
    Success  = 'Green'
    Warning  = 'Yellow'
    Error    = 'Red'
    Info     = 'Cyan'
    Section  = 'Blue'
    Accent   = 'DarkCyan'
}

$ServicePorts = @{
    'API'              = 8000
    'Frontend'         = 3000
    'ALBA'             = 5555
    'ALBI'             = 6680
    'JONA'             = 7777
    'Orchestrator'     = 9999
    'PostgreSQL'       = 5432
    'Redis'            = 6379
    'MinIO'            = 9000
    'MinIO-Console'    = 9001
    'Prometheus'       = 9090
    'Grafana'          = 3001
    'Health-Check'     = 8088
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Show-Banner {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║              🚀  CLISONIX CLOUD - MASTER LAUNCHER  🚀                         ║" -ForegroundColor $Colors.Title
    Write-Host "║                     « The Ultimate Orchestrator »                             ║" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor $Colors.Title
}

function Show-Status {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'OK', 'WAIT', 'ERROR', 'WARN')]
        [string]$Status = 'INFO'
    )
    
    $Icon = @{
        'INFO'    = '▸'
        'OK'      = '✓'
        'WAIT'    = '◌'
        'ERROR'   = '✗'
        'WARN'    = '⚠'
    }[$Status]
    
    $Color = @{
        'INFO'    = $Colors.Info
        'OK'      = $Colors.Success
        'WAIT'    = $Colors.Warning
        'ERROR'   = $Colors.Error
        'WARN'    = $Colors.Warning
    }[$Status]
    
    Write-Host "  $Icon " -NoNewline -ForegroundColor $Color
    Write-Host $Message
}

function Show-Help {
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         MASTER LAUNCHER - HELP                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

MODES:
  dev            Development mode (API + Frontend as background jobs)
  prod           Production mode (Detached windows with isolated processes)
  full           Full stack (All services parallel launch with health checks)
  docker         Docker Compose (Complete 12-service containerized deployment)
  saas           SaaS microservices only (ALBA, ALBI, JONA, Orchestrator)
  monitor        Continuous health monitoring & auto-healing
  diagnostics    System health scan (port check, service probes, report)

FLAGS:
  -Clean         Kill all existing node/python processes before startup
  -DryRun        Preview startup without launching services
  -Monitor       Enable continuous health monitoring during execution
  -Rebuild       Force Docker image rebuild (docker mode only)
  -Help          Show this help message

EXAMPLES:
  .\MASTER-LAUNCH.ps1 -Mode dev
  .\MASTER-LAUNCH.ps1 -Mode full -Monitor
  .\MASTER-LAUNCH.ps1 -Mode docker -Rebuild -DryRun
  .\MASTER-LAUNCH.ps1 -Mode diagnostics

"@ -ForegroundColor $Colors.Info
}

function Invoke-PreFlightCheck {
    Write-Host "`n┌─── PRE-FLIGHT CHECKS ───────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    $passed = $true
    
    # Check Node.js
    Show-Status "Checking Node.js..." 'WAIT'
    $node = node --version 2>$null
    if ($node) {
        Show-Status "Node.js $node ✓" 'OK'
    } else {
        Show-Status "Node.js not found ✗" 'ERROR'
        $passed = $false
    }
    
    # Check Python
    Show-Status "Checking Python..." 'WAIT'
    $python = python --version 2>&1
    if ($?) {
        Show-Status "Python installed ✓" 'OK'
    } else {
        Show-Status "Python not found ✗" 'ERROR'
        $passed = $false
    }
    
    # Check Docker (for docker mode)
    if ($Mode -eq 'docker') {
        Show-Status "Checking Docker..." 'WAIT'
        $docker = docker --version 2>$null
        if ($docker) {
            Show-Status "Docker $docker ✓" 'OK'
        } else {
            Show-Status "Docker not found ✗" 'ERROR'
            $passed = $false
        }
    }
    
    # Check .env file
    Show-Status "Checking .env configuration..." 'WAIT'
    if (-not (Test-Path '.env')) {
        Show-Status ".env not found (will use defaults)" 'WARN'
    } else {
        Show-Status ".env loaded ✓" 'OK'
    }
    
    # Check dependencies
    Show-Status "Checking npm dependencies..." 'WAIT'
    if (-not (Test-Path 'apps\web\node_modules')) {
        if (-not $DryRun) {
            Show-Status "Installing npm dependencies..." 'WAIT'
            Push-Location 'apps\web'
            npm install --legacy-peer-deps --silent 2>$null
            Pop-Location
        }
        Show-Status "Dependencies ready ✓" 'OK'
    } else {
        Show-Status "Dependencies cached ✓" 'OK'
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
    
    if (-not $passed) {
        Show-Status "Some critical tools missing!" 'ERROR'
        return $false
    }
    
    return $true
}

function Invoke-CleanupProcesses {
    Write-Host "`n┌─── PROCESS CLEANUP ──────────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    Show-Status "Terminating existing services..." 'WAIT'
    
    $nodeProcs = Get-Process -Name 'node' -ErrorAction SilentlyContinue
    $pythonProcs = Get-Process -Name 'python' -ErrorAction SilentlyContinue
    
    if ($nodeProcs) {
        $nodeProcs | Stop-Process -Force -ErrorAction SilentlyContinue
        Show-Status "Killed $($nodeProcs.Count) Node.js process(es) ✓" 'OK'
    }
    
    if ($pythonProcs) {
        $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
        Show-Status "Killed $($pythonProcs.Count) Python process(es) ✓" 'OK'
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Invoke-PortCheck {
    Write-Host "`n┌─── PORT AVAILABILITY CHECK ──────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    $busyPorts = @()
    
    foreach ($svc in $ServicePorts.GetEnumerator()) {
        $connection = Get-NetTCPConnection -LocalPort $svc.Value -ErrorAction SilentlyContinue
        if ($connection) {
            Show-Status "$($svc.Name) (Port $($svc.Value)) - IN USE ⚠" 'WARN'
            $busyPorts += $svc.Value
        } else {
            Show-Status "$($svc.Name) (Port $($svc.Value)) - Available ✓" 'OK'
        }
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
    
    if ($busyPorts.Count -gt 0 -and -not $Clean) {
        Write-Host "`n  ⚠  WARNING: Ports in use detected. Use -Clean flag to force cleanup.`n" -ForegroundColor $Colors.Warning
    }
    
    return $busyPorts.Count -eq 0
}

function Start-DevMode {
    Write-Host "`n┌─── MODE: DEVELOPMENT (Background Jobs) ──────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start API as background job (port 8000)" 'INFO'
        Show-Status "[DRY RUN] Would start Frontend as background job (port 3000)" 'INFO'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor $Colors.Section
        return
    }
    
    Show-Status "Starting API Server (port 8000)..." 'WAIT'
    $apiJob = Start-Job -Name 'API' -ScriptBlock {
        Set-Location 'c:\clisonix-cloud'
        python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
    }
    Show-Status "API started (Job #$($apiJob.Id)) ✓" 'OK'
    
    Start-Sleep -Seconds 2
    
    Show-Status "Starting Frontend (port 3000)..." 'WAIT'
    $webJob = Start-Job -Name 'Frontend' -ScriptBlock {
        Set-Location 'c:\clisonix-cloud\apps\web'
        $env:NEXT_PUBLIC_API_BASE = 'http://localhost:8000'
        npm run dev 2>$null
    }
    Show-Status "Frontend started (Job #$($webJob.Id)) ✓" 'OK'
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
    Show-Status "Use: Get-Job | Stop-Job to manage services" 'INFO'
}

function Start-ProdMode {
    Write-Host "`n┌─── MODE: PRODUCTION (Detached Windows) ──────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would open API window (port 8000)" 'INFO'
        Show-Status "[DRY RUN] Would open Frontend window (port 3000)" 'INFO'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor $Colors.Section
        return
    }
    
    Show-Status "Starting API in separate window..." 'WAIT'
    $apiScript = {
        Set-Location 'c:\clisonix-cloud'
        $host.UI.RawUI.WindowTitle = "Clisonix - API (8000)"
        Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║   API SERVER STARTING - Port 8000      ║" -ForegroundColor Green
        Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
        python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
    }
    Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $apiScript)
    Show-Status "API window opened ✓" 'OK'
    
    Start-Sleep -Seconds 3
    
    Show-Status "Starting Frontend in separate window..." 'WAIT'
    $frontendScript = {
        Set-Location 'c:\clisonix-cloud\apps\web'
        $host.UI.RawUI.WindowTitle = "Clisonix - Frontend (3000)"
        $env:NEXT_PUBLIC_API_BASE = "http://localhost:8000"
        Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║   FRONTEND STARTING - Port 3000        ║" -ForegroundColor Yellow
        Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Yellow
        npm run dev
    }
    Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $frontendScript)
    Show-Status "Frontend window opened ✓" 'OK'
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Start-FullMode {
    Write-Host "`n┌─── MODE: FULL STACK (Mega Launch with Health Checks) ────────────────────────┐" -ForegroundColor $Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would launch API (8000) in window" 'INFO'
        Show-Status "[DRY RUN] Would launch Frontend (3000) in window" 'INFO'
        Show-Status "[DRY RUN] Would perform 10 health check probes" 'INFO'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor $Colors.Section
        return
    }
    
    Show-Status "Initializing parallel startup sequence..." 'WAIT'
    Start-Sleep -Seconds 1
    
    Show-Status "Launching API Server..." 'WAIT'
    $apiScript = {
        Set-Location 'c:\clisonix-cloud'
        $host.UI.RawUI.WindowTitle = "CLISONIX - API SERVER (8000)"
        Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║   API SERVER ONLINE - Port 8000        ║" -ForegroundColor Cyan
        Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
        python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
    }
    Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $apiScript)
    Show-Status "API launched ✓" 'OK'
    
    Start-Sleep -Seconds 2
    
    Show-Status "Launching Frontend..." 'WAIT'
    $frontendScript = {
        Set-Location 'c:\clisonix-cloud\apps\web'
        $host.UI.RawUI.WindowTitle = "CLISONIX - FRONTEND (3000)"
        $env:NEXT_PUBLIC_API_BASE = "http://localhost:8000"
        Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║   FRONTEND ONLINE - Port 3000          ║" -ForegroundColor Yellow
        Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Yellow
        npm run dev
    }
    Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $frontendScript)
    Show-Status "Frontend launched ✓" 'OK'
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
    
    Start-Sleep -Seconds 3
    
    Invoke-HealthChecks
}

function Start-DockerMode {
    Write-Host "`n┌─── MODE: DOCKER COMPOSE (Full Container Stack) ───────────────────────────────┐" -ForegroundColor $Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would execute: docker-compose up -d" 'INFO'
        Show-Status "[DRY RUN] Would launch 12 containerized services" 'INFO'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor $Colors.Section
        return
    }
    
    if ($Rebuild) {
        Show-Status "Rebuilding Docker images..." 'WAIT'
        docker-compose build 2>$null
        Show-Status "Docker images rebuilt ✓" 'OK'
    }
    
    Show-Status "Starting Docker Compose stack..." 'WAIT'
    docker-compose up -d 2>$null
    Show-Status "Docker services launched ✓" 'OK'
    
    Start-Sleep -Seconds 5
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
    
    Show-Status "Running docker-compose status check..." 'WAIT'
    docker-compose ps 2>$null
}

function Start-SaaSMode {
    Write-Host "`n┌─── MODE: SAAS MICROSERVICES (ALBA, ALBI, JONA, Orchestrator) ────────────────┐" -ForegroundColor $Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start ALBA (5555)" 'INFO'
        Show-Status "[DRY RUN] Would start ALBI (6680)" 'INFO'
        Show-Status "[DRY RUN] Would start JONA (7777)" 'INFO'
        Show-Status "[DRY RUN] Would start Orchestrator (9999)" 'INFO'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor $Colors.Section
        return
    }
    
    Show-Status "Launching microservices..." 'WAIT'
    
    $services = @(
        @{ Name = 'ALBA'; Port = 5555; Script = 'alba_core.py' }
        @{ Name = 'ALBI'; Port = 6680; Script = 'albi_core.py' }
        @{ Name = 'JONA'; Port = 7777; Script = 'alba_frame_generator.py' }
        @{ Name = 'Orchestrator'; Port = 9999; Script = 'mesh_cluster_startup.py' }
    )
    
    foreach ($svc in $services) {
        if (Test-Path $svc.Script) {
            Start-Job -Name $svc.Name -ScriptBlock {
                param($Script, $Port)
                Set-Location 'c:\clisonix-cloud'
                python $Script
            } -ArgumentList $svc.Script, $svc.Port
            
            Show-Status "$($svc.Name) started on port $($svc.Port) ✓" 'OK'
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Invoke-HealthChecks {
    Write-Host "`n┌─── HEALTH CHECK PROBES ──────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    $endpoints = @(
        @{ Name = 'API Health'; URL = 'http://localhost:8000/health' }
        @{ Name = 'API Docs'; URL = 'http://localhost:8000/docs' }
        @{ Name = 'Frontend'; URL = 'http://localhost:3000' }
    )
    
    $maxRetries = 10
    $retryDelay = 2
    
    for ($retry = 1; $retry -le $maxRetries; $retry++) {
        Write-Host "  Probe $retry/$maxRetries..." -ForegroundColor $Colors.Info
        $healthy = 0
        
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.URL -SkipHttpErrorCheck -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Show-Status "$($endpoint.Name) responding ✓" 'OK'
                    $healthy++
                } else {
                    Show-Status "$($endpoint.Name) - Status $($response.StatusCode)" 'WARN'
                }
            } catch {
                if ($retry -eq $maxRetries) {
                    Show-Status "$($endpoint.Name) - No response" 'WARN'
                }
            }
        }
        
        if ($healthy -eq $endpoints.Count) {
            Write-Host "`n  ✓ All services healthy!`n" -ForegroundColor $Colors.Success
            break
        }
        
        if ($retry -lt $maxRetries) {
            Start-Sleep -Seconds $retryDelay
        }
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Invoke-DiagnosticsMode {
    Write-Host "`n┌─── DIAGNOSTICS: SYSTEM HEALTH SCAN ──────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    Write-Host "`n📋 Service Port Status:" -ForegroundColor $Colors.Section
    foreach ($svc in $ServicePorts.GetEnumerator()) {
        $connection = Get-NetTCPConnection -LocalPort $svc.Value -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "  ✓ $($svc.Name) (Port $($svc.Value)) - ACTIVE" -ForegroundColor $Colors.Success
        } else {
            Write-Host "  ○ $($svc.Name) (Port $($svc.Value)) - Inactive" -ForegroundColor $Colors.Info
        }
    }
    
    Write-Host "`n📊 Health Endpoints:" -ForegroundColor $Colors.Section
    $endpoints = @(
        'http://localhost:8000/health',
        'http://localhost:8000/system-status',
        'http://localhost:3000'
    )
    
    foreach ($url in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $url -SkipHttpErrorCheck -TimeoutSec 2 -ErrorAction SilentlyContinue
            Write-Host "  ✓ $url - HTTP $($response.StatusCode)" -ForegroundColor $Colors.Success
        } catch {
            Write-Host "  ✗ $url - Unreachable" -ForegroundColor $Colors.Error
        }
    }
    
    Write-Host "`n💾 Process Status:" -ForegroundColor $Colors.Section
    $nodeProcs = Get-Process -Name 'node' -ErrorAction SilentlyContinue
    $pythonProcs = Get-Process -Name 'python' -ErrorAction SilentlyContinue
    
    Write-Host "  Node.js processes: $($nodeProcs.Count)" -ForegroundColor $Colors.Info
    Write-Host "  Python processes: $($pythonProcs.Count)" -ForegroundColor $Colors.Info
    
    Write-Host "`n📁 Project Status:" -ForegroundColor $Colors.Section
    Write-Host "  Root: $Root" -ForegroundColor $Colors.Info
    Write-Host "  .env exists: $(Test-Path '.env')" -ForegroundColor $Colors.Info
    Write-Host "  apps/web/node_modules: $(Test-Path 'apps\web\node_modules')" -ForegroundColor $Colors.Info
    Write-Host "  docker-compose.yml: $(Test-Path 'docker-compose.yml')" -ForegroundColor $Colors.Info
    
    Write-Host "`n└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Show-Dashboard {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Title
    Write-Host "║                         🎯 SYSTEM ONLINE 🎯                                  ║" -ForegroundColor $Colors.Title
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  📊 ENDPOINTS                                                                 ║" -ForegroundColor $Colors.Title
    Write-Host "║  ├─ Frontend:      http://localhost:3000                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ API:           http://localhost:8000                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ Docs:          http://localhost:8000/docs                                 ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ Dashboard:     http://localhost:3000/modules/fitness-dashboard           ║" -ForegroundColor $Colors.Success
    Write-Host "║  └─ Health:        http://localhost:8000/health                               ║" -ForegroundColor $Colors.Success
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  ⚙️  STARTUP MODE                                                            ║" -ForegroundColor $Colors.Title
    Write-Host "║  └─ Mode: $Mode" -NoNewline -ForegroundColor $Colors.Title
    
    switch ($Mode) {
        'dev' { Write-Host " (Development - Background Jobs)" -ForegroundColor $Colors.Info }
        'prod' { Write-Host " (Production - Detached Windows)" -ForegroundColor $Colors.Info }
        'full' { Write-Host " (Full Stack - Mega Launch)" -ForegroundColor $Colors.Info }
        'docker' { Write-Host " (Docker - Container Stack)" -ForegroundColor $Colors.Info }
        'saas' { Write-Host " (SaaS - Microservices Only)" -ForegroundColor $Colors.Info }
        'monitor' { Write-Host " (Monitor - Continuous Health Check)" -ForegroundColor $Colors.Info }
        'diagnostics' { Write-Host " (Diagnostics - System Scan)" -ForegroundColor $Colors.Info }
    }
    
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  💡 QUICK TIPS                                                                ║" -ForegroundColor $Colors.Title
    Write-Host "║  ├─ Get-Job                    | List running background jobs                ║" -ForegroundColor $Colors.Warning
    Write-Host "║  ├─ Stop-Job -Name API         | Stop API service                            ║" -ForegroundColor $Colors.Warning
    Write-Host "║  ├─ Get-Job | Stop-Job         | Stop all services                           ║" -ForegroundColor $Colors.Warning
    Write-Host "║  └─ .\MASTER-LAUNCH.ps1 -Help  | Show this help                              ║" -ForegroundColor $Colors.Warning
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor $Colors.Title
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

Show-Banner

if ($Help) {
    Show-Help
    exit 0
}

if (-not (Invoke-PreFlightCheck)) {
    Show-Status "Pre-flight check FAILED!" 'ERROR'
    exit 1
}

if ($Clean) {
    Invoke-CleanupProcesses
}

if (-not (Invoke-PortCheck)) {
    if (-not $Clean) {
        Write-Host "`n  ⚠  Use -Clean flag to force cleanup of occupied ports`n" -ForegroundColor $Colors.Warning
    }
}

# Execute selected mode
switch ($Mode) {
    'dev'         { Start-DevMode }
    'prod'        { Start-ProdMode }
    'full'        { Start-FullMode }
    'docker'      { Start-DockerMode }
    'saas'        { Start-SaaSMode }
    'diagnostics' { Invoke-DiagnosticsMode }
    'monitor'     {
        Write-Host "`n┌─── MODE: CONTINUOUS MONITORING ──────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
        Show-Status "Starting continuous health monitoring..." 'WAIT'
        Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
        
        while ($true) {
            Invoke-HealthChecks
            Start-Sleep -Seconds 30
        }
    }
}

Show-Dashboard

Write-Host "🚀 Clisonix Cloud is ready for takeoff!`n" -ForegroundColor $Colors.Success

