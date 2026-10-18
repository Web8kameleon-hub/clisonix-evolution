# 🚀 UltraCom System Launcher (PowerShell)
# Automated setup and launch for Client ↔ Technician communication system

Write-Host "🚀 UltraCom System Launcher" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Navigate to ultracom directory
$ultracomPath = ".\ultracom"
if (-not (Test-Path $ultracomPath)) {
    Write-Host "❌ UltraCom directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location $ultracomPath

Write-Host "📂 Working directory: $(Get-Location)" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env configuration..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Configuration created" -ForegroundColor Green
}

# Generate tokens and start server
Write-Host "🔐 Generating JWT tokens and starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Server will be available at: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔧 Health check: http://localhost:8080/health" -ForegroundColor Cyan
Write-Host "💬 WebSocket: ws://localhost:8080/chat/ws/{room}?token={jwt}" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Cyan

# Start the UltraCom system
python start.py

Write-Host ""
Write-Host "🛑 UltraCom system stopped" -ForegroundColor Red
