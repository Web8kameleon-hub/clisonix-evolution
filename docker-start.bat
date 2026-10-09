@echo off
echo Starting Docker Desktop...
"C:\Program Files\Docker\Docker\resources\com.docker.desktop.exe"
echo Wait 30s for startup...
timeout /t 30 /nobreak >nul
docker ps || echo Docker still not ready
pause
