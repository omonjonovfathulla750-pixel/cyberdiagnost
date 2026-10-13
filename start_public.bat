@echo off
title PC Optimizer Pro (Public Cloudflare Tunnel)
echo ========================================================
echo    PC Optimizer Pro - Butun Dunyo uchun Ochiq Tunnel
echo ========================================================
echo.

if not exist cloudflared.exe (
    echo [Yuklanmoqda] cloudflared.exe yuklab olinmoqda...
    curl.exe -L -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
)

echo Tunnel ishga tushmoqda...
echo Quyida paydo bo'ladigan https://xxxx.trycloudflare.com havolasi orqali
echo istalgan telefon yoki kompyuterdan kirishingiz mumkin!
echo.
cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
