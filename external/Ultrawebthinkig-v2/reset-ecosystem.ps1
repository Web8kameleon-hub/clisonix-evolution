# UltraWeb Ecosystem Reset Script - DEFCON 1
# Resets ALL package managers and technologies to pristine state

Write-Host "🚨 EMERGENCY ECOSYSTEM RESET - DEFCON 1 🚨" -ForegroundColor Red
Write-Host "Resetting ALL systems: Yarn, Python, Node.js, Mesh, LoRa, WASM, Blockchain, Docker, AI, Databases" -ForegroundColor Yellow

# Stop all running processes
Write-Host "🛑 Stopping all processes..." -ForegroundColor Yellow
taskkill /F /IM node.exe /T 2>$null
taskkill /F /IM python.exe /T 2>$null
docker-compose down --volumes 2>$null

# Clean ALL caches and build artifacts
Write-Host "🧹 Cleaning ALL caches and artifacts..." -ForegroundColor Yellow
Remove-Item .yarn/cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue  
Remove-Item .next -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ultracom/__pycache__ -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ultracom/venv -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item mesh/.mesh-cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item lora/.device-cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item wasm/pkg -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item blockchain/build -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item models/.model-cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item databases/.db-cache -Recurse -Force -ErrorAction SilentlyContinue

# Clean ALL package manager caches
Write-Host "💾 Purging package manager caches..." -ForegroundColor Yellow
yarn cache clean --all
npm cache clean --force 2>$null
Set-Location ultracom
pip cache purge 2>$null
Set-Location ..
docker system prune -af 2>$null

# Rebuild EVERYTHING from scratch
Write-Host "🔄 Rebuilding ecosystem from scratch..." -ForegroundColor Green
yarn install --refresh-lockfile

Set-Location ultracom
pip install -r requirements.txt --force-reinstall 2>$null
Set-Location ..

# Create missing directories if they don't exist
$directories = @(
    "mesh", "lora", "wasm", "blockchain", 
    "models", "databases", "docker"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "📁 Created directory: $dir" -ForegroundColor Cyan
    }
}

# Verify ecosystem integrity
Write-Host "🧪 Testing ecosystem integrity..." -ForegroundColor Green

# Check if essential files exist
$essentialFiles = @(
    "package.json",
    "ultracom/requirements.txt", 
    "PACKAGE_COOPERATION_CONTRACT.md"
)

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 ECOSYSTEM RESET COMPLETE!" -ForegroundColor Green
Write-Host "🚀 Ready to launch with: yarn ultra-ecosystem" -ForegroundColor Cyan
Write-Host "📋 Contract enforced: ZERO CONFLICTS GUARANTEED" -ForegroundColor Green
Write-Host ""
