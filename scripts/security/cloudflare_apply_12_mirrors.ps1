<#
Applies an A+B+C defensive Cloudflare baseline for mirror honeypots.
This script is defensive only: block/challenge/rate-limit/sinkhole style controls.

Required permissions for API token:
- Zone:Zone Settings:Edit
- Zone:Firewall Services:Edit
- Zone:Rate Limits:Edit
- Zone:Read

Usage:
  . .\scripts\security\cloudflare_apply_12_mirrors.ps1
  Invoke-CFApply12Mirrors -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeCidrs @('1.2.3.4/32') -DryRun

  # Live apply
  Invoke-CFApply12Mirrors -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeCidrs @('1.2.3.4/32')
#>

param(
    [string]$ZoneId = $null,
    [string]$ApiToken = $null,
    [string[]]$OfficeCidrs = @(),
    [string[]]$BlockedAsns = @(),
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-CFApi {
    param(
        [Parameter(Mandatory = $true)][ValidateSet('GET', 'POST', 'PATCH', 'PUT', 'DELETE')][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$ApiToken,
        [object]$Body = $null,
        [switch]$DryRun
    )

    $headers = @{
        Authorization  = "Bearer $ApiToken"
        'Content-Type' = 'application/json'
    }

    if ($DryRun.IsPresent) {
        Write-Host "[DryRun] $Method $Uri"
        if ($null -ne $Body) {
            Write-Host "[DryRun] Body: $($Body | ConvertTo-Json -Depth 20 -Compress)"
        }
        return $null
    }

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $headers
    }

    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $headers -Body ($Body | ConvertTo-Json -Depth 20)
}

function Set-CFSetting {
    param(
        [string]$ZoneId,
        [string]$ApiToken,
        [string]$SettingName,
        [string]$SettingValue,
        [switch]$DryRun
    )

    $uri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/settings/$SettingName"
    $body = @{ value = $SettingValue }
    Write-Host "[CF] Setting '$SettingName' => '$SettingValue'"
    Invoke-CFApi -Method PATCH -Uri $uri -ApiToken $ApiToken -Body $body -DryRun:$DryRun | Out-Null
}

function Remove-CFFirewallRulesByTag {
    param(
        [string]$ZoneId,
        [string]$ApiToken,
        [string]$Tag,
        [switch]$DryRun
    )

    $listUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/firewall/rules?page=1&per_page=100"
    $resp = Invoke-CFApi -Method GET -Uri $listUri -ApiToken $ApiToken -DryRun:$DryRun
    if ($DryRun.IsPresent -or $null -eq $resp) {
        return
    }

    $rules = @($resp.result | Where-Object { $_.description -like "*$Tag*" })
    foreach ($rule in $rules) {
        $delUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/firewall/rules/$($rule.id)"
        Write-Host "[CF] Removing existing rule: $($rule.id) ($($rule.description))"
        Invoke-CFApi -Method DELETE -Uri $delUri -ApiToken $ApiToken -DryRun:$DryRun | Out-Null
    }
}

function New-CFFirewallRules12Mirrors {
    param(
        [string]$ZoneId,
        [string]$ApiToken,
        [string[]]$OfficeCidrs,
        [string[]]$BlockedAsns,
        [switch]$DryRun
    )

    $tag = 'CLX-12MIRRORS'
    Remove-CFFirewallRulesByTag -ZoneId $ZoneId -ApiToken $ApiToken -Tag $tag -DryRun:$DryRun

    $rulesUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/firewall/rules"

    $mirrorExpr = '(http.request.uri.path matches "^/mirror-(a[1-4]|b[1-4]|c[1-4])(/.*)?$") and not cf.client.bot'

    $payload = @(
        @{
            action      = 'managed_challenge'
            description = ('{0}: challenge mirror honeypot hits' -f $tag)
            filter      = @{
                expression  = $mirrorExpr
                paused      = $false
                description = "$tag mirror trap"
            }
        },
        @{
            action      = 'challenge'
            description = ('{0}: challenge high threat non-bot' -f $tag)
            filter      = @{
                expression  = '(cf.threat_score gt 20) and (not cf.client.bot) and (not http.request.uri.path in {"/health" "/status"})'
                paused      = $false
                description = "$tag threat challenge"
            }
        },
        @{
            action      = 'block'
            description = ('{0}: block obvious scanners on sensitive paths' -f $tag)
            filter      = @{
                expression  = '(not cf.client.bot) and (http.request.uri.path contains "/wp-admin" or http.request.uri.path contains "/.env" or http.request.uri.path contains "/phpmyadmin" or http.request.uri.path contains "/admin")'
                paused      = $false
                description = "$tag scanner block"
            }
        }
    )

    if ($OfficeCidrs.Count -gt 0) {
        $cidrSet = ($OfficeCidrs | ForEach-Object { $_.Trim() } | Where-Object { $_ }) -join ' '
        $adminExpr = '(http.request.uri.path contains "/admin") and not ip.src in {{{0}}}' -f $cidrSet
        $payload += @{
            action      = 'block'
            description = ('{0}: lock /admin outside office CIDRs' -f $tag)
            filter      = @{
                expression  = $adminExpr
                paused      = $false
                description = "$tag admin lock"
            }
        }
    }

    if ($BlockedAsns.Count -gt 0) {
        $asnSet = ($BlockedAsns | ForEach-Object { $_.Trim() } | Where-Object { $_ }) -join ' '
        $payload += @{
            action      = 'block'
            description = ('{0}: ASN deny list' -f $tag)
            filter      = @{
                expression  = "ip.geoip.asnum in {$asnSet}"
                paused      = $false
                description = "$tag asn deny"
            }
        }
    }

    Write-Host "[CF] Creating firewall rules for 12 mirrors profile"
    Invoke-CFApi -Method POST -Uri $rulesUri -ApiToken $ApiToken -Body $payload -DryRun:$DryRun | Out-Null
}

function New-CFRateLimitMirrorPaths {
    param(
        [string]$ZoneId,
        [string]$ApiToken,
        [switch]$DryRun
    )

    $uri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/rate_limits"

    $payload = @{
        threshold   = 6
        period      = 10
        action      = @{ mode = 'challenge'; timeout = 600 }
        match       = @{
            request  = @{
                methods = @('GET', 'POST', 'HEAD')
                schemes = @('HTTP', 'HTTPS')
                url     = '*://*/*'
            }
            response = @{ statuses = @(); origin_traffic = $true }
        }
        bypass      = @()
        correlate   = @{ by = 'nat' }
        disabled    = $false
        description = 'CLX-12MIRRORS: general burst limiter'
    }

    Write-Host "[CF] Adding baseline burst limiter"
    Invoke-CFApi -Method POST -Uri $uri -ApiToken $ApiToken -Body $payload -DryRun:$DryRun | Out-Null
}

function Invoke-CFApply12Mirrors {
    param(
        [Parameter(Mandatory = $true)][string]$ZoneId,
        [Parameter(Mandatory = $true)][string]$ApiToken,
        [string[]]$OfficeCidrs = @(),
        [string[]]$BlockedAsns = @(),
        [switch]$DryRun
    )

    Write-Host "[CF] Applying defensive A+B+C baseline for zone $ZoneId"

    # Keep settings defensive and standards-aligned.
    Set-CFSetting -ZoneId $ZoneId -ApiToken $ApiToken -SettingName 'security_level' -SettingValue 'high' -DryRun:$DryRun
    Set-CFSetting -ZoneId $ZoneId -ApiToken $ApiToken -SettingName 'bot_fight_mode' -SettingValue 'on' -DryRun:$DryRun

    # Optional on supported plans; harmless if unavailable.
    try {
        Set-CFSetting -ZoneId $ZoneId -ApiToken $ApiToken -SettingName 'super_bot_fight_mode' -SettingValue 'on' -DryRun:$DryRun
    }
    catch {
        Write-Warning "[CF] super_bot_fight_mode not available on this plan/API token. Continuing."
    }

    New-CFFirewallRules12Mirrors -ZoneId $ZoneId -ApiToken $ApiToken -OfficeCidrs $OfficeCidrs -BlockedAsns $BlockedAsns -DryRun:$DryRun
    New-CFRateLimitMirrorPaths -ZoneId $ZoneId -ApiToken $ApiToken -DryRun:$DryRun

    Write-Host "[CF] Done. Validate in Cloudflare dashboard: Security, WAF, and Rate Limiting pages."
}

if ($ZoneId -and $ApiToken) {
    Invoke-CFApply12Mirrors -ZoneId $ZoneId -ApiToken $ApiToken -OfficeCidrs $OfficeCidrs -BlockedAsns $BlockedAsns -DryRun:$DryRun
}
else {
    Write-Host 'Loaded cloudflare_apply_12_mirrors.ps1. Call Invoke-CFApply12Mirrors to apply.'
}
