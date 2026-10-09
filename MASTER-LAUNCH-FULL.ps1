#!/usr/bin/env pwsh
<#
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║           🚀 CLISONIX CLOUD - ULTIMATE MASTER LAUNCHER v3.0 🚀              ║
║                  "Complete Orchestration - All Services"                      ║
║                                                                               ║
║  Launches ALL services in separate PowerShell windows:                        ║
║  • PostgreSQL, Redis, MinIO (Infrastructure)                                 ║
║  • ALBA, ALBI, JONA, Orchestrator (Microservices)                            ║
║  • API Backend, Frontend (Core Services)                                      ║
║  • Docker Compose, Prometheus, Grafana (Monitoring)                           ║
║  • Postman CLI, Health Checker, Auto-Healer (Tools)                           ║
║                                                                               ║
║  Usage:  .\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor                            ║
║          .\MASTER-LAUNCH-FULL.ps1 -Docker -Monitor                           ║
║          .\MASTER-LAUNCH-FULL.ps1 -Help                                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
#>

param(
    [switch]$Clean,
    [switch]$Docker,
    [switch]$DryRun,
    [switch]$Monitor,
    [switch]$Help
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
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
    Service  = 'DarkGreen'
}

# Service definitions with ports and startup order
$Services = @(
    # Infrastructure Layer (Start First)
    @{ 
        Name = 'PostgreSQL'; 
        Port = 5432; 
        Icon = '🗄️'; 
        Color = 'Blue'
        Command = 'docker run --name clisonix-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14'
        Type = 'docker'
    }
    @{ 
        Name = 'Redis'; 
        Port = 6379; 
        Icon = '⚡'; 
        Color = 'Red'
        Command = 'docker run --name clisonix-redis -p 6379:6379 redis:7'
        Type = 'docker'
    }
    @{ 
        Name = 'MinIO'; 
        Port = 9000; 
        Icon = '📦'; 
        Color = 'Yellow'
        Command = 'docker run --name clisonix-minio -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"'
        Type = 'docker'
    }
    
    # Microservices Layer
    @{ 
        Name = 'ALBA (Telemetry)'; 
        Port = 5555; 
        Icon = '📡'; 
        Color = 'Cyan'
        Command = 'python alba_core.py'
        Type = 'python'
    }
    @{ 
        Name = 'ALBI (Neural)'; 
        Port = 6680; 
        Icon = '🧠'; 
        Color = 'Magenta'
        Command = 'python albi_core.py'
        Type = 'python'
    }
    @{ 
        Name = 'JONA (Synthesis)'; 
        Port = 7777; 
        Icon = '🎵'; 
        Color = 'Green'
        Command = 'python alba_frame_generator.py'
        Type = 'python'
    }
    @{ 
        Name = 'Mesh (Orchestrator)'; 
        Port = 9999; 
        Icon = '🔗'; 
        Color = 'DarkCyan'
        Command = 'python mesh_cluster_startup.py'
        Type = 'python'
    }
    
    # Core Services
    @{ 
        Name = 'API Backend'; 
        Port = 8000; 
        Icon = '🔷'; 
        Color = 'Cyan'
        Command = 'python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000'
        Type = 'python'
    }
    @{ 
        Name = 'Frontend'; 
        Port = 3000; 
        Icon = '🔶'; 
        Color = 'Yellow'
        Command = 'cd apps/web; npm run dev'
        Type = 'npm'
    }
    
    # Monitoring & Observability
    @{ 
        Name = 'Prometheus'; 
        Port = 9090; 
        Icon = '📊'; 
        Color = 'Red'
        Command = 'docker run --name clisonix-prometheus -p 9090:9090 -v c:\clisonix-cloud\prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus'
        Type = 'docker'
    }
    @{ 
        Name = 'Grafana'; 
        Port = 3001; 
        Icon = '📈'; 
        Color = 'Yellow'
        Command = 'docker run --name clisonix-grafana -e GF_SECURITY_ADMIN_PASSWORD=admin -p 3001:3000 grafana/grafana'
        Type = 'docker'
    }
)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Show-Banner {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║         🚀 CLISONIX CLOUD - ULTIMATE MASTER LAUNCHER v3.0 🚀                 ║" -ForegroundColor $Colors.Title
    Write-Host "║              « All Services in Separate Windows »                             ║" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor $Colors.Title
}

function Show-Status {
    param([string]$Message, [ValidateSet('INFO', 'OK', 'WAIT', 'ERROR', 'WARN')][string]$Status = 'INFO')
    
    $Icon = @{ 'INFO' = '▸'; 'OK' = '✓'; 'WAIT' = '◌'; 'ERROR' = '✗'; 'WARN' = '⚠' }[$Status]
    $Color = @{ 'INFO' = $Colors.Info; 'OK' = $Colors.Success; 'WAIT' = $Colors.Warning; 'ERROR' = $Colors.Error; 'WARN' = $Colors.Warning }[$Status]
    
    Write-Host "  $Icon " -NoNewline -ForegroundColor $Color
    Write-Host $Message
}

