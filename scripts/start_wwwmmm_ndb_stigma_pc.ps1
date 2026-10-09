#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Start lightweight local WWWMMM + NDB + Stigma runtime on PC.

.DESCRIPTION
  Starts:
  - CLX Hotguard (background)
  - CLX.I service (foreground)
  Optional:
  - Nanogrid node in separate shell command (shown as hint)
#>

param(
  [int]$ClxIPort = 8091,
  [switch]$NoHotguard,
  [switch]$WithNanogridHint
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  throw "Missing .venv. Run: pwsh scripts/install_wwwmmm_ndb_stigma_pc.ps1"
}

if (-not $NoHotguard) {
  Write-Host "[INFO] Starting CLX Hotguard in background" -ForegroundColor Cyan
  $hotguardArgs = @(
    "run_clx_hotguard.py",
    "--interval-seconds", "120",
    "--workspace-root", "$repoRoot",
    "--memory-dir", "$repoRoot/.clx_ops_2min"
  )
  $hotguard = Start-Process -FilePath $venvPy -ArgumentList $hotguardArgs -PassThru
  Write-Host "[OK] Hotguard PID: $($hotguard.Id)" -ForegroundColor Green
}
else {
  Write-Host "[INFO] Hotguard disabled (NoHotguard=true)" -ForegroundColor Yellow
}

$portBusy = Get-NetTCPConnection -LocalPort $ClxIPort -ErrorAction SilentlyContinue
if ($portBusy) {
  throw "Port $ClxIPort is already in use. Stop conflicting process or pass a different -ClxIPort."
}

Write-Host "[INFO] Starting CLX.I API on http://127.0.0.1:$ClxIPort" -ForegroundColor Cyan
$env:CLXI_MODE = "wwwmmm_ndb"
$env:CLXI_SELFLEARNING_ENABLED = "1"
$env:CLXI_MIRROR_FILE = ".clx_i/mirror_events.jsonl"
$env:CLXI_SELFLEARNING_FILE = ".clx_i/selflearning_events.jsonl"
$env:CLXI_TIMEOUT_SECONDS = "60"

& $venvPy -m uvicorn clx_i_service:app --host 127.0.0.1 --port $ClxIPort

Write-Host ""
Write-Host "[INFO] CLX.I stopped. Hotguard may still run in background." -ForegroundColor Yellow
if (-not $NoHotguard) {
  Write-Host "[INFO] To stop Hotguard: Stop-Process -Id $($hotguard.Id)" -ForegroundColor Yellow
}
if ($WithNanogridHint) {
  Write-Host "[INFO] Optional Nanogrid start: cd nanogrid; cargo run -p node" -ForegroundColor Gray
}
