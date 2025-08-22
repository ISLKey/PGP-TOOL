@echo off
title PGP Tool v4.2.0 - Windows Launcher
cls

echo ========================================
echo PGP Tool v4.2.0
echo Developed by Jamie Johnson (TriggerHappyMe)
echo Professional PGP Encryption ^& Secure Communication Platform
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% found

echo [2/5] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)
echo pip is available

echo [3/5] Checking required packages...
echo - cryptography: 
python -c "import cryptography; print('OK')" 2>nul || echo NOT FOUND
echo - pillow: 
python -c "import PIL; print('OK')" 2>nul || echo NOT FOUND
echo - tkinter: 
python -c "import tkinter; print('OK')" 2>nul || (
    echo NOT FOUND
    echo WARNING: tkinter is required but not found. Your Python installation may be incomplete.
)

echo.
echo [4/5] Installing missing packages...
echo Installing: cryptography pillow
echo This may take a few minutes...
python -m pip install cryptography pillow --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo All packages installed successfully

echo [5/5] Starting PGP Encryption Tool...
echo.
echo Starting PGP Encryption Tool...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application exited with error code %errorlevel%
    echo.
    echo This version uses pure Python cryptography and does not require GPG.
    echo If you continue to experience issues, please check:
    echo 1. Python version is 3.7 or later
    echo 2. All required packages are installed
    echo 3. You have sufficient permissions to create files
    echo.
)

echo.
pause

