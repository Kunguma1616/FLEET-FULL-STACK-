@echo off
echo.
echo ============================================================
echo  ✅ SYSTEM VERIFICATION
echo ============================================================
echo.

REM Check if ports are listening
echo Checking if services are running...
echo.

REM Check backend on 8002
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo ✅ Backend running on port 8002 (PID: %%a)
    goto frontend_check
)
echo ❌ Backend NOT running on port 8002
goto frontend_check

:frontend_check
REM Check frontend on 5174
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174') do (
    echo ✅ Frontend running on port 5174 (PID: %%a)
    goto success
)
echo ❌ Frontend NOT running on port 5174
goto success

:success
echo.
echo ============================================================
echo Configuration Summary:
echo.
echo 🌐 Frontend URL:  http://localhost:5174/
echo 🔌 Backend URL:   http://localhost:8002/
echo 🔐 Auth Method:   Microsoft OAuth (@aspect.co.uk)
echo.
echo ============================================================
echo.
pause
