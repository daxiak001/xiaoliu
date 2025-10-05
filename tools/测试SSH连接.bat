@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   测试SSH连接
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "quick-ssh-v2.ps1" -Command "ls -lh /home/ubuntu/xiaoliu/"

echo.
pause
