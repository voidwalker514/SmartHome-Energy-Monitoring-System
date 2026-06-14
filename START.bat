@echo off
REM Smart Home Energy Monitoring System - Quick Start Script
REM This script sets up and runs the entire project

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   Smart Home Energy Monitoring System - Quick Start            ║
echo ║   Python 3.8+ Required                                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8 or higher.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if requirements are already installed
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

echo.
echo 📁 Creating necessary directories...
if not exist "data" mkdir data
if not exist "outputs" mkdir outputs
echo ✅ Directories ready

echo.
echo 🚀 Starting Flask server...
echo.
echo ═══════════════════════════════════════════════════════════════════
echo   Dashboard will be available at: http://localhost:5000
echo   
echo   Press Ctrl+C to stop the server
echo ═══════════════════════════════════════════════════════════════════
echo.

python app.py

pause
