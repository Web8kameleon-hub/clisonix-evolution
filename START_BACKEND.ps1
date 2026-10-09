Write-Host "Starting Backend API (port 8000)..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
cd c:\Users\Admin\Desktop\Clisonix-cloud
$env:PYTHONPATH = "."
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
