import os
import shutil
import hashlib
import subprocess
import platform
import socket
import psutil
from flask import Flask, render_template, request, jsonify

# Windows-specific winreg xavfsiz import
try:
    import winreg
except ImportError:
    winreg = None

app = Flask(__name__, template_folder='templates', static_folder='static')

CURRENT_OS = platform.system() # 'Windows', 'Linux', 'Darwin' (macOS)

def get_local_ip():
    """Lokal Wi-Fi/LAN tarmog'idagi IP manzilni aniqlash"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# --- 1. KROSS-PLATFORMA TIZIM DIAGNOSTIKASI ---
class SystemDiagnoser:
    @staticmethod
    def get_system_stats():
        cpu_usage = psutil.cpu_percent(interval=0.3)
        cpu_freq = psutil.cpu_freq()
        ram = psutil.virtual_memory()
        
        disks_info = []
        for partition in psutil.disk_partitions(all=False):
            try:
                # Maxsus yoki virtual fayl tizimlarini chetlab o'tish
                if CURRENT_OS == 'Windows' and ('cdrom' in partition.opts or partition.fstype == ''):
                    continue
                if CURRENT_OS in ['Linux', 'Darwin'] and partition.mountpoint.startswith(('/snap', '/boot', '/dev', '/proc', '/sys')):
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
            "os": CURRENT_OS,
            "os_release": platform.release(),
            "cpu": cpu_usage,
            "cpu_freq_ghz": round(cpu_freq.current / 1000, 2) if cpu_freq else 0,
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "disks": disks_info,
            "local_ip": get_local_ip()
        }


# --- 2. KROSS-PLATFORMA KERAKSIZ FAYLLARNI TOZALASH ---
class JunkCleaner:
    def __init__(self):
        self.target_paths = []
        if CURRENT_OS == 'Windows':
            self.target_paths = [
                os.path.expandvars(r'%TEMP%'),
                r'C:\Windows\Temp',
                os.path.expandvars(r'%LOCALAPPDATA%\Temp')
            ]
        elif CURRENT_OS == 'Darwin': # macOS
            self.target_paths = [
                os.path.expanduser('~/Library/Caches/TemporaryItems'),
                '/tmp',
                '/var/tmp'
            ]
        else: # Linux
            self.target_paths = [
                '/tmp',
                '/var/tmp',
                os.path.expanduser('~/.cache/thumbnails')
            ]
        self.target_paths = list(set([p for p in self.target_paths if p and os.path.exists(p)]))

    def scan_junk(self):
        total_bytes = 0
        file_list = []
        for folder in self.target_paths:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        f_path = os.path.join(root, file)
                        try:
                            if os.path.islink(f_path):
                                continue
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


# --- 3. KROSS-PLATFORMA BRAUZER KESHLARI ---
class BrowserCleaner:
    @staticmethod
    def get_cache_paths():
        candidates = {}
        if CURRENT_OS == 'Windows':
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
        elif CURRENT_OS == 'Darwin': # macOS
            home = os.path.expanduser('~')
            candidates = {
                "Google Chrome": [os.path.join(home, 'Library/Caches/Google/Chrome/Default/Cache')],
                "Microsoft Edge": [os.path.join(home, 'Library/Caches/Microsoft Edge/Default/Cache')],
                "Brave Browser": [os.path.join(home, 'Library/Caches/BraveSoftware/Brave-Browser/Default/Cache')],
                "Safari": [os.path.join(home, 'Library/Caches/com.apple.Safari')]
            }
        else: # Linux
            home = os.path.expanduser('~')
            candidates = {
                "Google Chrome": [os.path.join(home, '.cache/google-chrome/Default/Cache')],
                "Microsoft Edge": [os.path.join(home, '.cache/microsoft-edge/Default/Cache')],
                "Brave Browser": [os.path.join(home, '.cache/BraveSoftware/Brave-Browser/Default/Cache')],
                "Mozilla Firefox": [os.path.join(home, '.cache/mozilla/firefox')]
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


# --- 4. KROSS-PLATFORMA AVTO-YUKLANISH (STARTUP MANAGER) ---
class StartupManager:
    @staticmethod
    def get_startup_apps():
        apps = []
        if CURRENT_OS == 'Windows' and winreg:
            locations = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
            ]
            for hkey, subkey, loc_name in locations:
                try:
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                        num_values = winreg.QueryInfoKey(key)[1]
                        for i in range(num_values):
                            name, val, _ = winreg.EnumValue(key, i)
                            apps.append({"name": name, "path": val, "location": loc_name})
                except Exception:
                    continue
        elif CURRENT_OS == 'Linux':
            autostart_dir = os.path.expanduser('~/.config/autostart')
            if os.path.exists(autostart_dir):
                for f in os.listdir(autostart_dir):
                    if f.endswith('.desktop'):
                        apps.append({
                            "name": f.replace('.desktop', ''),
                            "path": os.path.join(autostart_dir, f),
                            "location": "~/.config/autostart"
                        })
        elif CURRENT_OS == 'Darwin': # macOS
            agents_dir = os.path.expanduser('~/Library/LaunchAgents')
            if os.path.exists(agents_dir):
                for f in os.listdir(agents_dir):
                    if f.endswith('.plist'):
                        apps.append({
                            "name": f.replace('.plist', ''),
                            "path": os.path.join(agents_dir, f),
                            "location": "~/Library/LaunchAgents"
                        })
        return apps

    @staticmethod
    def remove_startup_app(name, location):
        if CURRENT_OS == 'Windows' and winreg:
            hkey = winreg.HKEY_CURRENT_USER if location == "HKCU" else winreg.HKEY_LOCAL_MACHINE
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                    return True
            except Exception:
                return False
        elif CURRENT_OS in ['Linux', 'Darwin']:
            # Linux va Mac da tegishli faylni o'chirish
            path = location if os.path.isabs(location) else os.path.expanduser(location)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    return True
                except Exception:
                    return False
        return False


# --- 5. KATTA FAYLLAR VA DUBLIKATLAR ---
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


# --- 6. SHUBHALI JARAYONLAR (VIRUS SCANNER) ---
class VirusScanner:
    @staticmethod
    def scan_processes():
        suspicious = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                exe = proc.info['exe']
                if not exe:
                    continue
                is_suspicious = False
                exe_lower = exe.lower()
                
                if CURRENT_OS == 'Windows' and "temp" in exe_lower:
                    is_suspicious = True
                elif CURRENT_OS in ['Linux', 'Darwin'] and (exe_lower.startswith('/tmp') or exe_lower.startswith('/var/tmp')):
                    is_suspicious = True

                if is_suspicious:
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
        if CURRENT_OS == 'Windows':
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], capture_output=True, text=True)
        elif CURRENT_OS == 'Darwin':
            subprocess.run(["rm", "-rf", os.path.expanduser("~/.Trash/*")], shell=True)
        else: # Linux
            trash_path = os.path.expanduser("~/.local/share/Trash/files")
            if os.path.exists(trash_path):
                shutil.rmtree(trash_path, ignore_errors=True)
                os.makedirs(trash_path, exist_ok=True)
        return jsonify({"status": "success", "message": "Savat (Trash/Recycle Bin) tozalandi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/flush-dns', methods=['POST'])
def flush_dns():
    try:
        if CURRENT_OS == 'Windows':
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
        elif CURRENT_OS == 'Darwin':
            subprocess.run(["dscacheutil", "-flushcache"], capture_output=True, text=True)
        else: # Linux
            subprocess.run(["resolvectl", "flush-caches"], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "DNS keshi tozalandi!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/scan-duplicates', methods=['POST'])
def scan_dup():
    data = request.get_json() or {}
    target_dir = data.get('target_dir') or os.path.expanduser(r'~/Downloads')
    dups = DuplicateFinder.find_duplicates(target_dir)
    return jsonify({"status": "success", "duplicates": dups})

@app.route('/scan-large-files', methods=['POST'])
def scan_large():
    data = request.get_json() or {}
    target_dir = data.get('target_dir') or os.path.expanduser(r'~/Downloads')
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
    return jsonify({"status": "error", "message": "O'chirib bo'lmadi"}), 400

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
    
    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "=" * 65)
    print("🚀 PC Optimizer Pro (Cross-Platform) Muvaffaqiyatli Ishga Tushdi!")
    print(f"🖥️  Operatsion tizim: {CURRENT_OS} ({platform.release()})")
    print("-" * 65)
    print(f"🌐 Ushbu kompyuterda:   http://127.0.0.1:{port}")
    print(f"📱 Telefon/Boshqa Wi-Fi: http://{local_ip}:{port}")
    print("=" * 65 + "\n")
    
    # 0.0.0.0 barcha tarmoq interfeyslaridan (telefon, boshqa PC) kirish imkonini beradi
    app.run(host='0.0.0.0', port=port, debug=False)
