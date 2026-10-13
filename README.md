# ⚡ PC Optimizer Pro v2.0

Zamonaviy veb-interfeysga ega Windows tizim diagnostikasi, xotirani tozalash va optimallashtirish dasturi (Python & Flask).

![Dashboard Preview](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-black.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3-38bdf8.svg)

---

## 🚀 Asosiy Imkoniyatlar

1. **📊 Jonli Tizim Diagnostikasi (Monitor):**
   - Real vaqtda CPU chastotasi va foydalanish foizi.
   - RAM (Tezkor xotira) bandligi (GB va foizda).
   - Barcha ichki va tashqi drayverlar (SSD/HDD) bo'sh/band holati.
   - Har 5 soniyada avtomatik jonli yangilanish.

2. **🧹 Chuqur Tozalash (Deep Clean):**
   - **Tizim vaqtinchalik fayllari:** `%TEMP%` va `C:\Windows\Temp` papkalaridagi axlatlarni tozalash.
   - **Brauzer keshlarini tozalash:** Google Chrome, Microsoft Edge, Brave va Opera veb-keshlarini o'chirish.

3. **🚀 Avto-yuklanishni boshqarish (Startup Manager):**
   - Windows ochilganda orqa fonda avtomatik ishga tushuvchi barcha dasturlarni ko'rish.
   - Keraksiz dasturlarni Windows Registry'dan o'chirish va yuklanish tezligini oshirish.

4. **🔍 Fayl Vositalari:**
   - **Katta fayllarni aniqlash:** Belgilangan papkadagi eng og'ir (50MB+, 100MB+, 500MB+, 1GB+) fayllarni topish va o'chirish.
   - **Dublikat fayllarni qidirish:** Downloads papkasidagi bir xil nusxa fayllarni tezkor xeshlash (MD5) orqali aniqlash.

5. **🛡️ Xavfsizlik & Tizim vositalari:**
   - Vaqtinchalik (`Temp`) papkadan ishlayotgan shubhali jarayonlarni aniqlash va to'xtatish.
   - Savatni (Recycle Bin) bitta tugma bilan tozalash.
   - DNS keshini tozalash (`ipconfig /flushdns`).

---

## 🛠️ O'rnatish va Ishga Tushirish

### 1. Repozitoriyani yuklab oling:
```bash
git clone https://github.com/<USERNAME>/pc-optimizer-pro.git
cd pc-optimizer-pro
```

### 2. Kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

### 3. Serverni ishga tushiring:
```bash
python app.py
```

Brauzeringizda oching:
👉 `http://127.0.0.1:5000`

> 💡 **Maslahat:** Tizim fayllarini va Windows Registry parametrlarini xatosiz boshqarish uchun terminalni **"Administrator sifatida"** ishga tushirish tavsiya etiladi.

---

## 📂 Loyiha Tuzilmasi

```
pc_cleaner/
├── app.py                # Asosiy Flask backend va diagnostika logikasi
├── requirements.txt      # Kerakli Python paketlari (flask, psutil)
├── .gitignore            # Git e'tiborsiz qoldiradigan fayllar
├── README.md             # Loyiha hujjatlari
└── templates/
    └── index.html        # Zamonaviy Tailwind CSS Dark Mode interfeysi
```

---

## ⚖️ Litsenziya
MIT License
