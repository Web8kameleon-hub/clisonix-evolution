param(
  [string]$BaseUrl = "http://127.0.0.1:8889",
  [string]$AdminToken = $env:KLOUD_BRIDGE_ADMIN_TOKEN
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Test-JsonEndpoint {
  param(
    [string]$Url,
    [hashtable]$Headers = @{}
  )

  $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -Headers $Headers -TimeoutSec 10
  $payload = $response.Content | ConvertFrom-Json
  [pscustomobject]@{
    Url = $Url
    StatusCode = [int]$response.StatusCode
    Payload = $payload
  }
}

$checks = @(
  (Test-JsonEndpoint -Url "$BaseUrl/health"),
  (Test-JsonEndpoint -Url "$BaseUrl/status")
)

if ($AdminToken) {
  $checks += Test-JsonEndpoint -Url "$BaseUrl/admin/diagnostics" -Headers @{ 'x-admin-token' = $AdminToken }
}

$checks | ForEach-Object {
  Write-Host "OK $($_.StatusCode) $($_.Url)"
  ($_.Payload | ConvertTo-Json -Depth 8)
}
