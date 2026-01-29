@echo off
REM Start both backend and frontend servers

echo.
echo ===============================================
echo Fleet Health Monitor - Starting Servers
echo ===============================================
echo.

REM Check if running in the correct directory
if not exist "backend\app.py" (
    echo ERROR: backend\app.py not found!
    echo Please run this script from the root directory
    pause
    exit /b 1
)

REM Start backend in a new window
echo Starting Backend Server (Port 8000)...
start cmd /k "cd backend && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in a new window
echo Starting Frontend Server (Port 5173)...
start cmd /k "npm run dev"

echo.
echo ===============================================
echo Servers started in separate windows!
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo.
echo Close either window to stop that server.
echo ===============================================
echo.

pause
