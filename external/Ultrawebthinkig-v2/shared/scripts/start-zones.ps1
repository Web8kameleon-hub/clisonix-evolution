Write-Host "🚀 ULTRAWEBTHINKING ZONE STARTUP" -ForegroundColor Green

Write-Host "🎯 Starting Frontend Zone (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-Command", "cd frontend; yarn dev" -WindowStyle Minimized

Start-Sleep 3

Write-Host "🐍 Starting Backend Zone (Port 8000)..." -ForegroundColor Blue  
Start-Process powershell -ArgumentList "-Command", "cd backend; python -m uvicorn main:app --reload --port 8000" -WindowStyle Minimized

Write-Host "⏱️ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep 10

Write-Host "🧪 Testing zones..." -ForegroundColor Green
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend Zone: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend Zone: NOT RESPONDING" -ForegroundColor Red
}

try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend Zone: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Zone: NOT RESPONDING" -ForegroundColor Red
}

Write-Host "🎯 ZONE STARTUP COMPLETE!" -ForegroundColor Green
