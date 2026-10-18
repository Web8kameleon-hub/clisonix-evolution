# ALBA/ASI Ultra System Launcher - PowerShell Version
Write-Host "🚀 ALBA/ASI Ultra System Launcher" -ForegroundColor Green
Write-Host "🔥 Starting Complete Autonomous Platform..." -ForegroundColor Yellow
Write-Host ""

# Function to display colored output
function Write-ColorOutput {
    param(
        [string]$ForegroundColor = "White",
        [string]$BackgroundColor = "Black", 
        [string]$Prefix,
        [string]$Message
    )
    Write-Host "[$Prefix] " -ForegroundColor $ForegroundColor -NoNewline
    Write-Host $Message -ForegroundColor White
}

# Start UltraCom Backend
Write-ColorOutput -ForegroundColor Cyan -Prefix "ULTRACOM" -Message "Starting AI Manager Backend on port 8080..."

$BackendJob = Start-Job -ScriptBlock {
    param($WorkingDir)
    Set-Location "$WorkingDir\ultracom"
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
} -ArgumentList $PSScriptRoot

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Next.js Frontend
Write-ColorOutput -ForegroundColor Magenta -Prefix "NEXTJS" -Message "Starting Frontend with automatic port detection..."

$FrontendJob = Start-Job -ScriptBlock {
    param($WorkingDir)
    Set-Location $WorkingDir
    yarn dev
} -ArgumentList $PSScriptRoot

# Wait for services to start
Start-Sleep -Seconds 5

Write-Host ""
Write-ColorOutput -ForegroundColor Green -Prefix "🎯 SUCCESS" -Message "ALBA/ASI Ultra System is running!"
Write-ColorOutput -ForegroundColor Blue -Prefix "📡 BACKEND" -Message "UltraCom AI Manager: http://localhost:8080"
Write-ColorOutput -ForegroundColor Magenta -Prefix "🌐 FRONTEND" -Message "Next.js auto-detected available port"
Write-ColorOutput -ForegroundColor Yellow -Prefix "📊 APIs" -Message "ALBA/ASI Hub, Life Sciences, Cultural Hub ready!"
Write-ColorOutput -ForegroundColor Cyan -Prefix "🤖 AI MANAGER" -Message "Zero Human Intervention Mode Active"
Write-Host ""
Write-Host "🚀 Press Ctrl+C to stop all services" -ForegroundColor Green

# Monitor jobs and keep script alive
try {
    while ($true) {
        if ($BackendJob.State -eq "Failed") {
            Write-ColorOutput -ForegroundColor Red -Prefix "ERROR" -Message "Backend job failed!"
            break
        }
        if ($FrontendJob.State -eq "Failed") {
            Write-ColorOutput -ForegroundColor Red -Prefix "ERROR" -Message "Frontend job failed!"
            break
        }
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-ColorOutput -ForegroundColor Yellow -Prefix "CLEANUP" -Message "Stopping all services..."
    Stop-Job $BackendJob -ErrorAction SilentlyContinue
    Stop-Job $FrontendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob -ErrorAction SilentlyContinue
    Remove-Job $FrontendJob -ErrorAction SilentlyContinue
    Write-ColorOutput -ForegroundColor Red -Prefix "SHUTDOWN" -Message "ALBA/ASI Ultra System stopped."
}
