#!/usr/bin/env pwsh
# 🚀 CLISONIX CLOUD - SUPER UNIVERSAL LAUNCHER
# Opens each service in separate PowerShell windows to see errors live

param(
    [ValidateSet('full', 'docker', 'services', 'monitoring', 'agents', 'all')]
    [string]$Mode = 'full',
    [switch]$Clean,
    [switch]$DryRun
)

$Root = 'C:\Users\Admin\Desktop\neurosonix-cloud'
Set-Location $Root

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  🚀 CLISONIX CLOUD - script_all.ps1 🚀                  ║" -ForegroundColor Magenta
Write-Host "║     Each Service Opens in NEW WINDOW (See Errors)       ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

$Services = @{
    'docker' = @{Name='🐳 Docker Stack'; Cmd='docker-compose up'; Group='Infrastructure'}
    'alba' = @{Name='📡 ALBA (5555)'; Cmd='python alba_core.py'; Group='Microservices'}
    'albi' = @{Name='🧠 ALBI (6680)'; Cmd='python albi_core.py'; Group='Microservices'}
    'jona' = @{Name='🎵 JONA (7777)'; Cmd='python jona_service_7777.py'; Group='Microservices'}
    'api' = @{Name='⚡ API (8000)'; Cmd='python alba_api_server.py'; Group='Core'}
    'frontend' = @{Name='🎨 Frontend (3000)'; Cmd='cd apps\web; npm run dev'; Group='Core'}
    'prometheus' = @{Name='📊 Prometheus'; Cmd='docker-compose up prometheus'; Group='Monitoring'}
    'grafana' = @{Name='📈 Grafana (3001)'; Cmd='docker-compose up grafana'; Group='Monitoring'}
    'victoria' = @{Name='⏱️ Victoria'; Cmd='docker-compose up victoria-metrics'; Group='Monitoring'}
    'cycle' = @{Name='♻️ Cycle Engine'; Cmd='python cycle_engine.py'; Group='Advanced'}
    'mesh' = @{Name='🕸️ Mesh Network'; Cmd='python mesh_cluster_startup.py'; Group='Advanced'}
    'agiem' = @{Name='🤖 AGIEM'; Cmd='python agiem_core.py'; Group='Advanced'}
    'asi' = @{Name='⚙️ ASI System'; Cmd='python asi_realtime_engine.py'; Group='Advanced'}
    'blerina' = @{Name='🔄 Blerina'; Cmd='python blerina_reformatter.py'; Group='Advanced'}
    'balance' = @{Name='⚖️ Balance'; Cmd='python distributed_pulse_balancer.py'; Group='Orchestration'}
    'saas' = @{Name='🎛️ SaaS Orchestrator'; Cmd='python saas_services_orchestrator.py'; Group='Orchestration'}
    'slack' = @{Name='💬 Slack'; Cmd='python slack_integration_service.py'; Group='Integration'}
}

if ($Clean) {
    Write-Host "🧹 Cleaning up processes..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -match 'python|node|npm'} | Stop-Process -Force -EA SilentlyContinue
    docker-compose down -v 2>$null
    Start-Sleep -Seconds 2
}

$groups = switch ($Mode) {
    'docker' { @('Infrastructure') }
    'services' { @('Core', 'Microservices') }
    'monitoring' { @('Monitoring') }
    'agents' { @('Advanced', 'Orchestration', 'Integration') }
    'all' { @('Infrastructure', 'Core', 'Microservices', 'Monitoring', 'Advanced', 'Orchestration', 'Integration') }
    default { @('Infrastructure', 'Core', 'Microservices', 'Monitoring') }
}

$count = 0
foreach ($group in $groups) {
    Write-Host "`n█ $group Services" -ForegroundColor Blue
    
    $Services.GetEnumerator() | Where-Object {$_.Value.Group -eq $group} | ForEach-Object {
        Write-Host "  ▶️  $($_.Value.Name)" -ForegroundColor Green
        
        if (-not $DryRun) {
            $cmd = $_.Value.Cmd
            Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$Root'; Write-Host '════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  $($_.Value.Name)' -ForegroundColor Cyan; Write-Host '════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; $cmd`""
            Start-Sleep -Milliseconds 600
        }
        $count++
    }
}

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ Started $count services in separate windows!          ║" -ForegroundColor Green
Write-Host "║  🌐 http://localhost:3000 (Frontend)                    ║" -ForegroundColor Cyan
Write-Host "║  📊 http://localhost:3001 (Grafana)                     ║" -ForegroundColor Cyan
Write-Host "║  ⚡ http://localhost:8000/docs (API)                    ║" -ForegroundColor Cyan
Write-Host "║  💡 Close windows to stop services                      ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
