$ErrorActionPreference = 'SilentlyContinue'

$base = 'https://clisonix.com'
$root = 'c:\Users\Admin\Desktop\Clisonix-cloud\apps\web\app'

$moduleDirs = Get-ChildItem "$root\modules" -Directory | Where-Object {
  Test-Path (Join-Path $_.FullName 'page.tsx')
}
$moduleUrls = @('/modules') + ($moduleDirs | ForEach-Object { '/modules/' + $_.Name })

$apiFiles = Get-ChildItem "$root\api" -Recurse -Filter route.ts
$apiUrls = @()

foreach ($file in $apiFiles) {
  $relativePath = $file.FullName.Substring((Join-Path $root 'api').Length).TrimStart('\\')

  if ($relativePath -match '\\[') {
    continue
  }

  if ($relativePath -eq 'route.ts') {
    $apiUrls += '/api'
    continue
  }

  $relativePath = $relativePath -replace '\\route\.ts$', ''
  $apiUrls += '/api/' + ($relativePath -replace '\\', '/')
}

$apiUrls = $apiUrls | Sort-Object -Unique

$acceptedCodes = @(200, 201, 202, 204, 301, 302, 307, 308, 400, 401, 403, 405)
$results = @()

foreach ($url in $moduleUrls) {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri ($base + $url) -Method GET -MaximumRedirection 2 -TimeoutSec 12
    $statusCode = [int]$response.StatusCode
  } catch {
    $statusCode = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode.value__ } else { 0 }
  }

  $results += [pscustomobject]@{
    kind = 'module'
    url = $url
    code = $statusCode
  }
}

foreach ($url in $apiUrls) {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri ($base + $url) -Method GET -MaximumRedirection 1 -TimeoutSec 10
    $statusCode = [int]$response.StatusCode
  } catch {
    $statusCode = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode.value__ } else { 0 }
  }

  $results += [pscustomobject]@{
    kind = 'api'
    url = $url
    code = $statusCode
  }
}

$failed = $results | Where-Object { $acceptedCodes -notcontains $_.code } | Sort-Object kind, url

"TOTAL_MODULES=$($moduleUrls.Count) TOTAL_API=$($apiUrls.Count) BAD=$($failed.Count)"
$failed | ForEach-Object { "{0} {1} {2}" -f $_.kind, $_.code, $_.url }