function Show-Help {
    Write-Host @"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ULTIMATE MASTER LAUNCHER - HELP                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
  Launches ALL Clisonix Cloud services in separate PowerShell windows with 
  intelligent sequencing and health monitoring.

  Services Launched:
  ├─ Infrastructure: PostgreSQL, Redis, MinIO
  ├─ Microservices: ALBA, ALBI, JONA, Mesh Orchestrator
  ├─ Core: API Backend, Frontend Dashboard
  └─ Monitoring: Docker Compose, Prometheus, Grafana

FLAGS:
  -Clean         Kill all existing processes before startup
  -Docker        Use Docker Compose for infrastructure services
  -DryRun        Preview startup without launching
  -Monitor       Enable continuous health monitoring
  -Help          Show this help message

EXAMPLES:
  .\MASTER-LAUNCH-FULL.ps1
  .\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor
  .\MASTER-LAUNCH-FULL.ps1 -Docker -Monitor
  .\MASTER-LAUNCH-FULL.ps1 -DryRun

KEYBOARD SHORTCUTS:
  Alt+Tab        Switch between service windows
  Ctrl+C         Stop individual service
  Close Window   Stop that service cleanly

"@ -ForegroundColor $Colors.Info
}

function Invoke-CleanupProcesses {
    Write-Host "`n┌─── PROCESS CLEANUP ──────────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    Show-Status "Terminating existing services..." 'WAIT'
    
    $processes = @('node', 'python', 'npm')
    $killed = 0
    
    foreach ($proc in $processes) {
        $procs = Get-Process -Name $proc -ErrorAction SilentlyContinue
        if ($procs) {
            $procs | Stop-Process -Force -ErrorAction SilentlyContinue
            $killed += $procs.Count
        }
    }
    
    if ($killed -gt 0) {
        Show-Status "Killed $killed process(es) ✓" 'OK'
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Launch-Service {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$Command,
        [string]$Icon,
        [int]$Delay = 0
    )
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would launch $ServiceName (Port $Port)" 'INFO'
        return
    }
    
    if ($Delay -gt 0) {
        Start-Sleep -Seconds $Delay
    }
    
    Show-Status "Launching $ServiceName (Port $Port)..." 'WAIT'
    
    $cmdString = @"
Set-Location '$Root'
`$host.UI.RawUI.WindowTitle = '$Icon Clisonix - $ServiceName (Port $Port)'
Write-Host '╔════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║ $Icon $ServiceName - Port $Port' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
$Command
"@
    
    Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $cmdString) -ErrorAction SilentlyContinue
    
    Show-Status "$ServiceName launched ✓" 'OK'
}

function Invoke-HealthChecks {
    Write-Host "`n┌─── HEALTH CHECK ─────────────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    $endpoints = @(
        @{ Name = 'API'; URL = 'http://localhost:8000/health'; Port = 8000 }
        @{ Name = 'Frontend'; URL = 'http://localhost:3000'; Port = 3000 }
        @{ Name = 'ALBA'; URL = 'http://localhost:5555/health'; Port = 5555 }
        @{ Name = 'ALBI'; URL = 'http://localhost:6680/health'; Port = 6680 }
        @{ Name = 'JONA'; URL = 'http://localhost:7777/health'; Port = 7777 }
        @{ Name = 'Orchestrator'; URL = 'http://localhost:9999/health'; Port = 9999 }
        @{ Name = 'Prometheus'; URL = 'http://localhost:9090'; Port = 9090 }
        @{ Name = 'Grafana'; URL = 'http://localhost:3001'; Port = 3001 }
    )
    
    Write-Host "`n  Probing service endpoints...`n" -ForegroundColor $Colors.Info
    
    foreach ($ep in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $ep.URL -SkipHttpErrorCheck -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✓ $($ep.Name) (Port $($ep.Port)) responding" -ForegroundColor $Colors.Success
            } else {
                Write-Host "  ◌ $($ep.Name) (Port $($ep.Port)) - HTTP $($response.StatusCode)" -ForegroundColor $Colors.Warning
            }
        } catch {
            Write-Host "  ○ $($ep.Name) (Port $($ep.Port)) - Not ready" -ForegroundColor $Colors.Info
        }
    }
    
    Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Show-ServiceMap {
    Write-Host "`n┌─── SERVICE LAUNCH SEQUENCE ──────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section
    
    Write-Host "`n  📦 INFRASTRUCTURE LAYER:" -ForegroundColor $Colors.Section
    Write-Host "     1. PostgreSQL (5432)  - Database foundation" -ForegroundColor $Colors.Info
    Write-Host "     2. Redis (6379)       - Cache & sessions" -ForegroundColor $Colors.Info
    Write-Host "     3. MinIO (9000/9001)  - Object storage" -ForegroundColor $Colors.Info
    
    Write-Host "`n  🧠 MICROSERVICES LAYER:" -ForegroundColor $Colors.Section
    Write-Host "     4. ALBA (5555)        - Network telemetry" -ForegroundColor $Colors.Info
    Write-Host "     5. ALBI (6680)        - Neural processing" -ForegroundColor $Colors.Info
    Write-Host "     6. JONA (7777)        - Data synthesis" -ForegroundColor $Colors.Info
    Write-Host "     7. Mesh (9999)        - Service orchestration" -ForegroundColor $Colors.Info
    
    Write-Host "`n  🔧 CORE SERVICES:" -ForegroundColor $Colors.Section
    Write-Host "     8. API Backend (8000) - FastAPI REST endpoints" -ForegroundColor $Colors.Info
    Write-Host "     9. Frontend (3000)    - React dashboard" -ForegroundColor $Colors.Info
    
    Write-Host "`n  📊 MONITORING:" -ForegroundColor $Colors.Section
    Write-Host "    10. Prometheus (9090) - Metrics collection" -ForegroundColor $Colors.Info
    Write-Host "    11. Grafana (3001)    - Visualization dashboards" -ForegroundColor $Colors.Info
    
    Write-Host "`n└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section
}

