import os
import shutil
import hashlib
import subprocess
import winreg
import psutil
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- 1. TIZIM VA SSD DIAGNOSTIKASI ---
class SystemDiagnoser:
    @staticmethod
    def get_system_stats():
        cpu_usage = psutil.cpu_percent(interval=0.3)
        cpu_freq = psutil.cpu_freq()
        ram = psutil.virtual_memory()
        
        disks_info = []
        for partition in psutil.disk_partitions():
            try:
                if 'cdrom' in partition.opts or partition.fstype == '':
                    continue
                usage = psutil.disk_usage(partition.mountpoint)
                disks_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total": round(usage.total / (1024**3), 2),
                    "free": round(usage.free / (1024**3), 2),
                    "used": round(usage.used / (1024**3), 2),
                    "percent": usage.percent
                })
            except (PermissionError, OSError):
                continue
                
        return {
            "cpu": cpu_usage,
            "cpu_freq_ghz": round(cpu_freq.current / 1000, 2) if cpu_freq else 0,
            "ram": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "disks": disks_info
        }

# --- 2. KERAKSIZ FAYLLAR (TEMP VA KESH) ---
class JunkCleaner:
    def __init__(self):
        self.target_paths = [
            os.path.expandvars(r'%TEMP%'),
            r'C:\Windows\Temp',
            os.path.expandvars(r'%LOCALAPPDATA%\Temp')
        ]
        self.target_paths = list(set([p for p in self.target_paths if os.path.exists(p)]))

    def scan_junk(self):
        total_bytes = 0
        file_list = []
        for folder in self.target_paths:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        f_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(f_path)
                            total_bytes += size
                            file_list.append(f_path)
                        except Exception:
                            continue
        return round(total_bytes / (1024 * 1024), 2), file_list

    def clean_junk(self):
        _, files = self.scan_junk()
        deleted = 0
        freed_bytes = 0
        for f_path in files:
            try:
                size = os.path.getsize(f_path)
                os.remove(f_path)
                deleted += 1
                freed_bytes += size
            except Exception:
                continue
        return {
            "deleted": deleted,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2)
        }

# --- 3. BRAUZER KESHLARINI TOZALASH ---
class BrowserCleaner:
    @staticmethod
    def get_cache_paths():
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        app_data = os.environ.get('APPDATA', '')
        
        candidates = {
            "Google Chrome": [
                os.path.join(local_app_data, r'Google\Chrome\User Data\Default\Cache'),
                os.path.join(local_app_data, r'Google\Chrome\User Data\Default\Code Cache')
            ],
            "Microsoft Edge": [
                os.path.join(local_app_data, r'Microsoft\Edge\User Data\Default\Cache'),
                os.path.join(local_app_data, r'Microsoft\Edge\User Data\Default\Code Cache')
            ],
            "Brave Browser": [
                os.path.join(local_app_data, r'BraveSoftware\Brave-Browser\User Data\Default\Cache')
            ],
            "Opera": [
                os.path.join(app_data, r'Opera Software\Opera Stable\Cache')
            ]
        }
        
        valid = {}
        for browser, paths in candidates.items():
            existing = [p for p in paths if os.path.exists(p)]
            if existing:
                valid[browser] = existing
        return valid

    @staticmethod
    def scan_browser_cache():
        cache_paths = BrowserCleaner.get_cache_paths()
        result = []
        total_mb = 0

        for browser, paths in cache_paths.items():
            b_size = 0
            b_count = 0
            for folder in paths:
                for root, _, files in os.walk(folder):
                    for file in files:
                        try:
                            f_path = os.path.join(root, file)
                            b_size += os.path.getsize(f_path)
                            b_count += 1
                        except Exception:
                            continue
            mb = round(b_size / (1024 * 1024), 2)
            total_mb += mb
            result.append({
                "browser": browser,
                "size_mb": mb,
                "files_count": b_count
            })
        return round(total_mb, 2), result

    @staticmethod
    def clean_browser_cache():
        cache_paths = BrowserCleaner.get_cache_paths()
        deleted = 0
        freed_bytes = 0
        for _, paths in cache_paths.items():
            for folder in paths:
                for root, _, files in os.walk(folder):
                    for file in files:
                        try:
                            f_path = os.path.join(root, file)
                            sz = os.path.getsize(f_path)
                            os.remove(f_path)
                            deleted += 1
                            freed_bytes += sz
                        except Exception:
                            continue
        return {
            "deleted": deleted,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2)
        }

