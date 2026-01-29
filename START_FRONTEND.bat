@echo off
REM Fleet Health Monitor - Frontend Start Script

echo.
echo ========================================
echo   Fleet Health Monitor - Frontend
echo ========================================
echo.

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
echo   Installing Dependencies...
echo ========================================
echo.

REM Install dependencies
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo ========================================
echo   Starting Frontend Development Server
echo ========================================
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend must be running on: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

REM Start dev server
npm run dev

pause
