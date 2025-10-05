@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   SSH连接修复工具
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "fix-ssh-hang.ps1"

echo.
pause
