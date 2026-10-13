# ⚡ PC Optimizer Pro (Cross-Platform)

Barcha qurilmalar (Windows, Linux, macOS, Docker, hamda Wi-Fi orqali Telefon va Planshetlar) uchun mo'ljallangan zamonaviy tizim nazorati va optimallashtirish dasturi.

![Cross Platform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Devices](https://img.shields.io/badge/Devices-PC%20%7C%20Laptop%20%7C%20Mobile%20%7C%20Tablet-purple)
![Python](https://img.shields.io/badge/Python-3.8+-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)

---

## 🌟 Nega "Barcha Qurilmalar"?

1. **💻 Cross-Platform Operatsion Tizimlar:**
   - **Windows:** Temp fayllar, Windows Registry avto-yuklanish dasturlari, Savat (Recycle Bin), DNS kesh.
   - **Linux:** `/tmp`, `/var/tmp`, `~/.cache`, `~/.config/autostart` tizimi.
   - **macOS:** `~/Library/Caches`, `/tmp`, LaunchAgents avto-yuklanish, Trash tozalash.
2. **📱 Telefon va Planshetdan boshqarish:**
   - Server lokal tarmoqda (`0.0.0.0:5000`) ochiladi.
   - Bir xil Wi-Fi tarmog'idagi istalgan telefon, iPhone, Android yoki planshetdan kompyuteringiz holatini nazorat qilishingiz mumkin.
3. **🐳 Docker & Server yordami:**
   - Istalgan Linux server, VPS yoki konteynerda `docker compose up -d` orqali ishga tushadi.

---

## 🚀 Har Qanday Qurilmada Ishga Tushirish

### 🪟 1. Windows:
`run.bat` faylini ikki marta bosing yoki terminalda:
```powershell
python app.py
```

### 🐧 2. Linux va 🍎 macOS:
Terminalda:
```bash
chmod +x run.sh
./run.sh
```

### 🐳 3. Docker orqali:
```bash
docker compose up -d
```

### 📱 4. Telefon yoki Planshetdan kirish:
1. Kompyuteringiz va telefoningiz bir xil Wi-Fi tarmog'iga ulangan bo'lsin.
2. Dastur terminalda chiqargan manzilni telefon brauzeriga kiriting:
   👉 `http://<KOMPYUTER_IP>:5000` *(masalan: `http://192.168.1.15:5000`)*

---

## 📂 Loyiha Fayllari

```
pc_cleaner/
├── app.py                # Kross-platforma backend (Windows, Linux, macOS)
├── run.bat               # Windows uchun 1-klik ishga tushiruvchi
├── run.sh                # Linux / macOS uchun 1-klik skripti
├── Dockerfile            # Docker konteynerlashtirish
├── docker-compose.yml    # Docker Compose konfiguratsiyasi
├── requirements.txt      # Python kutubxonalari
├── .gitignore            # Git istisno fayllari
├── README.md             # Qo'llanma
└── templates/
    └── index.html        # Responsive zamonaviy Dark Mode veb-interfeysi
```

---

## ⚖️ Litsenziya
MIT License
