Write-Host "🚨 EMERGENCY RESET - ALL ZONES" -ForegroundColor Red

# Kill all processes
Write-Host "🛑 Stopping all processes..." -ForegroundColor Yellow
taskkill /F /IM node.exe /T 2>$null
taskkill /F /IM python.exe /T 2>$null

# Clean frontend zone
Write-Host "🧹 Cleaning frontend zone..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    Set-Location frontend
    yarn cache clean --all 2>$null
    Remove-Item .next -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
    Set-Location ..
}

# Clean backend zone
Write-Host "🐍 Cleaning backend zone..." -ForegroundColor Cyan
if (Test-Path "backend") {
    Set-Location backend
    pip cache purge 2>$null
    Remove-Item __pycache__ -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item venv -Recurse -Force -ErrorAction SilentlyContinue  
    Set-Location ..
}

Write-Host "✅ ALL ZONES RESET COMPLETE!" -ForegroundColor Green
Write-Host "🚀 Ready to setup: npm run setup:all" -ForegroundColor Cyan
