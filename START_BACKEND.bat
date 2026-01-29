@echo off
REM Fleet Health Monitor - Quick Start Script

echo.
echo ========================================
echo   Fleet Health Monitor - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python detected

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)
echo ✅ Node.js detected

REM Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm not found!
    pause
    exit /b 1
)
echo ✅ npm detected

echo.
echo ========================================
echo   Setting up Backend...
echo ========================================
echo.

cd backend

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.template .env
    echo.
    echo ⚠️  Please edit backend\.env with:
    echo    - Salesforce credentials (SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN)
    echo    - Microsoft OAuth credentials (MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET)
    echo.
    echo Press any key when ready...
    pause
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

REM Test Salesforce connection
echo.
echo Testing Salesforce connection...
python -c "from salesforce_service import SalesforceService; print('✅ Salesforce connected')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Salesforce connection failed!
    echo Check your .env credentials and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Backend Setup Complete!
echo ========================================
echo.
echo Starting Backend on http://localhost:8000
echo Press Ctrl+C to stop
echo.

REM Start backend
python app.py

pause
