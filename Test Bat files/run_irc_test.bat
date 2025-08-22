@echo off
echo Starting IRC Client Test for PGP Tool v4.2.0...
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
echo Starting IRC Test Interface...
echo.
echo Instructions:
echo 1. Click "Random" to generate a nickname
echo 2. Select a network (Libera, OFTC, or EFNet)
echo 3. Click "Connect" to connect to IRC
echo 4. Enter a target nickname and message to test
echo 5. Test with another IRC client or user
echo.

python test_irc_client.py

echo.
echo IRC Test completed.
pause

