param(
    [string]$BaseUrl = "http://127.0.0.1:8030",
    [int]$RouteSamples = 40,
    [int]$StreamSamples = 20,
    [double]$RouteP95TargetMs = 50,
    [double]$StreamP95TargetMs = 1500,
    [double]$MinSuccessRate = 0.99
)

function Get-P95([double[]]$values) {
    if (-not $values -or $values.Count -eq 0) { return [double]::NaN }
    $sorted = $values | Sort-Object
    $index = [Math]::Ceiling(0.95 * $sorted.Count) - 1
    if ($index -lt 0) { $index = 0 }
    if ($index -ge $sorted.Count) { $index = $sorted.Count - 1 }
    return [double]$sorted[$index]
}

function Invoke-TimedJsonPost {
    param(
        [string]$Url,
        [string]$Body,
        [hashtable]$Headers = @{},
        [int]$TimeoutSec = 30
    )

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $resp = Invoke-WebRequest -Uri $Url -Method POST -Body $Body -ContentType 'application/json' -Headers $Headers -UseBasicParsing -TimeoutSec $TimeoutSec
        $sw.Stop()
        return [pscustomobject]@{
            ok     = $true
            status = [int]$resp.StatusCode
            ms     = [double]$sw.ElapsedMilliseconds
        }
    }
    catch {
        $sw.Stop()
        $status = -1
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        return [pscustomobject]@{
            ok     = $false
            status = $status
            ms     = [double]$sw.ElapsedMilliseconds
        }
    }
}

$routeBody = @{ text = 'ju lutem START tani'; commands = @('START', 'RESET', 'MODE') } | ConvertTo-Json -Compress
$streamBody = @{ message = 'ju lutem START tani'; xlc_commands = @('START', 'RESET', 'MODE'); xlc_elastic = $true; max_tokens = 64 } | ConvertTo-Json -Compress

$routeResults = @()
for ($i = 0; $i -lt $RouteSamples; $i++) {
    $routeResults += Invoke-TimedJsonPost -Url ($BaseUrl + '/xlc/route') -Body $routeBody
}

$streamResults = @()
for ($i = 0; $i -lt $StreamSamples; $i++) {
    $streamResults += Invoke-TimedJsonPost -Url ($BaseUrl + '/api/v1/chat/stream') -Body $streamBody -Headers @{ Accept = 'text/event-stream' } -TimeoutSec 45
}

$routeOk = @($routeResults | Where-Object { $_.ok -and $_.status -eq 200 })
$streamOk = @($streamResults | Where-Object { $_.ok -and $_.status -eq 200 })

$routeP95 = Get-P95 -values @($routeOk | ForEach-Object { [double]$_.ms })
$streamP95 = Get-P95 -values @($streamOk | ForEach-Object { [double]$_.ms })

$routeSuccess = if ($RouteSamples -gt 0) { $routeOk.Count / [double]$RouteSamples } else { 0.0 }
$streamSuccess = if ($StreamSamples -gt 0) { $streamOk.Count / [double]$StreamSamples } else { 0.0 }
$globalSuccess = if (($RouteSamples + $StreamSamples) -gt 0) { ($routeOk.Count + $streamOk.Count) / [double]($RouteSamples + $StreamSamples) } else { 0.0 }

$passed = ($routeP95 -le $RouteP95TargetMs) -and ($streamP95 -le $StreamP95TargetMs) -and ($globalSuccess -ge $MinSuccessRate)

"CLX_GATE route_p95_ms=$routeP95 stream_p95_ms=$streamP95 route_success=$([Math]::Round($routeSuccess,4)) stream_success=$([Math]::Round($streamSuccess,4)) global_success=$([Math]::Round($globalSuccess,4)) pass=$passed"

if (-not $passed) {
    exit 1
}