# --- 4. STARTUP MANAGER (AVTO-YUKLANISH TIZIMI) ---
class StartupManager:
    @staticmethod
    def get_startup_apps():
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
        ]
        apps = []
        for hkey, subkey, loc_name in locations:
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                    num_values = winreg.QueryInfoKey(key)[1]
                    for i in range(num_values):
                        name, val, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": name,
                            "path": val,
                            "location": loc_name
                        })
            except Exception:
                continue
        return apps

    @staticmethod
    def remove_startup_app(name, location):
        hkey = winreg.HKEY_CURRENT_USER if location == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
                return True
        except Exception:
            return False

# --- 5. KATTA FAYLLARNI QIDIRISH (LARGE FILE FINDER) ---
class LargeFilesFinder:
    @staticmethod
    def find_large_files(target_dir, min_size_mb=100, limit=20):
        if not os.path.exists(target_dir):
            return []
        min_bytes = min_size_mb * 1024 * 1024
        large_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                f_path = os.path.join(root, file)
                try:
                    if os.path.islink(f_path):
                        continue
                    sz = os.path.getsize(f_path)
                    if sz >= min_bytes:
                        large_files.append({
                            "name": file,
                            "path": f_path,
                            "size_mb": round(sz / (1024 * 1024), 2)
                        })
                except Exception:
                    continue
        large_files.sort(key=lambda x: x["size_mb"], reverse=True)
        return large_files[:limit]

# --- 6. DUBLIKAT FAYLLARNI QIDIRISH ---
class DuplicateFinder:
    @staticmethod
    def get_file_hash(file_path, quick=False):
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                if quick:
                    chunk = f.read(8192)
                    hasher.update(chunk)
                else:
                    for buf in iter(lambda: f.read(65536), b''):
                        hasher.update(buf)
            return hasher.hexdigest()
        except Exception:
            return None

    @staticmethod
    def find_duplicates(target_dir):
        if not os.path.exists(target_dir):
            return []

        size_dict = {}
        for root, _, files in os.walk(target_dir):
            for file in files:
                f_path = os.path.join(root, file)
                try:
                    if os.path.islink(f_path):
                        continue
                    size = os.path.getsize(f_path)
                    if size > 0:
                        size_dict.setdefault(size, []).append(f_path)
                except Exception:
                    continue
        
        duplicates = []
        for size, paths in size_dict.items():
            if len(paths) > 1:
                quick_hash_dict = {}
                for p in paths:
                    qh = DuplicateFinder.get_file_hash(p, quick=True)
                    if qh:
                        quick_hash_dict.setdefault(qh, []).append(p)
                
                for _, q_paths in quick_hash_dict.items():
                    if len(q_paths) > 1:
                        full_hash_dict = {}
                        for p in q_paths:
                            fh = DuplicateFinder.get_file_hash(p, quick=False)
                            if fh:
                                full_hash_dict.setdefault(fh, []).append(p)
                        for _, f_paths in full_hash_dict.items():
                            if len(f_paths) > 1:
                                duplicates.append({
                                    "original": f_paths[0],
                                    "duplicates": f_paths[1:],
                                    "size_mb": round(size / (1024 * 1024), 2)
                                })
        return duplicates

# --- 7. VIRUS VA SHUBHALI JARAYONLAR ---
class VirusScanner:
    @staticmethod
    def scan_processes():
        suspicious = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                exe = proc.info['exe']
                if exe and "temp" in exe.lower():
                    suspicious.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "exe": exe,
                        "user": proc.info.get('username', 'Noma\'lum')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return suspicious


