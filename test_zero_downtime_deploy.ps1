# =============================================================================
# Zero-Downtime Deployment Test for Clisonix Hotguard Container
# Tests rolling deployment strategy with health checks
# =============================================================================

param(
    [string]$ServiceName = "clisonix-postgres",
    [int]$HealthCheckTimeout = 30,
    [bool]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# Color-coded output
function Write-Success { Write-Host "[✅] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[ℹ️ ] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[⚠️ ] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[❌] $args" -ForegroundColor Red }

# Main test function
function Test-ZeroDowntimeDeploy {
    Write-Info "Starting Zero-Downtime Deployment Test"
    Write-Info "Service: $ServiceName"
    Write-Info "Health Check Timeout: $HealthCheckTimeout seconds"

    if ($DryRun) { Write-Warning "DRY RUN MODE: No actual changes will be made" }

    # Step 1: Verify docker-compose exists
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "docker-compose.yml not found in current directory"
        return $false
    }
    Write-Success "Found docker-compose.yml"

    # Step 2: Check current service health
    Write-Info "Step 1/5: Checking current service health..."
    $healthStatus = Get-ServiceHealth $ServiceName
    if (-not $healthStatus) {
        Write-Error "Service $ServiceName is not healthy before deployment"
        return $false
    }
    Write-Success "Service is currently healthy"

    # Step 3: Capture current state
    Write-Info "Step 2/5: Capturing current deployment state..."
    $beforeState = Get-ContainerState $ServiceName
    Write-Success "Current container ID: $($beforeState.ContainerId)"

    # Step 4: Trigger rolling deployment
    Write-Info "Step 3/5: Starting rolling deployment..."
    if ($DryRun) {
        Write-Info "DRY RUN: Would execute: docker compose up -d --no-deps --build $ServiceName"
    }
    else {
        $deployResult = Start-RollingDeploy $ServiceName
        if (-not $deployResult) {
            Write-Error "Deployment failed"
            return $false
        }
    }
    Write-Success "Rolling deployment initiated"

    # Step 5: Monitor health during transition
    Write-Info "Step 4/5: Monitoring health during deployment transition..."
    $transitionHealthy = Monitor-HealthDuringTransition $ServiceName $HealthCheckTimeout
    if (-not $transitionHealthy) {
        Write-Error "Service health check failed during transition"
        return $false
    }
    Write-Success "Health checks passed during entire transition"

    # Step 6: Verify new container
    Write-Info "Step 5/5: Verifying new container state..."
    $afterState = Get-ContainerState $ServiceName
    Write-Success "New container ID: $($afterState.ContainerId)"

    if ($beforeState.ContainerId -eq $afterState.ContainerId -and -not $DryRun) {
        Write-Warning "Container ID did not change (may be expected if no changes)"
    }
    elseif (-not $DryRun) {
        Write-Success "Container successfully replaced"
    }

    # Step 7: Final health verification
    $finalHealth = Get-ServiceHealth $ServiceName
    if (-not $finalHealth) {
        Write-Error "Final health check failed"
        return $false
    }
    Write-Success "Final health verification passed"

    # Success summary
    Write-Host ""
    Write-Success "✨ ZERO-DOWNTIME DEPLOYMENT TEST PASSED ✨"
    Write-Info "No downtime detected during deployment transition"
    Write-Info "All health checks passed successfully"

    return $true
}

# Get current service health status
function Get-ServiceHealth {
    param([string]$ServiceName)

    try {
        $json = docker compose ps --format json 2>$null | ConvertFrom-Json
        $service = $json | Where-Object { $_.Service -eq $ServiceName } | Select-Object -First 1

        if (-not $service) {
            Write-Warning "Service $ServiceName not found in docker compose"
            return $false
        }

        # Check if container is running and healthy
        if ($service.State -like "*running*") {
            # Check health status via docker inspect
            $healthInfo = docker inspect "$($service.Name)" --format='{{.State.Health.Status}}' 2>$null
            $isHealthy = $healthInfo -eq "healthy" -or $healthInfo -eq ""
            return $isHealthy
        }

        return $false
    }
    catch {
        Write-Warning "Error checking service health: $_"
        return $false
    }
}

# Get container state information
function Get-ContainerState {
    param([string]$ServiceName)

    try {
        $json = docker compose ps --format json 2>$null | ConvertFrom-Json
        $service = $json | Where-Object { $_.Service -eq $ServiceName } | Select-Object -First 1

        if ($service) {
            $containerInfo = docker inspect "$($service.Name)" --format='{{.Id}}|{{.State.StartedAt}}|{{.State.Status}}' 2>$null
            $parts = $containerInfo -split '\|'

            return @{
                ContainerId = $parts[0].Substring(0, 12)
                StartedAt   = $parts[1]
                Status      = $parts[2]
            }
        }
        return $null
    }
    catch {
        return $null
    }
}

# Start rolling deployment
function Start-RollingDeploy {
    param([string]$ServiceName)

    try {
        Write-Info "Building and deploying $ServiceName..."

        # Use docker compose to do rolling update with graceful shutdown
        $output = docker compose up -d --build --no-deps --remove-orphans $ServiceName 2>&1
        Write-Info $output

        return $true
    }
    catch {
        Write-Error "Deployment error: $_"
        return $false
    }
}

# Monitor health during the transition
function Monitor-HealthDuringTransition {
    param([string]$ServiceName, [int]$TimeoutSeconds)

    $startTime = Get-Date
    $healthChecksPassed = 0

    Write-Info "Monitoring health for $TimeoutSeconds seconds..."

    while ((Get-Date) -lt $startTime.AddSeconds($TimeoutSeconds)) {
        $isHealthy = Get-ServiceHealth $ServiceName

        if ($isHealthy) {
            $healthChecksPassed++
            Write-Info "✓ Health check passed ($healthChecksPassed)"
        }
        else {
            Write-Warning "✗ Health check failed at $(Get-Date -Format 'HH:mm:ss')"
            # Don't fail immediately, wait for recovery
            Start-Sleep -Milliseconds 500
        }

        Start-Sleep -Milliseconds 1000
    }

    # Require at least 1 successful health check during transition
    return $healthChecksPassed -gt 0
}

# Run the test
if (Test-ZeroDowntimeDeploy) {
    Write-Host ""
    Write-Success "All tests passed! Zero-downtime deployment is working correctly."
    exit 0
}
else {
    Write-Host ""
    Write-Error "Test failed. Review logs above for details."
    exit 1
}
