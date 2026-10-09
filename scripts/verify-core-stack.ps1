param(
    [string]$WebBase = 'http://127.0.0.1:3010',
    [string]$BridgeBase = 'http://127.0.0.1:8889'
)

$ProgressPreference = 'SilentlyContinue'
$failures = New-Object System.Collections.Generic.List[string]

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = 'GET',
        [object]$Body = $null
    )

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        if ($Method -eq 'POST') {
            $jsonBody = $Body | ConvertTo-Json -Depth 8 -Compress
            $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType 'application/json' -Body $jsonBody -SkipHttpErrorCheck
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method Get -SkipHttpErrorCheck
        }

        $sw.Stop()
        $ok = $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
        $state = if ($ok) { 'OK' } else { 'FAIL' }
        Write-Host ('{0,-24} {1,4} {2,6}ms {3}' -f $Name, $response.StatusCode, $sw.ElapsedMilliseconds, $state)

        if (-not $ok) {
            $failures.Add("$Name returned HTTP $($response.StatusCode)")
        }
    }
    catch {
        $sw.Stop()
        Write-Host ('{0,-24} ERR {1,6}ms {2}' -f $Name, $sw.ElapsedMilliseconds, $_.Exception.Message)
        $failures.Add("$Name errored: $($_.Exception.Message)")
    }
}

Write-Host '=== Clisonix Core Smoke Verification ==='
Test-Endpoint -Name 'bridge-direct-health' -Url "$BridgeBase/health"
Test-Endpoint -Name 'bridge-direct-status' -Url "$BridgeBase/status"
Test-Endpoint -Name 'bridge-proxy-health' -Url "$WebBase/api/kloud-bridge/health"
Test-Endpoint -Name 'bridge-proxy-status' -Url "$WebBase/api/kloud-bridge/status"
Test-Endpoint -Name 'ocean-fast' -Url "$WebBase/api/ocean" -Method 'POST' -Body @{ message = 'hi'; processing_mode = 'fast' }

if ($failures.Count -gt 0) {
    Write-Host ''
    Write-Host 'Smoke verification failed:' -ForegroundColor Red
    $failures | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    exit 1
}

Write-Host ''
Write-Host 'All core checks passed.' -ForegroundColor Green
exit 0
