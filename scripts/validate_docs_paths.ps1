param(
    [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path $Root).Path
$docs = Get-ChildItem -Path $rootPath -Recurse -File -Include *.md
$missing = @()

foreach ($doc in $docs) {
    $content = Get-Content -Path $doc.FullName -Raw
    if ($null -eq $content) { $content = "" }
    $regex = [regex]'\[[^\]]+\]\(([^)]+)\)'
    $matches = $regex.Matches($content)

    foreach ($m in $matches) {
        $target = $m.Groups[1].Value.Trim()

        if ([string]::IsNullOrWhiteSpace($target)) { continue }
        if ($target.StartsWith("http://") -or $target.StartsWith("https://") -or $target.StartsWith("mailto:")) { continue }
        if ($target.StartsWith("#")) { continue }

        $pathOnly = $target.Split("#")[0]
        if ([string]::IsNullOrWhiteSpace($pathOnly)) { continue }

        $resolved = Join-Path $doc.DirectoryName $pathOnly
        if (-not (Test-Path -LiteralPath $resolved)) {
            $missing += [PSCustomObject]@{
                File = $doc.FullName.Replace($rootPath + [IO.Path]::DirectorySeparatorChar, "")
                Link = $target
            }
        }
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[docs-path-validation] Missing references found:" -ForegroundColor Red
    $missing | Sort-Object File, Link | Format-Table -AutoSize | Out-String | Write-Host
    exit 1
}

Write-Host "[docs-path-validation] OK: no missing local markdown link targets." -ForegroundColor Green
exit 0
