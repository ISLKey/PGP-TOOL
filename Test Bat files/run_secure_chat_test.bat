@echo off
echo Starting Secure Chat Test for PGP Tool v4.2.0...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Secure Chat Test Interface...
echo.
echo Instructions:
echo 1. Initialize PGP with a test directory
echo 2. Generate or import PGP keys for testing
echo 3. Connect to IRC network
echo 4. Add contacts with their IRC nicknames and PGP fingerprints
echo 5. Send encrypted messages to test contacts
echo.
echo Note: This tests PGP+IRC integration before full UI integration
echo.

python test_secure_chat.py

echo.
echo Secure Chat Test completed.
pause