# --- FLASK ROUTES ---
@app.route('/')
def index():
    stats = SystemDiagnoser.get_system_stats()
    junk_mb, junk_files = JunkCleaner().scan_junk()
    browser_total_mb, browser_details = BrowserCleaner.scan_browser_cache()
    suspicious_procs = VirusScanner.scan_processes()
    startup_apps = StartupManager.get_startup_apps()
    
    return render_template('index.html', 
                           stats=stats, 
                           junk_mb=junk_mb, 
                           junk_count=len(junk_files),
                           browser_total_mb=browser_total_mb,
                           browser_details=browser_details,
                           suspicious_count=len(suspicious_procs),
                           suspicious_procs=suspicious_procs,
                           startup_apps=startup_apps)

@app.route('/api/stats')
def api_stats():
    stats = SystemDiagnoser.get_system_stats()
    junk_mb, junk_files = JunkCleaner().scan_junk()
    browser_total_mb, browser_details = BrowserCleaner.scan_browser_cache()
    suspicious_procs = VirusScanner.scan_processes()
    return jsonify({
        "stats": stats,
        "junk_mb": junk_mb,
        "junk_count": len(junk_files),
        "browser_total_mb": browser_total_mb,
        "browser_details": browser_details,
        "suspicious_count": len(suspicious_procs),
        "suspicious_procs": suspicious_procs
    })

@app.route('/clean', methods=['POST'])
def clean():
    result = JunkCleaner().clean_junk()
    return jsonify({
        "status": "success", 
        "deleted": result["deleted"],
        "freed_mb": result["freed_mb"]
    })

@app.route('/clean-browser', methods=['POST'])
def clean_browser():
    result = BrowserCleaner.clean_browser_cache()
    return jsonify({
        "status": "success",
        "deleted": result["deleted"],
        "freed_mb": result["freed_mb"]
    })

@app.route('/empty-recycle-bin', methods=['POST'])
def empty_recycle_bin():
    try:
        subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Savat (Recycle Bin) tozalandi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/flush-dns', methods=['POST'])
def flush_dns():
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "DNS keshi muvaffaqiyatli tozalandi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/scan-duplicates', methods=['POST'])
def scan_dup():
    data = request.get_json() or {}
    target_dir = data.get('target_dir') or os.path.expanduser(r'~\Downloads')
    dups = DuplicateFinder.find_duplicates(target_dir)
    return jsonify({"status": "success", "duplicates": dups})

@app.route('/scan-large-files', methods=['POST'])
def scan_large():
    data = request.get_json() or {}
    target_dir = data.get('target_dir') or os.path.expanduser(r'~\Downloads')
    min_size = int(data.get('min_size_mb', 100))
    files = LargeFilesFinder.find_large_files(target_dir, min_size_mb=min_size)
    return jsonify({"status": "success", "files": files})

@app.route('/delete-files', methods=['POST'])
def delete_files():
    data = request.get_json() or {}
    paths = data.get('paths', [])
    deleted = 0
    for p in paths:
        try:
            if os.path.exists(p) and os.path.isfile(p):
                os.remove(p)
                deleted += 1
        except Exception:
            continue
    return jsonify({"status": "success", "deleted": deleted})

@app.route('/startup/remove', methods=['POST'])
def remove_startup():
    data = request.get_json() or {}
    name = data.get('name')
    loc = data.get('location')
    if not name or not loc:
        return jsonify({"status": "error", "message": "Ma'lumot to'liq emas"}), 400
    success = StartupManager.remove_startup_app(name, loc)
    if success:
        return jsonify({"status": "success", "message": f"{name} avto-yuklanishdan o'chirildi"})
    return jsonify({"status": "error", "message": "O'chirib bo'lmadi (Ruxsat yo'q bo'lishi mumkin)"}), 400

@app.route('/kill-process', methods=['POST'])
def kill_process():
    data = request.get_json() or {}
    pid = data.get('pid')
    if not pid:
        return jsonify({"status": "error", "message": "PID ko'rsatilmadi"}), 400
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({"status": "success", "message": f"PID {pid} jarayoni to'xtatildi"})
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    print("Veb-server ishga tushmoqda: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
