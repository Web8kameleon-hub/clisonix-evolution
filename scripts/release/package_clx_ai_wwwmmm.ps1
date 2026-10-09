param(
    [string]$Version = "",
    [string]$OutDir = "",
    [switch]$CreateTag,
    [switch]$PublishWithGh
)

$ErrorActionPreference = "Stop"

function New-NormalizedPath([string]$PathValue) {
    return [System.IO.Path]::GetFullPath($PathValue)
}

function Assert-Exists([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "Required path not found: $PathValue"
    }
}

function New-DirectoryIfMissing([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue | Out-Null
    }
}

function Copy-FileIfExists([string]$Source, [string]$DestinationDir) {
    if (Test-Path -LiteralPath $Source) {
        New-DirectoryIfMissing $DestinationDir
        Copy-Item -LiteralPath $Source -Destination $DestinationDir -Force
        return $true
    }
    return $false
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = New-NormalizedPath (Join-Path $scriptRoot "..\..")
Set-Location $repoRoot

if ([string]::IsNullOrWhiteSpace($Version)) {
    $Version = "v" + (Get-Date -Format "yyyy.MM.dd-HHmm")
}

if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $repoRoot "releases"
}
$OutDir = New-NormalizedPath $OutDir
New-DirectoryIfMissing $OutDir

$packageName = "clx-ai-wwwmmm-$Version"
$stagingDir = Join-Path $OutDir $packageName
$zipPath = Join-Path $OutDir ($packageName + ".zip")
$manifestPath = Join-Path $OutDir ($packageName + ".manifest.json")
$shaPath = Join-Path $OutDir ($packageName + ".sha256.txt")

if (Test-Path -LiteralPath $stagingDir) {
    Remove-Item -LiteralPath $stagingDir -Recurse -Force
}
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

New-DirectoryIfMissing $stagingDir

$requiredPaths = @(
    (Join-Path $repoRoot "sdist\clx-ai\clx"),
    (Join-Path $repoRoot "sdist\clx-ai\examples"),
    (Join-Path $repoRoot "sdist\clx-ai\tests"),
    (Join-Path $repoRoot "scripts\clx_only_gate.ps1")
)

foreach ($p in $requiredPaths) {
    Assert-Exists $p
}

$copyMap = @(
    # Source code and core modules
    @{ Source = "sdist\clx-ai\clx"; Dest = "sdist\clx-ai\clx"; Type = "dir" },

    # Documentation
    @{ Source = "sdist\clx-ai\README.md"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\LICENSE"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\BUILD_AND_PUBLISH.md"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\DISTRIBUTION.md"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\PACKAGE_STRUCTURE.md"; Dest = "sdist\clx-ai"; Type = "file" },

    # Configuration files
    @{ Source = "sdist\clx-ai\pyproject.toml"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\setup.py"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\requirements.txt"; Dest = "sdist\clx-ai"; Type = "file" },
    @{ Source = "sdist\clx-ai\MANIFEST.in"; Dest = "sdist\clx-ai"; Type = "file" },

    # Examples (all)
    @{ Source = "sdist\clx-ai\examples"; Dest = "sdist\clx-ai\examples"; Type = "dir" },

    # Tests
    @{ Source = "sdist\clx-ai\tests"; Dest = "sdist\clx-ai\tests"; Type = "dir" },

    # Validation utility
    @{ Source = "sdist\clx-ai\validate_package.py"; Dest = "sdist\clx-ai"; Type = "file" },

    # Release policies
    @{ Source = "scripts\clx_only_gate.ps1"; Dest = "scripts"; Type = "file" },
    @{ Source = "RELEASE_GATE_CHECKLIST.md"; Dest = "."; Type = "file" },
    @{ Source = "NO_FAKE_DATA_POLICY.md"; Dest = "."; Type = "file" },

    # Runner scripts (user-accessible from package root)
    @{ Source = "run_clx_hotguard.py"; Dest = "."; Type = "file" },
    @{ Source = "run_clx_hotguard_cli.ps1"; Dest = "."; Type = "file" },
    @{ Source = "CLX_AI_INSTALLATION_GUIDE.md"; Dest = "."; Type = "file" },
    @{ Source = "CLX_AI_COMPLETE_TIMELINE.md"; Dest = "."; Type = "file" }
)

