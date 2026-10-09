# Stripe One-Time Checkout Smoke Test
# Run: .\test-stripe-one-time.ps1

param(
    [string]$BaseUrl = "http://localhost:3000"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "💳 STRIPE ONE-TIME SMOKE TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

# Test 1: Product creation
Write-Host "TEST 1: POST /api/stripe/products" -ForegroundColor Yellow
$productBody = @{
    name = "Clisonix Day0 Product"
    currency = "eur"
    unit_amount = 999
} | ConvertTo-Json

$productResponse = Invoke-WebRequest -Uri "$BaseUrl/api/stripe/products" `
    -Method POST `
    -ContentType "application/json" `
    -Body $productBody `
    -UseBasicParsing `
    -TimeoutSec 30

$productData = $productResponse.Content | ConvertFrom-Json
$priceId = $productData.default_price

if (-not $priceId) {
    throw "No default_price returned from /api/stripe/products"
}

Write-Host "✅ Product created: $($productData.product_id)" -ForegroundColor Green
Write-Host "✅ Default price: $priceId" -ForegroundColor Green
Write-Host ""

# Test 2: One-time checkout session
Write-Host "TEST 2: POST /api/stripe/checkout/one-time" -ForegroundColor Yellow
$checkoutBody = @{
    price = $priceId
    quantity = 1
} | ConvertTo-Json

$checkoutResponse = Invoke-WebRequest -Uri "$BaseUrl/api/stripe/checkout/one-time" `
    -Method POST `
    -ContentType "application/json" `
    -Body $checkoutBody `
    -UseBasicParsing `
    -TimeoutSec 30

$checkoutData = $checkoutResponse.Content | ConvertFrom-Json
if (-not $checkoutData.url) {
    throw "No checkout URL returned from /api/stripe/checkout/one-time"
}

Write-Host "✅ Checkout session: $($checkoutData.id)" -ForegroundColor Green
Write-Host "🔗 URL: $($checkoutData.url)" -ForegroundColor Cyan
Write-Host ""

# Test 3: Bootstrap endpoint (product + checkout in one call)
Write-Host "TEST 3: POST /api/stripe/one-time/bootstrap" -ForegroundColor Yellow
$bootstrapBody = @{
    name = "Clisonix Bootstrap Product"
    currency = "eur"
    unit_amount = 1499
    quantity = 1
} | ConvertTo-Json

$bootstrapResponse = Invoke-WebRequest -Uri "$BaseUrl/api/stripe/one-time/bootstrap" `
    -Method POST `
    -ContentType "application/json" `
    -Body $bootstrapBody `
    -UseBasicParsing `
    -TimeoutSec 30

$bootstrapData = $bootstrapResponse.Content | ConvertFrom-Json
if (-not $bootstrapData.checkout_session.url) {
    throw "No checkout URL returned from /api/stripe/one-time/bootstrap"
}

Write-Host "✅ Bootstrap product: $($bootstrapData.product.id)" -ForegroundColor Green
Write-Host "✅ Bootstrap session: $($bootstrapData.checkout_session.id)" -ForegroundColor Green
Write-Host "🔗 URL: $($bootstrapData.checkout_session.url)" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ ALL STRIPE ONE-TIME TESTS PASSED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next: open checkout URL and complete Stripe test payment (e.g., 4242 4242 4242 4242)." -ForegroundColor Gray
