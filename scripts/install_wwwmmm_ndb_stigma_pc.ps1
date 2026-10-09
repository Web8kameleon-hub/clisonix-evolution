#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Lightweight local installer for WWWMMM + NDB + Stigma stack on Windows PC.

.DESCRIPTION
  Installs only the minimum packages required to run:
  - CLX Hotguard (run_clx_hotguard.py)
  - CLX.I service (clx_i_service.py)
  - Optional Nanogrid build check (Rust)

  Designed for disk-conscious local setup.
#>

param(
    [switch]$WithWebLockCheck,
    [switch]$SkipCargoCheck,
    [switch]$SkipPipUpgrade
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m) { Write-Host "[OK]   $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Info "Creating .venv"
    python -m venv .venv
}

if (-not $SkipPipUpgrade) {
    # Keep upgrade minimal to avoid dependency conflicts with heavy local stacks (e.g., torch).
    Info "Upgrading pip only (safe mode)"
    & $venvPy -m pip install --upgrade pip | Out-Null
}

Info "Installing minimal runtime packages"
& $venvPy -m pip install -r "packages/wwwmmm-ndb-stigma-pc/requirements-min.txt"

Info "Installing CLX AI from local source"
& $venvPy -m pip install -e "sdist/clx-ai"

Info "Verifying critical imports"
& $venvPy -c "import clx,fastapi,httpx,prometheus_client,pydantic; print('OK_IMPORTS')"
Ok "Python runtime ready"

if ($WithWebLockCheck) {
    Info "Checking npm workspace deps (apps/web)"
    if (Test-Path "apps/web/package.json") {
        Push-Location "apps/web"
        npm install --package-lock-only | Out-Null
        Pop-Location
        Ok "apps/web lockfile verified"
    }
    else {
        Warn "apps/web not found, skipping npm lock check"
    }
}
else {
    Info "Skipping npm lock check (use -WithWebLockCheck to enable)"
}

Info "Checking Rust toolchain for Nanogrid"
if ($SkipCargoCheck) {
    Info "Skipping cargo check (requested)"
}
else {
    $hasCargo = $null -ne (Get-Command cargo -ErrorAction SilentlyContinue)
    if ($hasCargo) {
        Push-Location "nanogrid"
        cargo check -p node
        Pop-Location
        Ok "Nanogrid Rust check passed"
    }
    else {
        Warn "cargo not found. Install Rust later if Nanogrid local node is required"
    }
}

Write-Host ""
Ok "Installation complete"
Write-Host "Next:" -ForegroundColor Gray
Write-Host "  1) .\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Gray
Write-Host "  2) pwsh scripts/start_wwwmmm_ndb_stigma_pc.ps1" -ForegroundColor Gray
