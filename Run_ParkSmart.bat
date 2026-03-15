@echo off
setlocal
title ParkSmart AI Launcher

:: Get the directory of this script
cd /d "%~dp0"

echo ========================================================
echo   Launching ParkSmart AI (Integrated System)
echo ========================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python.
    pause
    exit /b 1
)

:: Run the consolidated main script
echo [INFO] Starting application...
python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application crashed or failed to start.
    pause
    exit /b %ERRORLEVEL%
)

pause
