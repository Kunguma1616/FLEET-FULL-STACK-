@echo off
REM Start both backend and frontend servers

echo.
echo ============================================================
echo  🚀 FLEET HEALTH MONITOR - FULL STARTUP
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: backend folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Starting services...
echo.

REM Start backend in a new window
echo 1️⃣  Starting Backend Server on port 8002...
start cmd /k "cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in a new window
echo 2️⃣  Starting Frontend Server on port 5174...
start cmd /k "npm run dev"

echo.
echo ============================================================
echo ✅ Both servers started!
echo.
echo 🌐 Frontend:  http://localhost:5174/
echo 🔌 Backend:   http://localhost:8002/
echo.
echo 📝 Login with: Kung.Balaji@aspect.co.uk
echo.
echo ============================================================
echo Press any key to close this window...
pause
