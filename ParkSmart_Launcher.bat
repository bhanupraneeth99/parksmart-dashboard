@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   Launching Smart Parking Management System...
echo ========================================================
echo.

:: Check for PowerShell
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PowerShell not found. Please install PowerShell to run this system.
    pause
    exit /b 1
)

:: Run the PowerShell startup script
powershell.exe -ExecutionPolicy Bypass -File "run_system.ps1"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] System failed to start. Review the logs above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Opening Dashboard...
pause