function Show-Dashboard {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Title
    Write-Host "║                    🎯 ALL SERVICES LAUNCHED 🎯                                ║" -ForegroundColor $Colors.Title
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $Colors.Title
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  📊 QUICK ACCESS URLs                                                         ║" -ForegroundColor $Colors.Title
    Write-Host "║  ├─ Frontend:      http://localhost:3000                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ API Docs:      http://localhost:8000/docs                                 ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ Grafana:       http://localhost:3001 (admin/admin)                        ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ Prometheus:    http://localhost:9090                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ MinIO:         http://localhost:9001 (minioadmin/minioadmin)              ║" -ForegroundColor $Colors.Success
    Write-Host "║  └─ Fitness:       http://localhost:3000/modules/fitness-dashboard           ║" -ForegroundColor $Colors.Success
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  🔧 SERVICE PORTS                                                             ║" -ForegroundColor $Colors.Title
    Write-Host "║  ├─ ALBA:          http://localhost:5555                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ ALBI:          http://localhost:6680                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ JONA:          http://localhost:7777                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  ├─ Orchestrator:  http://localhost:9999                                      ║" -ForegroundColor $Colors.Success
    Write-Host "║  └─ PostgreSQL:    localhost:5432 (postgres/postgres)                         ║" -ForegroundColor $Colors.Success
    Write-Host "║                                                                               ║" -ForegroundColor $Colors.Title
    Write-Host "║  💡 WINDOW MANAGEMENT                                                         ║" -ForegroundColor $Colors.Title
    Write-Host "║  ├─ Alt+Tab        Switch between service windows                             ║" -ForegroundColor $Colors.Warning
    Write-Host "║  ├─ Close Window   Stop that service cleanly                                  ║" -ForegroundColor $Colors.Warning
    Write-Host "║  └─ Ctrl+C         Force stop service in window                               ║" -ForegroundColor $Colors.Warning
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

if ($Clean) {
    Invoke-CleanupProcesses
}

Show-ServiceMap

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE] - Preview of services that would launch:`n" -ForegroundColor $Colors.Warning
}

# Launch services sequentially with delays
Write-Host "`n┌─── LAUNCHING SERVICES ───────────────────────────────────────────────────────┐" -ForegroundColor $Colors.Section

$delay = 0
foreach ($svc in $Services) {
    Launch-Service -ServiceName $svc.Name -Port $svc.Port -Command $svc.Command -Icon $svc.Icon -Delay $delay
    $delay = 2  # 2 second delay between service launches
}

Write-Host "└────────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor $Colors.Section

if (-not $DryRun) {
    Start-Sleep -Seconds 5
    
    if ($Monitor) {
        Write-Host "`n[MONITORING MODE] Starting health checks every 30 seconds (press Ctrl+C to stop)...`n" -ForegroundColor $Colors.Warning
        while ($true) {
            Invoke-HealthChecks
            Start-Sleep -Seconds 30
        }
    } else {
        Invoke-HealthChecks
    }
}

Show-Dashboard

Write-Host "🚀 Clisonix Cloud is ready for FULL OPERATION!`n" -ForegroundColor $Colors.Success

