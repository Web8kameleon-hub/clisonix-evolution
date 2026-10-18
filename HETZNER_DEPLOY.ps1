#!/usr/bin/env powershell
# ═══════════════════════════════════════════════════════════════════════════════
# CLISONIX CLOUD - HETZNER DEPLOYMENT ORCHESTRATOR (PowerShell)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Purpose: Deploy 75+ microservices to Hetzner CPX62 from Windows
# Server: 46.62.210.251 (Helsinki, Finland)
# Usage: .\HETZNER_DEPLOY.ps1 -Action "deploy" -Environment "production"
#
# Created: May 28, 2026
# ═══════════════════════════════════════════════════════════════════════════════

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("setup", "deploy", "verify", "logs", "restart", "stop", "status")]
    [string]$Action = "status",

    [Parameter(Mandatory = $false)]
    [ValidateSet("production", "staging", "development")]
    [string]$Environment = "production",

    [Parameter(Mandatory = $false)]
    [string]$ServerIP = "46.62.210.251",

    [Parameter(Mandatory = $false)]
    [string]$SSHUser = "root",

    [Parameter(Mandatory = $false)]
    [int]$SSHPort = 22
)

# ═════════════════════════════════════════════════════════════════════════════
# COLOR DEFINITIONS
# ═════════════════════════════════════════════════════════════════════════════

$Colors = @{
    "Success" = [System.ConsoleColor]::Green
    "Error"   = [System.ConsoleColor]::Red
    "Warning" = [System.ConsoleColor]::Yellow
    "Info"    = [System.ConsoleColor]::Cyan
    "Header"  = [System.ConsoleColor]::Magenta
}

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $Color = $Colors[$Type]
    Write-Host "[$Type]" -ForegroundColor $Color -NoNewline
    Write-Host " $Message"
}

# ═════════════════════════════════════════════════════════════════════════════
# SSH HELPER FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-RemoteCommand {
    param(
        [string]$Command,
        [string]$IdentityFile = $null
    )

    $SSHHost = "$SSHUser@$ServerIP"

    Write-Status "Executing: $Command" "Info"

    if ($IdentityFile) {
        ssh -i $IdentityFile -p $SSHPort $SSHHost $Command
    }
    else {
        ssh -p $SSHPort $SSHHost $Command
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Status "Command successful" "Success"
        return $true
    }
    else {
        Write-Status "Command failed (Exit code: $LASTEXITCODE)" "Error"
        return $false
    }
}

# ═════════════════════════════════════════════════════════════════════════════
# SETUP PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Setup {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         CLISONIX CLOUD - HETZNER SETUP PHASE                             ║" -ForegroundColor Magenta
    Write-Host "║         Preparing server for 75+ microservices deployment                 ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""

    Write-Status "Testing SSH connection to $ServerIP" "Info"
    if (-not (Invoke-RemoteCommand "echo 'Connected'" )) {
        Write-Status "Cannot connect to server. Check SSH access." "Error"
        exit 1
    }

    Write-Status "Running deployment setup script on server" "Info"
    Invoke-RemoteCommand "cd /opt/clisonix && bash HETZNER_DEPLOY_SETUP.sh"

    Write-Status "Setup phase completed!" "Success"
}

# ═════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Deploy {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         DEPLOYING 75+ MICROSERVICES TO HETZNER CPX62                     ║" -ForegroundColor Magenta
    Write-Host "║         Environment: $Environment                                        ║" -ForegroundColor Magenta
    Write-Host "║         Server: $ServerIP (Helsinki)                                     ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""

    $EnvFile = ".env.$Environment"

    Write-Status "Phase 1: Verifying prerequisites" "Info"
    Invoke-RemoteCommand "cd /opt/clisonix && docker --version && docker-compose --version"

    Write-Status "Phase 2: Creating Docker network" "Info"
    Invoke-RemoteCommand "docker network create clisonix-net 2>/dev/null || true"

    Write-Status "Phase 3: Starting all 75+ microservices (this may take several minutes...)" "Warning"

    $DeployCmd = @"
cd /opt/clisonix && \
docker-compose -f docker-compose.75-services.yml \
  --env-file $EnvFile \
  up -d
"@

    Invoke-RemoteCommand $DeployCmd

    Write-Status "Phase 4: Waiting for services to stabilize (60 seconds)..." "Info"
    Start-Sleep -Seconds 60

    Write-Status "Deployment phase completed!" "Success"
}

