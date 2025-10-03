@echo off
chcp 65001 >nul
echo ========================================
echo 小柳云端Git提交工具
echo ========================================
echo.

set /p commit_msg="请输入提交说明: "

if "%commit_msg%"=="" (
    set commit_msg=更新小柳系统
)

echo.
echo 正在连接服务器并提交...
echo.

ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53 "cd /home/ubuntu/xiaoliu && git add . && git commit -m '%commit_msg%' && git push origin main"

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo ✅ 提交成功！
    echo ========================================
    echo.
    echo 查看GitHub: https://github.com/daxiak001/xiaoliu
) else (
    echo.
    echo ========================================
    echo ❌ 提交失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. 网络连接问题
    echo 2. SSH密钥认证失败
    echo 3. Git仓库有冲突
    echo.
    echo 请查看上面的错误信息
)

echo.
pause

