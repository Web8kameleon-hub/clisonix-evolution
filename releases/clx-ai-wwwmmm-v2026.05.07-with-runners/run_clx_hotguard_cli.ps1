#!/usr/bin/env pwsh
<#
.SYNOPSIS
    CLX AI Hotguard Runner — 2-Minute Learning Cycle
    Starts the 2-minute hotguard learning mode with safe atomic persistence.

.DESCRIPTION
    This launcher runs CLX AI ecosystem_ops_10min.py with:
    - 120-second cycle intervals (2 minutes per cycle)
    - Atomic JSON writes with fsync() for power-loss safety
    - Unlimited duration (runs continuously)
    - Safe workspace isolation

    Usage: 
        pwsh run_clx_hotguard_cli.ps1

.NOTES
    Requires: Python 3.13+, CLX AI package installed
    Author: Clisonix Cloud
    License: Apache-2.0
#>

$ErrorActionPreference = "Stop"

# Detect venv
$venvPath = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    $venvPath = "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPath)) {
        Write-Error "Virtual environment not found. Run: python -m venv .venv && .venv\Scripts\Activate.ps1"
        exit 1
    }
}

# Verify CLX AI is installed
Write-Host "🔍 Checking CLX AI installation..." -ForegroundColor Cyan
& $venvPath -c "import clx; print(f'✅ CLX AI v{clx.__version__ if hasattr(clx, \"__version__\") else \"0.1.0\"} loaded')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "CLX AI not installed. Run: pip install -e sdist/clx-ai"
    exit 1
}

# Run hotguard via Python module interface
Write-Host "🚀 Starting CLX AI Hotguard (2-min cycles)..." -ForegroundColor Green
Write-Host "📊 Workspace: $PWD" -ForegroundColor Gray
Write-Host "⏱️  Interval: 120 seconds (2 minutes)" -ForegroundColor Gray
Write-Host "🔄 Duration: Unlimited (Ctrl+C to stop)" -ForegroundColor Gray
Write-Host ""

& $venvPath -m clx.cli.hotguard `
    --interval-seconds 120 `
    --workspace-root "$PWD" `
    --memory-dir "$PWD\.clx_ops_2min" `
    --report-file "$PWD\.clx_ops_2min\final_report.json" `
    --local-max-files 220 `
    --local-max-bytes 10000 `
    --code-max-files 70 `
    --code-max-bytes 14000

Write-Host ""
Write-Host "✅ Hotguard completed or stopped" -ForegroundColor Green
Write-Host "📄 Report saved to: .clx_ops_2min\final_report.json"
