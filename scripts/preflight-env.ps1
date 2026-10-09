param(
    [string]$EnvFile = ".env.production",
    [switch]$SkipComposeValidation
)

$ErrorActionPreference = "Stop"

function Read-EnvFile {
    param([string]$Path)

    $map = @{}
    foreach ($line in Get-Content -Path $Path) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
        if ($trimmed.StartsWith("#")) { continue }
        $idx = $trimmed.IndexOf("=")
        if ($idx -lt 1) { continue }
        $key = $trimmed.Substring(0, $idx).Trim()
        $val = $trimmed.Substring($idx + 1)
        $map[$key] = $val
    }
    return $map
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envPath = if ([System.IO.Path]::IsPathRooted($EnvFile)) { $EnvFile } else { Join-Path $repoRoot $EnvFile }

if (-not (Test-Path $envPath)) {
    Write-Host "[FAIL] Env file not found: $envPath" -ForegroundColor Red
    Write-Host "Create it from .env.production.template first." -ForegroundColor Yellow
    exit 1
}

$required = @(
    "POSTGRES_PASSWORD",
    "MONGO_ROOT_PASSWORD",
    "NEO4J_PASSWORD",
    "MINIO_ROOT_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD",
    "KITCHEN_RUN_API_KEY"
)

$placeholderPatterns = @(
    "REPLACE_WITH_",
    "CHANGE_ME",
    "your-",
    "example",
    "admin123",
    "test123"
)

$envMap = Read-EnvFile -Path $envPath
$missing = @()
$weak = @()

foreach ($key in $required) {
    if (-not $envMap.ContainsKey($key) -or [string]::IsNullOrWhiteSpace($envMap[$key])) {
        $missing += $key
        continue
    }

    $value = $envMap[$key]
    foreach ($pattern in $placeholderPatterns) {
        if ($value -like "*$pattern*") {
            $weak += $key
            break
        }
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[FAIL] Missing required variables:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

if ($weak.Count -gt 0) {
    Write-Host "[FAIL] Placeholder or weak values detected:" -ForegroundColor Red
    ($weak | Select-Object -Unique) | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "[OK] Required env variables are present and non-placeholder." -ForegroundColor Green

if ($envMap.ContainsKey("CLISONIX_ENV_FILE") -and $envMap["CLISONIX_ENV_FILE"] -ne ".env.production") {
    Write-Host "[WARN] CLISONIX_ENV_FILE in env file is '$($envMap["CLISONIX_ENV_FILE"])'. Expected '.env.production'." -ForegroundColor Yellow
}

if (-not $SkipComposeValidation) {
    Push-Location $repoRoot
    try {
        $env:CLISONIX_ENV_FILE = ".env.production"
        $null = docker compose --env-file $envPath config
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] docker compose config validation failed." -ForegroundColor Red
            exit 1
        }
        Write-Host "[OK] docker compose config validation passed." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

Write-Host "Preflight env check passed." -ForegroundColor Green
