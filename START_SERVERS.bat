@echo off
REM Fleet Health Monitor - Quick Start Script (Windows)
REM This script starts both backend and frontend servers

echo.
echo ============================================================
echo   FLEET HEALTH MONITOR - QUICK START
echo ============================================================
echo.
echo This will open 2 terminal windows:
echo   1. Backend server (Port 8000)
echo   2. Frontend server (Port 5173)
echo.
pause

REM Get the current directory
set SCRIPT_DIR=%~dp0

echo.
echo [1/2] Starting Backend Server...
echo.
cd /d "%SCRIPT_DIR%backend"
start cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 3 seconds before starting frontend...
timeout /t 3 /nobreak

echo.
echo [2/2] Starting Frontend Server...
echo.
cd /d "%SCRIPT_DIR%"
start cmd /k "npm run dev"

echo.
echo ============================================================
echo   SERVERS STARTING
echo ============================================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Check browser console (F12) if you see errors.
echo.
pause
