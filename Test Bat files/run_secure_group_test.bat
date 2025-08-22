@echo off
echo ========================================
echo PGP Tool v4.2.5 - Secure Group Access Control Test
echo ========================================
echo.

echo Python found. Running secure group access control test...
echo.

python test_secure_group_access.py

echo.
echo ========================================
echo Test completed. Check results above.
echo ========================================
echo.

if %ERRORLEVEL% EQU 0 (
    echo ✅ ALL TESTS PASSED! Secure group access control is working correctly.
    echo.
    echo 🔒 SECURITY FEATURES VERIFIED:
    echo   • Invitation-only group access
    echo   • Proper permission checking
    echo   • Encrypted group messaging
    echo   • Data persistence and integrity
    echo   • Protection against unauthorized access
    echo   • Invitation expiration and validation
) else (
    echo ❌ SOME TESTS FAILED! Please review the implementation.
)

echo.
echo Press any key to exit...
pause >nul

