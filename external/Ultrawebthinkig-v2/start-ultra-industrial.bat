@echo off
echo 🏭 ULTRA INDUSTRIAL PRODUCTION SYSTEM
echo ====================================
echo Starting Ultra Industrial Engine with REAL DATA ONLY...
echo.

REM Check if .env.local exists
if not exist ".env.local" (
    echo ❌ .env.local file not found!
    echo.
    echo 📋 Please create .env.local file with your API keys:
    echo OPENWEATHER_API_KEY=your_openweather_key_here
    echo ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here  
    echo NASA_API_KEY=your_nasa_key_here
    echo.
    echo Get free API keys from:
    echo - OpenWeatherMap: https://openweathermap.org/api
    echo - Alpha Vantage: https://www.alphavantage.co/support/#api-key
    echo - NASA: https://api.nasa.gov/
    echo.
    pause
    exit /b 1
)

echo ✅ Found .env.local file
echo 🚀 Starting development server on port 3002...
echo.
echo Ultra Industrial Dashboard will be available at:
echo http://localhost:3002/ultra-industrial
echo.
echo Features:
echo ✅ Real Weather Data (OpenWeatherMap)
echo ✅ Real Financial Data (Alpha Vantage)  
echo ✅ Real Satellite Data (NASA)
echo ✅ Real System Metrics (Node.js)
echo ✅ Zero Mock Data - 100%% Production Ready
echo.

npm run dev

pause
