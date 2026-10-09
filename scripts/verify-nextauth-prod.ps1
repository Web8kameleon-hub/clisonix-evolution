param(
    [string]$BaseUrl = "https://www.clisonix.com"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/3] Checking providers endpoint: $BaseUrl/api/auth/providers"
$providersRaw = curl.exe -s "$BaseUrl/api/auth/providers"
Write-Host $providersRaw

if ($providersRaw -eq "{}") {
    throw "NextAuth providers are empty. AUTH_GOOGLE_ID/AUTH_GOOGLE_SECRET are not loaded in production."
}

if ($providersRaw -notmatch '"google"') {
    throw "Google provider is missing in providers response."
}

Write-Host "[2/3] Checking /sign-up status"
$signupCode = curl.exe -s -o NUL -w "%{http_code}" "$BaseUrl/sign-up"
Write-Host "HTTP $signupCode"
if ($signupCode -ne "200") {
    throw "/sign-up returned non-200 status ($signupCode)."
}

Write-Host "[3/3] Checking /sign-in status"
$signinCode = curl.exe -s -o NUL -w "%{http_code}" "$BaseUrl/sign-in"
Write-Host "HTTP $signinCode"
if ($signinCode -ne "200") {
    throw "/sign-in returned non-200 status ($signinCode)."
}

Write-Host "OK: NextAuth production checks passed." -ForegroundColor Green
