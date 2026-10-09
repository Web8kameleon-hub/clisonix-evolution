param(
    [string]$GitHubOwner = "Web8kameleon-hub",
    [string]$TargetRoot = "",
    [switch]$Commit,
    [switch]$Push,
    [switch]$IncludeCurrentRepo,
    [string[]]$IsolatedRepos = @('Kloud')
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path
$canonicalPackage = Join-Path $repoRoot 'packages\nanogrid'

if (-not (Test-Path $canonicalPackage)) {
    throw "Canonical NanoGrid package not found at: $canonicalPackage"
}

if ([string]::IsNullOrWhiteSpace($TargetRoot)) {
    $TargetRoot = Join-Path $repoRoot '_profile_repos'
}

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null

$headers = @{
    'User-Agent' = 'Clisonix-NanoGrid-Sync'
    'Accept'     = 'application/vnd.github+json'
}

$apiUrl = "https://api.github.com/users/$GitHubOwner/repos?per_page=100&sort=updated"
Write-Host "Fetching repositories for $GitHubOwner ..." -ForegroundColor Cyan
$repos = Invoke-RestMethod -Uri $apiUrl -Headers $headers

if (-not $repos) {
    throw "No repositories returned for owner '$GitHubOwner'."
}

$processed = @()
$failed = @()
$isolated = @()

foreach ($repo in $repos) {
    if (-not $IncludeCurrentRepo -and $repo.name -eq 'clisonix.com') {
        continue
    }

    $localRepo = Join-Path $TargetRoot $repo.name
    Write-Host "`n=== $($repo.name) ===" -ForegroundColor Yellow

    try {
        if (Test-Path (Join-Path $localRepo '.git')) {
            Write-Host "Updating existing clone..."
            & git -C $localRepo pull --ff-only
            if ($LASTEXITCODE -ne 0) {
                throw "git pull failed"
            }
        }
        else {
            Write-Host "Cloning repository..."
            & git clone --depth 1 $repo.clone_url $localRepo
            if ($LASTEXITCODE -ne 0) {
                throw "git clone failed"
            }
        }

        if ($IsolatedRepos -contains $repo.name) {
            Write-Host "Skipping package copy for isolated repo $($repo.name)." -ForegroundColor Magenta
            $isolated += $repo.name
            $processed += $repo.name
            continue
        }

        $targetPackage = Join-Path $localRepo 'packages\nanogrid'
        if (Test-Path $targetPackage) {
            Remove-Item -Recurse -Force $targetPackage
        }

        New-Item -ItemType Directory -Force -Path $targetPackage | Out-Null
        Copy-Item -Path (Join-Path $canonicalPackage '*') -Destination $targetPackage -Recurse -Force

        Write-Host "NanoGrid package copied to $targetPackage" -ForegroundColor Green

        if ($Commit -or $Push) {
            & git -C $localRepo add packages/nanogrid
            $status = & git -C $localRepo status --short packages/nanogrid

            if ($status) {
                & git -C $localRepo commit -m 'chore: sync nanogrid package'
                if ($LASTEXITCODE -ne 0) {
                    throw "git commit failed"
                }
            }
            else {
                Write-Host "No package changes to commit."
            }
        }

        if ($Push) {
            & git -C $localRepo push origin HEAD
            if ($LASTEXITCODE -ne 0) {
                throw "git push failed"
            }
        }

        $processed += $repo.name
    }
    catch {
        Write-Warning "Failed for $($repo.name): $($_.Exception.Message)"
        $failed += $repo.name
    }
}

Write-Host "`nSync complete." -ForegroundColor Cyan
Write-Host "Processed: $($processed.Count) repo(s)" -ForegroundColor Green
if ($processed.Count -gt 0) {
    $processed | ForEach-Object { Write-Host "  - $_" }
}

if ($isolated.Count -gt 0) {
    Write-Host "Isolated (intentionally not synced): $($isolated.Count) repo(s)" -ForegroundColor Magenta
    $isolated | ForEach-Object { Write-Host "  - $_" }
}

if ($failed.Count -gt 0) {
    Write-Host "Failed: $($failed.Count) repo(s)" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" }
}

Write-Host "`nExample:" -ForegroundColor Cyan
Write-Host "  pwsh ./scripts/sync-nanogrid-profile.ps1 -GitHubOwner $GitHubOwner"
Write-Host "  pwsh ./scripts/sync-nanogrid-profile.ps1 -GitHubOwner $GitHubOwner -Commit"
