#!/usr/bin/env bash

echo "==================================================="
echo "    PC Optimizer Pro (Linux / macOS) ishga tushmoqda"
echo "==================================================="

# Python tekshirish
if ! command -v python3 &> /dev/null
then
    echo "[XATO] python3 topilmadi! Iltimos, Python o'rnating."
    exit 1
fi

# Kutubxonalarni o'rnatish
echo "Kutubxonalar tekshirilmoqda..."
pip3 install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet

# Serverni ishga tushirish
echo "Dastur ishga tushmoqda..."
python3 app.py || python app.py
