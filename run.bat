@echo off
title PC Optimizer Pro
echo ===================================================
echo     PC Optimizer Pro ishga tushirilmoqda...
echo ===================================================
echo.

:: Python tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi! Iltimos, Python 3.8+ o'rnating.
    pause
    exit /b
)

:: Kutubxonalarni tekshirish va o'rnatish
echo Kerakli kutubxonalar tekshirilmoqda...
pip install -r requirements.txt --quiet

:: Dasturni ishga tushirish
echo Dastur ishga tushmoqda...
python app.py
pause
