# UltraWeb Directory Separation Script
# Creates isolated zones for each technology to eliminate conflicts

Write-Host "🚀 CREATING SEPARATE TECHNOLOGY ZONES..." -ForegroundColor Green
Write-Host "This will eliminate ALL package manager conflicts!" -ForegroundColor Yellow

# Create main directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Cyan
$directories = @(
    "frontend",
    "frontend/pages", 
    "frontend/components",
    "frontend/lib",
    "backend",
    "backend/app", 
    "mesh",
    "mesh/peers",
    "iot", 
    "iot/devices",
    "iot/sensors",
    "blockchain",
    "blockchain/contracts",
    "blockchain/migrations", 
    "shared",
    "shared/docs",
    "shared/scripts",
    "shared/configs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Already exists: $dir" -ForegroundColor Yellow
    }
}

# Create frontend package.json
Write-Host "📦 Creating frontend package.json..." -ForegroundColor Cyan
$frontendPackageJson = @"
{
  "name": "ultrawebthinking-frontend",
  "version": "1.0.0",
  "private": true,
  "packageManager": "yarn@4.10.3",
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build", 
    "start": "next start -p 3001",
    "clean": "rimraf .next node_modules yarn.lock"
  },
  "dependencies": {
    "next": "^14.2.33",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "rimraf": "^5.0.0"
  }
}
"@

Set-Content -Path "frontend/package.json" -Value $frontendPackageJson -Encoding UTF8

# Create backend requirements.txt
Write-Host "🐍 Creating backend requirements.txt..." -ForegroundColor Cyan
$backendRequirements = @"
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
aiohttp>=3.8.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
greenlet>=2.0.0
"@

Set-Content -Path "backend/requirements.txt" -Value $backendRequirements -Encoding UTF8

# Create backend main.py
Write-Host "⚡ Creating backend main.py..." -ForegroundColor Cyan
$backendMain = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UltraWeb Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "UltraWeb Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
"@

Set-Content -Path "backend/main.py" -Value $backendMain -Encoding UTF8

# Create root master package.json
Write-Host "🎯 Creating master control package.json..." -ForegroundColor Cyan
$masterPackageJson = @"
{
  "name": "ultrawebthinking-master",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev:frontend": "cd frontend && yarn dev",
    "dev:backend": "cd backend && python -m uvicorn main:app --reload --port 8000",
    "dev:all": "concurrently --names \"Frontend,Backend\" --prefix-colors \"green,blue\" \"npm run dev:frontend\" \"npm run dev:backend\"",
    "setup:frontend": "cd frontend && yarn install",
    "setup:backend": "cd backend && pip install -r requirements.txt", 
    "setup:all": "npm run setup:frontend && npm run setup:backend",
    "clean:frontend": "cd frontend && yarn clean",
    "clean:backend": "cd backend && Remove-Item __pycache__ -Recurse -Force -ErrorAction SilentlyContinue",
    "clean:all": "npm run clean:frontend && npm run clean:backend",
    "test:frontend": "curl -s http://localhost:3000",
    "test:backend": "curl -s http://localhost:8000/health", 
    "test:all": "npm run test:frontend && npm run test:backend"
  },
  "devDependencies": {
    "concurrently": "^9.2.1"
  }
}
"@

Set-Content -Path "package-master.json" -Value $masterPackageJson -Encoding UTF8

# Create reset script
Write-Host "🚨 Creating emergency reset script..." -ForegroundColor Cyan
$resetScript = @"
Write-Host "🚨 EMERGENCY RESET - ALL ZONES" -ForegroundColor Red

# Kill all processes
Write-Host "🛑 Stopping all processes..." -ForegroundColor Yellow
taskkill /F /IM node.exe /T 2>`$null
taskkill /F /IM python.exe /T 2>`$null

# Clean frontend zone
Write-Host "🧹 Cleaning frontend zone..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    Set-Location frontend
    yarn cache clean --all 2>`$null
    Remove-Item .next -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
    Set-Location ..
}

# Clean backend zone
Write-Host "🐍 Cleaning backend zone..." -ForegroundColor Cyan
if (Test-Path "backend") {
    Set-Location backend
    pip cache purge 2>`$null
    Remove-Item __pycache__ -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item venv -Recurse -Force -ErrorAction SilentlyContinue  
    Set-Location ..
}

Write-Host "✅ ALL ZONES RESET COMPLETE!" -ForegroundColor Green
Write-Host "🚀 Ready to setup: npm run setup:all" -ForegroundColor Cyan
"@

Set-Content -Path "shared/scripts/reset-all.ps1" -Value $resetScript -Encoding UTF8

# Create zone startup script
Write-Host "🎮 Creating zone startup script..." -ForegroundColor Cyan
$startupScript = @"
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
    `$frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend Zone: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend Zone: NOT RESPONDING" -ForegroundColor Red
}

try {
    `$backend = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend Zone: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Zone: NOT RESPONDING" -ForegroundColor Red
}

Write-Host "🎯 ZONE STARTUP COMPLETE!" -ForegroundColor Green
"@

Set-Content -Path "shared/scripts/start-zones.ps1" -Value $startupScript -Encoding UTF8

Write-Host ""
Write-Host "🎉 DIRECTORY SEPARATION COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. npm install (install concurrently for master control)" -ForegroundColor White
Write-Host "2. npm run setup:all (setup both zones)" -ForegroundColor White  
Write-Host "3. npm run dev:all (start both zones)" -ForegroundColor White
Write-Host "4. Or use: ./shared/scripts/start-zones.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🚨 Emergency Reset: ./shared/scripts/reset-all.ps1" -ForegroundColor Red
Write-Host ""
Write-Host "🎯 NO MORE CONFLICTS - EACH ZONE IS ISOLATED!" -ForegroundColor Green