# ═════════════════════════════════════════════════════════════════════════════
# VERIFICATION PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Verify {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         VERIFYING MICROSERVICES DEPLOYMENT                               ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""

    Write-Status "Checking Docker containers status..." "Info"
    Invoke-RemoteCommand "docker-compose -f /opt/clisonix/docker-compose.75-services.yml ps --filter 'status=running' | tail -20"

    Write-Status "Counting running services..." "Info"
    $CountCmd = "docker ps | grep clisonix | wc -l"
    Invoke-RemoteCommand $CountCmd

    Write-Status "Testing core service endpoints..." "Info"

    $Endpoints = @(
        @{Name = "API"; URL = "http://localhost:8000/health" },
        @{Name = "Ocean Core"; URL = "http://localhost:8030/health" },
        @{Name = "ALBA"; URL = "http://localhost:5555/health" },
        @{Name = "ALBI"; URL = "http://localhost:6680/health" },
        @{Name = "Ollama"; URL = "http://localhost:11434" }
    )

    foreach ($Endpoint in $Endpoints) {
        $TestCmd = "curl -s -m 5 '$($Endpoint.URL)' | head -c 50"
        Write-Status "Testing $($Endpoint.Name)..." "Info"
        Invoke-RemoteCommand $TestCmd
    }

    Write-Status "Verification complete!" "Success"
}

# ═════════════════════════════════════════════════════════════════════════════
# STATUS PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Status {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         CLISONIX CLOUD - DEPLOYMENT STATUS                               ║" -ForegroundColor Cyan
    Write-Host "║         Server: $ServerIP                                                ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    $StatusCmd = "cd /opt/clisonix && docker-compose -f docker-compose.75-services.yml ps"
    Invoke-RemoteCommand $StatusCmd

    Write-Status "Service count:" "Info"
    $CountCmd = "docker ps | grep clisonix | wc -l"
    Invoke-RemoteCommand $CountCmd

    Write-Status "System resources:" "Info"
    Invoke-RemoteCommand "free -h && echo '' && df -h /"
}

# ═════════════════════════════════════════════════════════════════════════════
# LOGS PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Logs {
    param([string]$Service = "clisonix-api")

    Write-Status "Fetching logs for $Service..." "Info"
    Invoke-RemoteCommand "docker logs --tail 50 -f $Service"
}

# ═════════════════════════════════════════════════════════════════════════════
# RESTART PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Restart {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║         RESTARTING MICROSERVICES                                          ║" -ForegroundColor Yellow
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""

    Write-Status "Restarting all services..." "Warning"
    Invoke-RemoteCommand "cd /opt/clisonix && docker-compose -f docker-compose.75-services.yml restart"

    Write-Status "Waiting for services to restart (30 seconds)..." "Info"
    Start-Sleep -Seconds 30

    Write-Status "Services restarted!" "Success"
}

# ═════════════════════════════════════════════════════════════════════════════
# STOP PHASE
# ═════════════════════════════════════════════════════════════════════════════

function Invoke-Stop {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║         STOPPING ALL MICROSERVICES                                        ║" -ForegroundColor Yellow
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""

    $Confirm = Read-Host "Are you sure you want to stop all services? (yes/no)"
    if ($Confirm -ne "yes") {
        Write-Status "Cancelled" "Warning"
        return
    }

    Write-Status "Stopping all services..." "Warning"
    Invoke-RemoteCommand "cd /opt/clisonix && docker-compose -f docker-compose.75-services.yml down"

    Write-Status "All services stopped!" "Success"
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     CLISONIX CLOUD - HETZNER DEPLOYMENT ORCHESTRATOR                     ║" -ForegroundColor Magenta
Write-Host "║     Deploying 75+ Microservices to CPX62 (16 vCPU, 32 GB RAM)            ║" -ForegroundColor Magenta
Write-Host "║                                                                           ║" -ForegroundColor Magenta
Write-Host "║     Action: $Action                                                  ║" -ForegroundColor Magenta
Write-Host "║     Environment: $Environment                                            ║" -ForegroundColor Magenta
Write-Host "║     Server: $ServerIP                                                   ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

switch ($Action) {
    "setup" { Invoke-Setup }
    "deploy" {
        Invoke-Setup
        Invoke-Deploy
        Invoke-Verify
    }
    "verify" { Invoke-Verify }
    "logs" { Invoke-Logs -Service "clisonix-api" }
    "restart" { Invoke-Restart }
    "stop" { Invoke-Stop }
    "status" { Invoke-Status }
    default {
        Write-Status "Unknown action: $Action" "Error"
        exit 1
    }
}

Write-Host ""
Write-Host "✓ Operation completed!" -ForegroundColor Green
Write-Host ""
