@echo off
REM Build script for com0com GUI Manager
REM Run this batch file from the project root to build the executable on Windows

echo =========================================
echo com0com GUI Manager - Build Script
echo =========================================
echo.

REM Change to project root if we're in scripts directory
if /I "%~dp0" == "%CD%\scripts\" (
    cd ..
    echo Changed to project root: %CD%
)

REM Verify we're in the correct location
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the project root directory.
    echo Usage: scripts\build.bat
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

REM Install build requirements
echo Installing build dependencies...
pip install -r scripts\requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install build dependencies
    pause
    exit /b 1
)

echo.
echo Starting build process...
echo.

REM Run the Python build script
python scripts\build.py

echo.
echo Build process completed.
pause