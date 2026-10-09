#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Repeatable install-test-metrics run for WWWMMM/NDB/Stigma local profile.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
$reportDir = Join-Path $repoRoot "reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = Join-Path $reportDir "wwwmmm_ndb_install_test_metrics_$ts.json"

function Invoke-LatencyProbe([string]$url, [int]$count) {
  $samples = @()
  for ($i=0; $i -lt $count; $i++) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
      Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 5 | Out-Null
    } catch {
      # keep sample to show timeout/fail duration cost
    }
    $sw.Stop()
    $samples += $sw.Elapsed.TotalMilliseconds
  }

  $avg = ($samples | Measure-Object -Average).Average
  $min = ($samples | Measure-Object -Minimum).Minimum
  $max = ($samples | Measure-Object -Maximum).Maximum
  $sorted = $samples | Sort-Object
  $p95Index = [Math]::Max(0, [Math]::Ceiling($sorted.Count * 0.95) - 1)
  $p95 = $sorted[$p95Index]

  return [pscustomobject]@{
    avg_ms = [math]::Round($avg,2)
    min_ms = [math]::Round($min,2)
    max_ms = [math]::Round($max,2)
    p95_ms = [math]::Round($p95,2)
    count = $count
  }
}

function Get-DirSize([string]$path) {
  if (-not (Test-Path $path)) {
    return [pscustomobject]@{ path=$path; size_mb=0; size_gb=0 }
  }
  $sum = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
  if (-not $sum) { $sum = 0 }
  return [pscustomobject]@{
    path = $path
    size_mb = [math]::Round($sum/1MB,2)
    size_gb = [math]::Round($sum/1GB,3)
  }
}

$results = [ordered]@{}
$results.timestamp = (Get-Date).ToString("o")
$results.repo_root = "$repoRoot"

# 1) Install
$installSw = [System.Diagnostics.Stopwatch]::StartNew()
& pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_wwwmmm_ndb_stigma_pc.ps1 -SkipCargoCheck
$installSw.Stop()
$results.install = [ordered]@{
  ok = $LASTEXITCODE -eq 0
  duration_sec = [math]::Round($installSw.Elapsed.TotalSeconds,2)
}

# 2) Tests
$testSw = [System.Diagnostics.Stopwatch]::StartNew()
& $venvPy -m pytest kloud-soc-clean/tests/unit/test_ocean_core_xlc_security_api.py kloud-soc-clean/tests/unit/test_clx_i_service.py -q
$testSw.Stop()
$results.tests = [ordered]@{
  ok = $LASTEXITCODE -eq 0
  duration_sec = [math]::Round($testSw.Elapsed.TotalSeconds,2)
}

# 3) Disk snapshot
$results.disk = @(
  (Get-DirSize ".venv"),
  (Get-DirSize "sdist/clx-ai"),
  (Get-DirSize ".clx_i"),
  (Get-DirSize ".clx_ops_2min"),
  (Get-DirSize "apps/web/node_modules")
)

# 4) CLX.I only profile
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*clx_i_service:app*' -or $_.CommandLine -like '*run_clx_hotguard.py*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

$uvOnly = Start-Process -FilePath $venvPy -ArgumentList @('-m','uvicorn','clx_i_service:app','--host','127.0.0.1','--port','8096') -PassThru
$latOnly = Invoke-LatencyProbe -url 'http://127.0.0.1:8096/health' -count 20
$uvOnlyProc = Get-Process -Id $uvOnly.Id -ErrorAction SilentlyContinue
$results.profile_clxi_only = [ordered]@{
  latency = $latOnly
  process = [ordered]@{
    pid = $uvOnly.Id
    ws_mb = if ($uvOnlyProc) { [math]::Round($uvOnlyProc.WorkingSet64/1MB,2) } else { 0 }
    cpu_sec = if ($uvOnlyProc) { [math]::Round($uvOnlyProc.CPU,2) } else { 0 }
  }
}
Stop-Process -Id $uvOnly.Id -Force -ErrorAction SilentlyContinue

# 5) CLX.I + Hotguard profile
$uv = Start-Process -FilePath $venvPy -ArgumentList @('-m','uvicorn','clx_i_service:app','--host','127.0.0.1','--port','8097') -PassThru
$hg = Start-Process -FilePath $venvPy -ArgumentList @('run_clx_hotguard.py','--interval-seconds','120','--workspace-root',"$repoRoot",'--memory-dir',"$repoRoot\.clx_ops_2min") -PassThru
$latCombined = Invoke-LatencyProbe -url 'http://127.0.0.1:8097/health' -count 20
$uvProc = Get-Process -Id $uv.Id -ErrorAction SilentlyContinue
$hgProc = Get-Process -Id $hg.Id -ErrorAction SilentlyContinue
$results.profile_clxi_hotguard = [ordered]@{
  latency = $latCombined
  uvicorn = [ordered]@{
    pid = $uv.Id
    ws_mb = if ($uvProc) { [math]::Round($uvProc.WorkingSet64/1MB,2) } else { 0 }
    cpu_sec = if ($uvProc) { [math]::Round($uvProc.CPU,2) } else { 0 }
  }
  hotguard = [ordered]@{
    pid = $hg.Id
    ws_mb = if ($hgProc) { [math]::Round($hgProc.WorkingSet64/1MB,2) } else { 0 }
    cpu_sec = if ($hgProc) { [math]::Round($hgProc.CPU,2) } else { 0 }
  }
}
Stop-Process -Id $uv.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $hg.Id -Force -ErrorAction SilentlyContinue

# 6) Full-stack baseline availability
$ports = @(8000,8030,9999)
$baseline = @()
foreach($p in $ports){
  try {
    $r = Invoke-WebRequest -UseBasicParsing ("http://127.0.0.1:{0}/health" -f $p) -TimeoutSec 3
    $baseline += [pscustomobject]@{ port=$p; available=$true; status=[int]$r.StatusCode }
  } catch {
    $baseline += [pscustomobject]@{ port=$p; available=$false; status='n/a' }
  }
}
$results.full_stack_baseline = $baseline

$json = $results | ConvertTo-Json -Depth 8
Set-Content -Path $reportPath -Value $json -Encoding UTF8
Write-Output "REPORT=$reportPath"
