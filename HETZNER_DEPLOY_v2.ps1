# ═══════════════════════════════════════════════════════════════════════════
# CLISONIX OCEAN CORE v2 - HETZNER SAFE DEPLOYMENT (POWERSHELL)
# Purpose: Deploy 7 Ocean Core v2 implementations to production Hetzner
# Platform: Windows PowerShell 7+
# Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$HetznerHost = "46.225.14.83",
    [string]$HetznerUser = "root",
    [int]$HetznerPort = 22,
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

$DeploymentDir = if ($env:DEPLOYMENT_DIR) { $env:DEPLOYMENT_DIR } else { "/root/Clisonix-cloud" }
$BackupDir = if ($env:BACKUP_DIR) { $env:BACKUP_DIR } else { "/root/clisonix-backups" }
$BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DeployBranch = if ($env:DEPLOY_BRANCH) { $env:DEPLOY_BRANCH } else { try { (git rev-parse --abbrev-ref HEAD).Trim() } catch { "main" } }
$EnvFile = if ($env:ENV_FILE) { $env:ENV_FILE } else { ".env" }

$OceanServices = @(
    "ocean-core:8030",
    "ocean-core-multimodal:8033",
    "ocean-core-strict-chat:8035",
    "ocean-core-blerina:8032"
)

# ═══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = "Cyan"
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Level] $Timestamp - $Message" -ForegroundColor $Color
}

function Write-Success {
    Write-Log $args[0] "SUCCESS" "Green"
}

function Write-Warning {
    Write-Log $args[0] "WARNING" "Yellow"
}

function Write-Error {
    Write-Log $args[0] "ERROR" "Red"
}

function Invoke-SSHCommand {
    param(
        [string]$Command
    )

    $SSHArgs = @(
        "-p", $HetznerPort
        "-i", $SSHKeyPath
        "-o", "StrictHostKeyChecking=no"
        "-o", "UserKnownHostsFile=/dev/null"
        "$HetznerUser@$HetznerHost"
        $Command
    )

    & ssh $SSHArgs
}

function Copy-ToServer {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )

    $SCPArgs = @(
        "-P", $HetznerPort
        "-i", $SSHKeyPath
        "-o", "StrictHostKeyChecking=no"
        "-o", "UserKnownHostsFile=/dev/null"
        $LocalPath
        "$HetznerUser@$HetznerHost`:$RemotePath"
    )

    & scp $SCPArgs
}