$included = New-Object System.Collections.Generic.List[string]
foreach ($item in $copyMap) {
    $src = Join-Path $repoRoot $item.Source
    $dest = Join-Path $stagingDir $item.Dest

    if ($item.Type -eq "dir") {
        if (Test-Path -LiteralPath $src) {
            New-DirectoryIfMissing (Split-Path -Parent $dest)
            Copy-Item -LiteralPath $src -Destination $dest -Recurse -Force
            $included.Add($item.Source) | Out-Null
        }
        continue
    }

    if (Copy-FileIfExists -Source $src -DestinationDir $dest) {
        $included.Add($item.Source) | Out-Null
    }
}

# Remove runtime cache artifacts from staged package.
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter "build" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter "dist" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter "*.egg-info" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -Directory -Filter ".clx_*" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $stagingDir -Recurse -File -Include "*.pyc", "*.pyo" -ErrorAction SilentlyContinue |
Remove-Item -Force -ErrorAction SilentlyContinue

$runnerContent = @"
`$ErrorActionPreference = "Stop"
`$root = Split-Path -Parent `$(Split-Path -Parent `$MyInvocation.MyCommand.Path)
`$python = Join-Path `$root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath `$python)) {
    throw "Python venv not found at `$python"
}
`$env:PYTHONPATH = Join-Path `$root "sdist\clx-ai"
& `$python (Join-Path `$root "sdist\clx-ai\examples\ecosystem_ops_10min.py") `
    --interval-seconds 120 `
    --duration-seconds 14400 `
    --workspace-root `$root `
    --memory-dir (Join-Path `$root "sdist\clx-ai\.clx_ops_2min") `
    --report-file (Join-Path `$root "sdist\clx-ai\.clx_ops_2min\final_report.json") `
    --snapshots-dir (Join-Path `$root "sdist\clx-ai\.clx_ops_2min\snapshots") `
    --local-max-files 220 `
    --local-max-bytes 10000 `
    --code-max-files 70 `
    --code-max-bytes 14000
"@
Set-Content -LiteralPath (Join-Path $stagingDir "run_2min_hotguard.ps1") -Value $runnerContent -Encoding UTF8
$included.Add("run_2min_hotguard.ps1") | Out-Null

$manifest = [ordered]@{
    package                = $packageName
    version                = $Version
    generated_at_utc       = (Get-Date).ToUniversalTime().ToString("o")
    repository             = "Web8kameleon-hub/clisonix.com"
    branch                 = (git rev-parse --abbrev-ref HEAD)
    commit                 = (git rev-parse HEAD)
    license                = "Apache-2.0"
    license_url            = "https://www.apache.org/licenses/LICENSE-2.0"
    included_paths         = $included
    publish_recommendation = [ordered]@{
        git_tag              = "clx-ai/$Version"
        github_release_title = "CLX AI WWWMMM $Version"
        github_release_notes = "2-minute hotguard release with atomic persistence and phased ops learning."
    }
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $zipPath -CompressionLevel Optimal

$zipHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash
"$zipHash  $(Split-Path -Leaf $zipPath)" | Set-Content -LiteralPath $shaPath -Encoding ASCII

Write-Host "[CLX-PACKAGE] ZIP: $zipPath"
Write-Host "[CLX-PACKAGE] MANIFEST: $manifestPath"
Write-Host "[CLX-PACKAGE] SHA256: $shaPath"

if ($CreateTag) {
    $tagName = "clx-ai/$Version"
    git tag $tagName
    git push origin $tagName
    Write-Host "[CLX-PACKAGE] Tag pushed: $tagName"
}

if ($PublishWithGh) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) not found. Install gh or run without -PublishWithGh."
    }

    $releaseTag = "clx-ai/$Version"
    if (-not (git tag --list $releaseTag)) {
        git tag $releaseTag
        git push origin $releaseTag
    }

    gh release create $releaseTag `
        --title "CLX AI WWWMMM $Version" `
        --notes "Mass-ready CLX AI package with 2-minute hotguard runner, atomic persistence, and release gate assets." `
        $zipPath $manifestPath $shaPath

    Write-Host "[CLX-PACKAGE] GitHub release published: $releaseTag"
}

Write-Host "[CLX-PACKAGE] Next:"
Write-Host "  1) Test package locally from ZIP"
Write-Host "  2) Create PR from feature/clx-2min-hotguard"
Write-Host "  3) Publish with: pwsh -File scripts/release/package_clx_ai_wwwmmm.ps1 -Version $Version -CreateTag -PublishWithGh"