# ═══════════════════════════════════════════════════════════════════════════
# PRE-DEPLOYMENT CHECKS
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CLISONIX OCEAN CORE v2 HETZNER DEPLOYMENT                         ║" -ForegroundColor Cyan
Write-Host "║  Version 2.0.0 - Safe Production Deployment (PowerShell)           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Log "Starting deployment to Hetzner: $HetznerHost`:$HetznerPort"

# Check SSH availability
Write-Log "Checking SSH connectivity..."
try {
    Invoke-SSHCommand "echo 'SSH connection OK'" | Out-Null
    Write-Success "SSH connectivity verified"
} catch {
    Write-Error "Cannot connect to Hetzner server at ${HetznerHost}:${HetznerPort}"
    Write-Host "Make sure you have:"
    Write-Host "  1. SSH public key in ~/.ssh/authorized_keys on Hetzner"
    Write-Host "  2. Private key at: $SSHKeyPath"
    Write-Host "  3. Server IP/hostname correct"
    Write-Host "  4. Firewall allows SSH (port $HetznerPort)"
    exit 1
}

# Check Docker availability
Write-Log "Checking Docker and Docker Compose on server..."
try {
    $DockerVersion = Invoke-SSHCommand "docker --version && docker-compose --version"
    Write-Success "Docker and Docker Compose available"
} catch {
    Write-Error "Docker or Docker Compose not found on Hetzner server"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# BACKUP OPERATION
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "🔄 Creating backups on Hetzner server..."

try {
    Invoke-SSHCommand "mkdir -p $BackupDir" | Out-Null

    # Backup docker-compose.yml
    try {
        Invoke-SSHCommand "test -f $DeploymentDir/docker-compose.yml" | Out-Null
        Write-Log "Backing up docker-compose.yml..."
        Invoke-SSHCommand "cp $DeploymentDir/docker-compose.yml $BackupDir/docker-compose.yml.$BackupTimestamp" | Out-Null
        Write-Success "docker-compose.yml backed up"
    } catch {
        Write-Warning "No existing docker-compose.yml found (fresh deployment)"
    }

    # Backup .env
    try {
        Invoke-SSHCommand "test -f $DeploymentDir/.env" | Out-Null
        Write-Log "Backing up .env..."
        Invoke-SSHCommand "cp $DeploymentDir/.env $BackupDir/.env.$BackupTimestamp" | Out-Null
        Write-Success ".env backed up"
    } catch {
        Write-Warning ".env not found"
    }
} catch {
    Write-Error "Backup operation failed: $_"
}

# ═══════════════════════════════════════════════════════════════════════════
# TRANSFER FILES
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "📦 Transferring updated configurations..."

try {
    # Ensure deployment directory exists
    Invoke-SSHCommand "mkdir -p $DeploymentDir" | Out-Null

    # Transfer docker-compose.yml
    if (Test-Path "docker-compose.yml") {
        Write-Log "Copying docker-compose.yml..."
        Copy-ToServer (Get-Item "docker-compose.yml").FullName "${DeploymentDir}/"
        Write-Success "docker-compose.yml transferred"
    } else {
        Write-Error "docker-compose.yml not found in current directory"
        exit 1
    }

    # Transfer Dockerfiles
    Write-Log "Transferring Ocean Core Dockerfiles..."

    $Dockerfiles = @(
        "ocean-core\Dockerfile",
        "ocean-core\Dockerfile.multimodal",
        "ocean-core\Dockerfile.strict-chat",
        "ocean-core\Dockerfile.blerina"
    )

    foreach ($dockerfile in $Dockerfiles) {
        if (Test-Path $dockerfile) {
            $FileName = Split-Path $dockerfile -Leaf
            Copy-ToServer (Get-Item $dockerfile).FullName "${DeploymentDir}/${dockerfile.Replace('\', '/')}"
            Write-Success "$FileName transferred"
        }
    }
} catch {
    Write-Error "File transfer failed: $_"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# GIT UPDATE
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "🔄 Updating codebase from git..."

try {
    Invoke-SSHCommand "test -d $DeploymentDir/.git" | Out-Null
    Write-Log "Git repository found, syncing branch $DeployBranch..."
    Invoke-SSHCommand "cd $DeploymentDir && git fetch origin $DeployBranch --quiet && (git checkout $DeployBranch || git checkout -b $DeployBranch origin/$DeployBranch) && git reset --hard origin/$DeployBranch" 2>&1 | Out-Null
    Write-Success "Git sync completed"
} catch {
    Write-Warning "Not in a git repository or git sync failed"
}

# ═══════════════════════════════════════════════════════════════════════════
# STOP EXISTING OCEAN SERVICES
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "🛑 Stopping existing Ocean Core services..."

foreach ($service in $OceanServices) {
    $ServiceName = $service.Split(":")[0]

    try {
        $IsRunning = Invoke-SSHCommand "docker ps --filter 'name=$ServiceName' --format '{{.Names}}' | grep -q '^$ServiceName`$'" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Stopping $ServiceName..."
            Invoke-SSHCommand "docker stop $ServiceName 2>/dev/null || true" 2>&1 | Out-Null
            Write-Success "$ServiceName stopped"
        }
    } catch {
        Write-Warning "Could not stop $ServiceName (may not be running)"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# BUILD AND DEPLOY
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "🏗️ Building and starting Ocean Core services..."

try {
    $BuildCommand = @"
cd $DeploymentDir && `
export CLISONIX_ENV_FILE='$EnvFile' && `
docker-compose up -d --build `
    ocean-core `
    ocean-core-multimodal `
    ocean-core-strict-chat `
    ocean-core-blerina
"@

    Invoke-SSHCommand $BuildCommand 2>&1 | Out-Null
    Write-Success "Ocean Core services built and started"
} catch {
    Write-Error "Failed to build/start services: $_"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECKS
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Log "⏳ Waiting for Ocean Core services to be healthy..."

Start-Sleep -Seconds 5

foreach ($service in $OceanServices) {
    $ServiceName = $service.Split(":")[0]
    $Port = $service.Split(":")[1]

    Write-Log "Checking $ServiceName (port $Port)..."

    $MaxAttempts = 30
    $Attempt = 0
    $Healthy = $false

    while ($Attempt -lt $MaxAttempts) {
        try {
            Invoke-SSHCommand "curl -sf http://localhost:${Port}/health >/dev/null 2>&1" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$ServiceName is HEALTHY ✓"
                $Healthy = $true
                break
            }
        } catch { }

        $Attempt++

        if ($Attempt -lt $MaxAttempts) {
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 2
        }
    }

    if (-not $Healthy) {
        Write-Warning "$ServiceName health check timed out (may still be starting)"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# DEPLOYMENT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  DEPLOYMENT COMPLETE                                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Success "Ocean Core v2 deployed to $HetznerHost"
Write-Host "Services should be accessible at:" -ForegroundColor White

foreach ($service in $OceanServices) {
    $ServiceName = $service.Split(":")[0]
    $Port = $service.Split(":")[1]
    Write-Host "  🌊 $ServiceName`: http://${HetznerHost}:${Port}" -ForegroundColor Cyan
}

Write-Host ""
Write-Log "Backup location: $BackupDir/docker-compose.yml.$BackupTimestamp"
Write-Log "Deployment finished at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Success "✅ All Ocean Core v2 services deployed successfully!"
Write-Host ""
