import sys
from pathlib import Path


# ============ CONFIG HELPER ============
def _find_config():
    """Cari config.json di berbagai lokasi."""
    from pathlib import Path
    paths = [
        Path(__file__).parent / "config.json",
        Path(__file__).parent.parent / "config.json",
        Path(__file__).parent.parent / "config" / "config.json",
        Path(__file__).parent.parent / "data" / "config.json",
    ]
    for p in paths:
        if p.exists():
            return str(p)
    return "config.json"


def _load_config():
    """Load config.json."""
    import json
    from pathlib import Path
    paths = [
        Path(__file__).parent / "config.json",
        Path(__file__).parent.parent / "config.json",
        Path(__file__).parent.parent / "config" / "config.json",
        Path(__file__).parent.parent / "data" / "config.json",
    ]
    for p in paths:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}
# ============ END HELPER ============


_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""core.py - Semua fungsi inti ORION"""
import os
import re
import sys
import json
import time
import sqlite3
import logging
import platform
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

# ============ CONFIG ============
BASE = Path(__file__).parent
CFG = CFG = _load_config()
P = CFG["path"]

# ============ INTEGRASI SOUL + MEMORI ============
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).parent))

try:
    import memory_orion as MEM
    import notif_orion as NOTIF
    import web_orion as WEB
    _MODUL_OK = True
except Exception as _e:
    MEM = NOTIF = WEB = None
    _MODUL_OK = False
    _err_modul = str(_e)

_soul_file = _Path(__file__).parent / "SOUL.md"
_akses_file = _Path(__file__).parent / "AKSES.md"
SOUL = _soul_file.read_text(encoding="utf-8") if _soul_file.exists() else ""
AKSES = _akses_file.read_text(encoding="utf-8") if _akses_file.exists() else ""

# Load file konteks Riki
def _load_md(nama):
    p = _Path(__file__).parent / nama
    return p.read_text(encoding="utf-8") if p.exists() else ""

USER_MD = _load_md("USER.md")
VALUES_MD = _load_md("VALUES.md")
GOALS_MD = _load_md("GOALS.md")
PROJECTS_MD = _load_md("PROJECTS.md")
ROUTINE_MD = _load_md("ROUTINE.md")
# ==================================================

# ============ LOGGING ============
logging.basicConfig(
    filename=P["log"],
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)
log = logging.getLogger("ORION")


# ============ DATABASE ============
def init_db():
    con = sqlite3.connect(P["db"])
    con.execute("""CREATE TABLE IF NOT EXISTS todo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tugas TEXT, selesai INTEGER DEFAULT 0,
        dibuat TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS log_aksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aksi TEXT, waktu TEXT)""")
    con.commit()
    con.close()

def db_exec(query, params=()):
    con = sqlite3.connect(P["db"])
    cur = con.execute(query, params)
    con.commit()
    hasil = cur.fetchall()
    con.close()
    return hasil

def catat(aksi):
    db_exec("INSERT INTO log_aksi (aksi, waktu) VALUES (?, ?)",
            (aksi, datetime.now().isoformat()))
    log.info(aksi)


# ============ 1. STATUS SISTEM ============
def status_sistem():
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    bat = psutil.sensors_battery()
    print("\n" + "="*45)
    print(f"  📊 STATUS - {datetime.now().strftime('%H:%M:%S')}")
    print("="*45)
    print(f"  OS    : {platform.system()} {platform.release()}")
    print(f"  CPU   : {cpu}%")
    print(f"  RAM   : {mem.percent}% ({mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB)")
    print(f"  Disk  : {disk.percent}% ({disk.free/(1024**3):.1f} GB bebas)")
    if bat:
        s = "🔌" if bat.power_plugged else "🔋"
        print(f"  Baterai: {bat.percent}% {s}")
    print("="*45 + "\n")
    catat("Cek status")


# ============ 2. SCREENSHOT ============
def screenshot():
    import pyautogui
    Path(P["output"]).mkdir(exist_ok=True)
    nama = f"shot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file = Path(P["output"]) / nama
    pyautogui.screenshot(str(file))
    print(f"  ✅ Screenshot: {file}")
    catat(f"Screenshot: {nama}")


# ============ 3. VOLUME ============
def volume_api(level=50):
    """Set volume - tanpa input()."""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(interface, POINTER(IAudioEndpointVolume))

        # Set volume (0.0 - 1.0)
        level_float = max(0.0, min(1.0, int(level) / 100))
        vol.SetMasterVolumeLevelScalar(level_float, None)
        return f"Volume: {level}%"
    except Exception as e:
        return f"Error: {e}"


def brightness_api(level=80):
    """Set brightness - tanpa input()."""
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(int(level))
        return f"Brightness: {level}%"
    except Exception as e:
        return f"Error: {e}"


def kill_api(nama):
    """Kill proses - tanpa input()."""
    try:
        import psutil
        killed = []
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if nama.lower() in p.info['name'].lower():
                    p.kill()
                    killed.append(p.info['name'])
            except Exception:
                pass
        if killed:
            return f"Killed: {', '.join(killed)}"
        return f"Proses '{nama}' tidak ditemukan"
    except Exception as e:
        return f"Error: {e}"


def volume():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL

        # API baru pycaw: pakai AudioDevice
        device = AudioUtilities.GetSpeakers()
        interface = device._dev.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        vol = cast(interface, POINTER(IAudioEndpointVolume))

        cur = round(vol.GetMasterVolumeLevelScalar() * 100)
        print(f"  🔊 Volume: {cur}%")
        a = input("  (u)p/(d)own/(m)ute/(n)ilai: ").strip().lower()
        if a == "u":
            n = min(100, cur + 10)
            vol.SetMasterVolumeLevelScalar(n/100, None)
            print(f"  → {n}%")
        elif a == "d":
            n = max(0, cur - 10)
            vol.SetMasterVolumeLevelScalar(n/100, None)
            print(f"  → {n}%")
        elif a == "m":
            vol.SetMute(1, None)
            print("  🔇 Muted")
        elif a == "n":
            n = int(input("  Nilai 0-100: "))
            vol.SetMasterVolumeLevelScalar(max(0,min(100,n))/100, None)
            print(f"  → {n}%")
        catat(f"Volume: {a}")
    except Exception as e:
        print(f"  ❌ Error volume: {e}")
        print("  💡 Coba: pip install --upgrade pycaw comtypes")


# ============ 4. BRIGHTNESS ============
def brightness():
    try:
        import screen_brightness_control as sbc
        cur = sbc.get_brightness()[0]
        print(f"  ☀️ Brightness: {cur}%")
        a = input("  (u)p/(d)own/(n)ilai: ").strip().lower()
        if a == "u": sbc.set_brightness(min(100, cur + 10))
        elif a == "d": sbc.set_brightness(max(0, cur - 10))
        elif a == "n": sbc.set_brightness(int(input("  Nilai 0-100: ")))
        print("  ✅ OK")
        catat(f"Brightness: {a}")
    except Exception as e:
        print(f"  ❌ {e}")


# ============ 5. POWER ============
def power():
    print("""
  [1] 🔒 Lock      [3] 🔄 Restart
  [2] 😴 Sleep     [4] ⛔ Shutdown
  [5] ↩️  Cancel
    """)
    p = input("  Pilih: ").strip()
    if p == "1":
        os.system("rundll32.exe user32.dll,LockWorkStation")
        print("  🔒 Locked")
    elif p == "2":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif p == "3":
        if input("  Yakin restart? (y/n): ").lower() == "y":
            os.system("shutdown /r /t 5")
    elif p == "4":
        if input("  Yakin shutdown? (y/n): ").lower() == "y":
            os.system("shutdown /s /t 5")
    catat(f"Power: {p}")


# ============ 6. BROWSER ============
def browser():
    print("  [1] Google  [2] YouTube  [3] URL  [4] Wikipedia")
    p = input("  Pilih: ").strip()
    if p == "1":
        q = input("  Query: ")
        webbrowser.open(f"https://www.google.com/search?q={q}")
    elif p == "2":
        q = input("  Query: ")
        webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
    elif p == "3":
        webbrowser.open(input("  URL: "))
    elif p == "4":
        q = input("  Cari di Wikipedia: ")
        webbrowser.open(f"https://id.wikipedia.org/wiki/{q}")
    print("  ✅ Browser dibuka")
    catat(f"Browser: {p}")


# ============ 7. BUKA APLIKASI ============
def buka_app():
    print("""
  [1] Notepad    [4] CMD
  [2] Calculator [5] Task Manager
  [3] Explorer   [6] Custom
    """)
    p = input("  Pilih: ").strip()
    apps = {
        "1": "notepad",
        "2": "calc",
        "3": "explorer",
        "4": "cmd",
        "5": "taskmgr",
        "6": input("  Nama/path app: ")
    }
    app = apps.get(p)
    if app:
        subprocess.Popen(app, shell=True)
        print(f"  ✅ Membuka: {app}")
        catat(f"Buka app: {app}")


# ============ 8. KILL PROSES ============
def kill_proses():
    import psutil
    print("\n  Top 5 proses CPU:")
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            procs.append(p.info)
        except: pass
    procs.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
    for i, p in enumerate(procs[:5], 1):
        print(f"  {i}. {p['name']} (PID {p['pid']}) - CPU {p['cpu_percent']}%")
    nama = input("\n  Nama proses yg dimatikan: ").strip()
    if nama:
        for p in psutil.process_iter(['name']):
            if p.info['name'] and nama.lower() in p.info['name'].lower():
                try:
                    p.kill()
                    print(f"  ✅ Killed: {p.info['name']}")
                    catat(f"Kill: {p.info['name']}")
                except Exception as e:
                    print(f"  ❌ {e}")




# ============ DATA HABIT REALISTIS (24 JAM) ============
DATA_HABIT = [
    # 00:00 - 05:30 (tidur)
    (0.0, "tidur"),  (0.5, "tidur"),  (1.0, "tidur"),  (1.5, "tidur"),
    (2.0, "tidur"),  (2.5, "tidur"),  (3.0, "tidur"),  (3.5, "tidur"),
    (4.0, "tidur"),  (4.5, "tidur"),  (5.0, "tidur"),  (5.5, "tidur"),
    # 06:00 - 06:30 (makan pagi)
    (6.0, "makan"),  (6.5, "makan"),
    # 07:00 - 11:30 (kerja pagi)
    (7.0, "kerja"),  (7.5, "kerja"),
    (8.0, "kerja"),  (8.5, "kerja"),
    (9.0, "kerja"),  (9.5, "kerja"),
    (10.0, "kerja"), (10.5, "kerja"),
    (11.0, "kerja"), (11.5, "kerja"),
    # 12:00 - 12:30 (makan siang)
    (12.0, "makan"), (12.5, "makan"),
    # 13:00 - 17:30 (kerja sore)
    (13.0, "kerja"), (13.5, "kerja"),
    (14.0, "kerja"), (14.5, "kerja"),
    (15.0, "kerja"), (15.5, "kerja"),
    (16.0, "kerja"), (16.5, "kerja"),
    (17.0, "kerja"), (17.5, "kerja"),
    # 18:00 - 21:30 (santai)
    (18.0, "santai"), (18.5, "santai"),
    (19.0, "santai"), (19.5, "santai"),
    (20.0, "santai"), (20.5, "santai"),
    (21.0, "santai"), (21.5, "santai"),
    # 22:00 - 23:30 (tidur)
    (22.0, "tidur"), (22.5, "tidur"),
    (23.0, "tidur"), (23.5, "tidur"),
]

# ============ 9. OTAK (PyTorch) ============
class Otak:
    """Otak ORION v2 - 48 titik, multi-fitur, Top-N, per-hari, auto-retrain."""

    def __init__(self):
        import torch
        import math
        torch.set_num_threads(CFG["model"].get("threads", 2))
        self.torch = torch
        self.math = math
        self.cfg = CFG["model"]
        self.aktivitas = self.cfg["aktivitas"]
        self.model = None
        self.path = Path(P["model"])
        self._init_db_pengalaman()

    def _init_db_pengalaman(self):
        """Bikin tabel pengalaman kalau belum ada."""
        try:
            con = sqlite3.connect(P["db"])
            con.execute("""CREATE TABLE IF NOT EXISTS pengalaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jam REAL,
                aktivitas TEXT,
                hari TEXT,
                tanggal TEXT,
                sumber TEXT DEFAULT 'user'
            )""")
            con.commit()
            con.close()
        except Exception as e:
            log.warning(f"Init db pengalaman gagal: {e}")

    def _fitur(self, jam):
        rad = 2 * self.math.pi * jam / 24
        return [self.math.sin(rad), self.math.cos(rad)]

    def _buat(self):
        nn = self.torch.nn
        layers = []
        prev = 2
        for h in [32, 16, 8]:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(0.1)]
            prev = h
        layers += [nn.Linear(prev, self.cfg["output"])]
        return nn.Sequential(*layers)

    def _data_gabung(self):
        """Gabungin DATA_HABIT + pengalaman user."""
        data = list(DATA_HABIT)
        try:
            con = sqlite3.connect(P["db"])
            rows = con.execute("SELECT jam, aktivitas FROM pengalaman").fetchall()
            con.close()
            for jam, akt in rows:
                if akt in self.aktivitas:
                    data.append((jam, akt))
                    data.append((jam, akt))  # reinforce 2x
        except Exception as e:
            log.warning(f"Ambil pengalaman gagal: {e}")
        return data

    def latih(self, verbose=True):
        t = self.torch
        if verbose:
            print("[Otak] Training v2...")

        data = self._data_gabung()

        X = t.tensor([self._fitur(d[0]) for d in data], dtype=t.float32)
        y = t.tensor([self.aktivitas.index(d[1]) for d in data], dtype=t.long)

        self.model = self._buat()

        from collections import Counter
        counter = Counter([d[1] for d in data])
        total = len(data)
        weights = [total / (len(self.aktivitas) * counter[a]) for a in self.aktivitas]
        class_weights = t.tensor(weights, dtype=t.float32)

        opt = t.optim.Adam(self.model.parameters(), lr=0.01, weight_decay=1e-4)
        loss_fn = t.nn.CrossEntropyLoss(weight=class_weights)

        epoch = 2000
        for ep in range(epoch):
            opt.zero_grad()
            out = self.model(X)
            loss = loss_fn(out, y)
            loss.backward()
            opt.step()
            if verbose and ep % 400 == 0:
                print(f"  epoch {ep:4d} | loss={loss.item():.4f}")

        t.save(self.model.state_dict(), self.path)
        if verbose:
            print(f"[Otak] OK - Disimpan: {self.path}")
            print(f"[Otak] Data: {len(DATA_HABIT)} habit + {len(data)-len(DATA_HABIT)} pengalaman")
        catat("Training otak v2")

    def load(self):
        t = self.torch
        if self.path.exists():
            self.model = self._buat()
            self.model.load_state_dict(t.load(self.path))
            self.model.eval()
            return True
        return False

    def prediksi(self, jam):
        """Prediksi aktivitas + confidence."""
        t = self.torch
        if self.model is None and not self.load():
            return None, 0
        with t.no_grad():
            fitur = t.tensor([self._fitur(jam)], dtype=t.float32)
            logits = self.model(fitur)
            probs = t.nn.functional.softmax(logits, dim=1)
            conf, idx = t.max(probs, dim=1)
            return self.aktivitas[idx.item()], conf.item()

    def prediksi_top_n(self, jam, n=3):
        """Top-N prediksi (default 3)."""
        t = self.torch
        if self.model is None and not self.load():
            return []
        with t.no_grad():
            fitur = t.tensor([self._fitur(jam)], dtype=t.float32)
            logits = self.model(fitur)
            probs = t.nn.functional.softmax(logits, dim=1)[0]
            top_probs, top_idx = t.topk(probs, min(n, len(self.aktivitas)))
            hasil = []
            for i in range(len(top_idx)):
                hasil.append((self.aktivitas[top_idx[i].item()], top_probs[i].item()))
            return hasil

    def prediksi_per_hari(self, jam, hari):
        """Prediksi dengan konteks hari (Senin-Minggu).
        Hari cuma dipakai buat pattern matching sederhana.
        Kalau ada pengalaman di hari itu, priority ke pengalaman."""
        # Cek pengalaman di hari itu
        try:
            con = sqlite3.connect(P["db"])
            rows = con.execute(
                "SELECT aktivitas, COUNT(*) FROM pengalaman WHERE hari = ? AND CAST(jam AS INT) = ? GROUP BY aktivitas ORDER BY COUNT(*) DESC LIMIT 1",
                (hari, int(jam))
            ).fetchall()
            con.close()
            if rows:
                akt, count = rows[0]
                if count >= 2:  # minimal 2x baru dianggap pattern
                    return akt, min(0.95, 0.7 + count * 0.05)
        except Exception as e:
            log.warning(f"Prediksi per hari gagal: {e}")

        # Fallback: prediksi biasa
        return self.prediksi(jam)

    def simpan_pengalaman(self, jam, aktivitas, hari=None, sumber="user"):
        """Simpan pengalaman user ke database."""
        if aktivitas not in self.aktivitas:
            return False, f"Aktivitas '{aktivitas}' tidak dikenal"
        try:
            con = sqlite3.connect(P["db"])
            con.execute(
                "INSERT INTO pengalaman (jam, aktivitas, hari, tanggal, sumber) VALUES (?, ?, ?, ?, ?)",
                (jam, aktivitas, hari, datetime.now().isoformat(), sumber)
            )
            con.commit()
            con.close()
            catat(f"Pengalaman: jam {jam} = {aktivitas}")
            return True, "Tersimpan"
        except Exception as e:
            return False, str(e)

    def hitung_pengalaman(self):
        """Hitung jumlah pengalaman user."""
        try:
            con = sqlite3.connect(P["db"])
            n = con.execute("SELECT COUNT(*) FROM pengalaman").fetchone()[0]
            con.close()
            return n
        except:
            return 0

    def retrain_dari_pengalaman(self, verbose=True):
        """Retrain otak dari DATA_HABIT + pengalaman user."""
        n = self.hitung_pengalaman()
        if n == 0:
            if verbose:
                print("[Otak] Belum ada pengalaman user.")
            return False
        if verbose:
            print(f"[Otak] Retrain dari {n} pengalaman user...")
        self.latih(verbose=verbose)
        return True

def animasi_loading(durasi=2.0, teks="Memuat ORION"):
    import sys, time
    spinner = ["|", "/", "-", "\\"]
    end = time.time() + durasi
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  \033[96m{spinner[i % len(spinner)]}\033[0m {teks}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f"\r  \033[92mOK\033[0m {teks}... selesai!     \n")
    sys.stdout.flush()


def animasi_bar(durasi=1.5):
    import sys, time
    lebar = 30
    end = time.time() + durasi
    while time.time() < end:
        for i in range(lebar + 1):
            if time.time() >= end:
                break
            filled = "=" * i
            empty = " " * (lebar - i)
            sys.stdout.write(f"\r  \033[96m[{filled}{empty}]\033[0m {int(i/lebar*100)}%")
            sys.stdout.flush()
            time.sleep(durasi / (lebar * 2))
    sys.stdout.write(f"\r  \033[92m[{'='*lebar}]\033[0m 100%     \n")
    sys.stdout.flush()


def sound_startup():
    from pathlib import Path
    sound = Path(P["output"]) / "tts" / "startup.mp3"
    if not sound.exists():
        return False
    try:
        import pygame, time
        pygame.mixer.init()
        pygame.mixer.music.load(str(sound))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"  Warning: {e}")
        return False

# ============ 24. OCR - BACA TEKS DARI GAMBAR ============
def ocr_gambar():
    """OCR: baca teks dari gambar/screenshot."""
    try:
        import pytesseract
        from PIL import Image
        import pyautogui
        
        # Set path Tesseract (Windows default)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        print("  [1] Screenshot baru")
        print("  [2] File gambar yang ada")
        p = input("  Pilih: ").strip()
        
        if p == "1":
            Path(P["output"]).mkdir(exist_ok=True)
            nama = f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file = Path(P["output"]) / nama
            print("  Mengambil screenshot...")
            pyautogui.screenshot(str(file))
        elif p == "2":
            path = input("  Path gambar: ").strip()
            file = Path(path)
            if not file.exists():
                print("  File tidak ada")
                return
        else:
            return
        
        print("  Membaca teks...")
        img = Image.open(file)
        teks = pytesseract.image_to_string(img, lang="ind+eng")
        
        if not teks.strip():
            print("  Tidak ada teks terdeteksi")
            return
        
        print()
        print("=" * 60)
        print("  HASIL OCR:")
        print("=" * 60)
        print(teks)
        print("=" * 60)
        
        # Simpan ke file
        txt_file = Path(P["output"]) / f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        txt_file.write_text(teks, encoding="utf-8")
        print(f"  Tersimpan: {txt_file}")
        catat("OCR")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Pastikan Tesseract OCR terinstall: https://github.com/UB-Mannheim/tesseract/wiki")



def ocr_file(path_file, lang="ind+eng", simpan=True):
    """OCR dari file gambar - non-interaktif."""
    try:
        import pytesseract
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        file = Path(path_file)
        if not file.exists():
            return {"sukses": False, "error": f"File tidak ada: {path_file}"}

        img = Image.open(file)
        teks = pytesseract.image_to_string(img, lang=lang)

        if not teks.strip():
            return {"sukses": False, "error": "Tidak ada teks terdeteksi", "teks": ""}

        file_txt = None
        if simpan:
            Path(P["output"]).mkdir(exist_ok=True)
            file_txt = Path(P["output"]) / f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_txt.write_text(teks, encoding="utf-8")
            catat("OCR")

        return {
            "sukses": True,
            "teks": teks,
            "file_txt": str(file_txt) if file_txt else None,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


# ============ 25. CHAT MEMORY ============
def chat_simpan(user, orion):
    """Simpan chat ke database."""
    db_exec(
        "INSERT INTO chat (user_pesan, orion_pesan, waktu) VALUES (?, ?, ?)",
        (user, orion, datetime.now().isoformat())
    )


def chat_lihat():
    """Lihat history chat."""
    rows = db_exec("SELECT user_pesan, orion_pesan, waktu FROM chat ORDER BY id DESC LIMIT 20")
    if not rows:
        print("  (belum ada history)")
        return
    print()
    print("=" * 60)
    print("  HISTORY CHAT (20 terakhir)")
    print("=" * 60)
    for u, o, w in reversed(rows):
        print(f"\n  [{w[:19]}]")
        print(f"  Riki  : {u}")
        print(f"  ORION : {o}")
    print()
    print("=" * 60)


def chat_hapus():
    """Hapus semua history."""
    y = input("  Yakin hapus semua? (y/n): ").strip().lower()
    if y == "y":
        db_exec("DELETE FROM chat")
        print("  History dihapus")


def chat_echo():
    """Mode chat sederhana (echo + simpan)."""
    print("  Mode chat (ketik 'exit' untuk keluar)")
    while True:
        u = input("  Riki  > ").strip()
        if u.lower() in ("exit", "quit", "keluar"):
            break
        if not u:
            continue
        # Echo sederhana (nanti bisa diganti LLM)
        if "halo" in u.lower() or "hai" in u.lower():
            o = "Halo Riki! Ada yang bisa saya bantu?"
        elif "jam" in u.lower():
            o = f"Sekarang jam {datetime.now().strftime('%H:%M')}"
        elif "tanggal" in u.lower():
            o = f"Hari ini {datetime.now().strftime('%A, %d %B %Y')}"
        elif "nama" in u.lower():
            o = "Nama saya ORION, asisten pribadi Anda"
        elif "terima kasih" in u.lower():
            o = "Sama-sama Riki!"
        else:
            o = "Baik Riki, saya catat ya."
        print(f"  ORION > {o}")
        chat_simpan(u, o)


# ============ 26. YOUTUBE DOWNLOADER ============
def yt_download():
    """Download YouTube video/audio."""
    try:
        import yt_dlp
    except ImportError:
        print("  Install dulu: pip install yt-dlp")
        return
    
    url = input("  URL YouTube: ").strip()
    if not url:
        return
    
    print("  [1] Video MP4 (720p)")
    print("  [2] Video MP4 (1080p)")
    print("  [3] Audio MP3 saja")
    p = input("  Pilih [1-3]: ").strip()
    
    out_dir = Path(P["output"]) / "youtube"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if p == "1":
        fmt = "best[height<=720]"
        ext = "mp4"
    elif p == "2":
        fmt = "best[height<=1080]"
        ext = "mp4"
    elif p == "3":
        fmt = "bestaudio/best"
        ext = "mp3"
    else:
        return
    
    opts = {
        "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
        "format": fmt,
    }
    
    if ext == "mp3":
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }]
    
    print("  Mendownload...")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"  Selesai: {info.get('title', '?')}")
        catat(f"YouTube DL: {url[:50]}")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 27. AUTO-NOTIFICATION ============
def auto_notif_mulai():
    """Aktifkan reminder otomatis tiap jam."""
    import threading
    import time as t

    reminders = {
        7:  "Selamat pagi Riki! Waktunya sarapan.",
        9:  "Sudah 1 jam kerja, minum air dulu.",
        11: "Istirahat sebentar, posture check!",
        12: "Waktunya makan siang.",
        14: "Minum air lagi, jangan lupa!",
        16: "Istirahatkan mata 20 detik.",
        18: "Kerja selesai, waktu santai!",
        20: "Minum air, jangan lupa istirahat.",
        22: "Siap-siap tidur, besok pagi.",
    }

    def loop():
        last_jam = -1
        while True:
            now = datetime.now()
            if now.hour != last_jam and now.hour in reminders:
                pesan = reminders[now.hour]
                notif("ORION Reminder", pesan)
                try:
                    tts_bicara(pesan)
                except:
                    pass
                last_jam = now.hour
            t.sleep(60)

    th = threading.Thread(target=loop, daemon=True)
    th.start()
    print("  Auto-Notification aktif!")
    print(f"  {len(reminders)} reminder terjadwal sepanjang hari")
    catat("Auto-notif aktif")


# ============ 28. CUACA+ (5 HARI) ============
def cuaca_api(kota=None):
    """Prakiraan cuaca - tanpa input()."""
    try:
        import requests
        api = CFG["cuaca"]["api_key"]
        if api == "GANTI_DENGAN_API_KEY_OPENWEATHER":
            return "Fitur cuaca belum aktif. Butuh API key OpenWeather."

        kota = kota or CFG["cuaca"].get("kota", "Jakarta")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={kota}&appid={api}&units=metric&lang=id"
        r = requests.get(url, timeout=10)
        data = r.json()

        if r.status_code != 200:
            return f"Error: {data.get('message', '?')}"

        return f"Cuaca {kota}: {data['main']['temp']}C, {data['weather'][0]['description']}"
    except Exception as e:
        return f"Error: {e}"


def cuaca_plus():
    """Prakiraan cuaca 5 hari."""
    try:
        import requests
        api = CFG["cuaca"]["api_key"]
        if api == "GANTI_DENGAN_API_KEY_OPENWEATHER":
            print("  Set api_key di config.json dulu")
            print("  Daftar gratis: https://openweathermap.org/api")
            return
        
        kota = input(f"  Kota (default {CFG['cuaca']['kota']}): ").strip() or CFG["cuaca"]["kota"]
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={kota}&appid={api}&units=metric&lang=id"
        
        r = requests.get(url, timeout=5).json()
        
        print()
        print("=" * 60)
        print(f"  PRAKIRAAN CUACA - {r['city']['name']}")
        print("=" * 60)
        
        # Group by tanggal
        from collections import defaultdict
        per_hari = defaultdict(list)
        for item in r["list"]:
            tanggal = item["dt_txt"][:10]
            per_hari[tanggal].append(item)
        
        for tanggal, items in list(per_hari.items())[:5]:
            # Ambil suhu min/max
            temps = [i["main"]["temp"] for i in items]
            tmin = min(temps)
            tmax = max(temps)
            # Ambil cuaca paling sering
            cuacas = [i["weather"][0]["description"] for i in items]
            cuaca_utama = max(set(cuacas), key=cuacas.count)
            
            print(f"\n  {tanggal}")
            print(f"    Suhu: {tmin:.1f}C - {tmax:.1f}C")
            print(f"    Cuaca: {cuaca_utama}")
        
        print()
        print("=" * 60)
        catat(f"Cuaca+: {kota}")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 29. GOOGLE CALENDAR ============
def gcal_buka():
    """Buka Google Calendar di browser."""
    import webbrowser
    webbrowser.open("https://calendar.google.com")
    print("  Google Calendar dibuka di browser")
    catat("GCal")


def gcal_hari_ini():
    """Buka kalender hari ini."""
    import webbrowser
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    webbrowser.open(f"https://calendar.google.com/calendar/r/day/{today}")
    print(f"  Kalender {today} dibuka")
    catat("GCal hari ini")


def gcal_buat_event():
    """Buat link untuk buat event baru."""
    import webbrowser
    from urllib.parse import quote
    
    judul = input("  Judul event: ").strip()
    tanggal = input("  Tanggal (YYYYMMDD, contoh 20260924): ").strip()
    jam_mulai = input("  Jam mulai (HHMM, contoh 1400): ").strip()
    jam_selesai = input("  Jam selesai (HHMM): ").strip()
    lokasi = input("  Lokasi (opsional): ").strip()
    deskripsi = input("  Deskripsi (opsional): ").strip()
    
    if not judul or not tanggal:
        print("  Judul & tanggal wajib")
        return
    
    dates = f"{tanggal}T{jam_mulai}00/{tanggal}T{jam_selesai}00"
    url = (
        f"https://calendar.google.com/calendar/render?"
        f"action=TEMPLATE&text={quote(judul)}&dates={dates}"
        f"&location={quote(lokasi)}&details={quote(deskripsi)}"
    )
    webbrowser.open(url)
    print("  Link event dibuka di browser")
    print("  Klik SAVE di Google Calendar untuk simpan")
    catat(f"GCal event: {judul}")


# ============ INIT DATABASE CHAT ============
def init_db_chat():
    """Tambah tabel chat ke database."""
    con = sqlite3.connect(P["db"])
    con.execute("""CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_pesan TEXT,
        orion_pesan TEXT,
        waktu TEXT
    )""")
    con.commit()
    con.close()


# Init chat table saat import
try:
    init_db_chat()
except:
    pass

# ============ 30. WEB SCRAPER ============
def berita_detik():
    """Ambil berita terpopuler dari Detik.com."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = "https://www.detik.com/terpopuler"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        
        berita = []
        seen = set()
        for a in soup.find_all("a", href=True):
            judul = a.get_text(strip=True)
            link = a["href"]
            if judul and len(judul) > 30 and link.startswith("http") and judul not in seen:
                seen.add(judul)
                berita.append((judul, link))
            if len(berita) >= 10:
                break
        
        print()
        print("=" * 70)
        print("  BERITA TERPOPULER - DETIK.COM")
        print("=" * 70)
        for i, (judul, link) in enumerate(berita, 1):
            print(f"\n  {i}. {judul}")
            print(f"     {link}")
        print()
        print("=" * 70)
        catat("Scraper: Detik")
    except Exception as e:
        print(f"  Error: {e}")


def berita_kompas():
    """Ambil berita terbaru dari Kompas.com (bersih)."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = "https://www.kompas.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        # Label yang sering nempel di judul
        label_kotor = [
            "Headline", "News", "Regional", "Nasional", "Megapolitan",
            "Internasional", "Sport", "Bola", "Ekonomi", "Tekno",
            "Otomotif", "Travel", "Lifestyle", "Health", "Edukasi",
            "Terpopuler", "Rekomendasi", "Indeks",
        ]

        berita = []
        seen = set()
        for a in soup.find_all("a", href=True):
            judul = a.get_text(strip=True)
            link = a["href"]

            if (judul and len(judul) > 30 and "/read/" in link
                    and "kompas.com" in link):
                # Bersihkan judul
                bersih = judul
                for lbl in label_kotor:
                    bersih = bersih.replace(lbl, "")
                # Hapus angka di awal (1, 2, 3, ...)
                bersih = re.sub(r"^\d+", "", bersih).strip()
                # Hapus spasi ganda
                bersih = re.sub(r"\s+", " ", bersih).strip()
                # Hapus tanda baca di akhir
                bersih = bersih.rstrip(".,;:")

                if len(bersih) > 25 and bersih not in seen:
                    seen.add(bersih)
                    berita.append((bersih, link))
            if len(berita) >= 10:
                break

        if not berita:
            print("  Tidak ada berita ditemukan")
            return

        print()
        print("=" * 70)
        print("  BERITA TERBARU - KOMPAS.COM")
        print("=" * 70)
        for i, (judul, link) in enumerate(berita, 1):
            print(f"\n  {i}. {judul}")
            print(f"     {link}")
        print()
        print("=" * 70)
        catat("Scraper: Kompas")
    except Exception as e:
        print(f"  Error: {e}")

def berita_cnn():
    """Ambil berita terbaru dari CNN Indonesia."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = "https://www.cnnindonesia.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        
        berita = []
        seen = set()
        for a in soup.find_all("a", href=True):
            judul = a.get_text(strip=True)
            link = a["href"]
            if judul and len(judul) > 30 and "cnnindonesia.com" in link and judul not in seen:
                seen.add(judul)
                berita.append((judul, link))
            if len(berita) >= 10:
                break
        
        print()
        print("=" * 70)
        print("  BERITA TERBARU - CNN INDONESIA")
        print("=" * 70)
        for i, (judul, link) in enumerate(berita, 1):
            print(f"\n  {i}. {judul}")
            print(f"     {link}")
        print()
        print("=" * 70)
        catat("Scraper: CNN")
    except Exception as e:
        print(f"  Error: {e}")


def berita_tempo():
    """Ambil berita terbaru dari Tempo.co."""
    try:
        import requests
        from bs4 import BeautifulSoup
        url = "https://www.tempo.co/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        
        berita = []
        seen = set()
        for a in soup.find_all("a", href=True):
            judul = a.get_text(strip=True)
            link = a["href"]
            if judul and len(judul) > 30 and "tempo.co" in link and judul not in seen:
                seen.add(judul)
                berita.append((judul, link))
            if len(berita) >= 10:
                break
        
        print()
        print("=" * 70)
        print("  BERITA TERBARU - TEMPO.CO")
        print("=" * 70)
        for i, (judul, link) in enumerate(berita, 1):
            print(f"\n  {i}. {judul}")
            print(f"     {link}")
        print()
        print("=" * 70)
        catat("Scraper: Tempo")
    except Exception as e:
        print(f"  Error: {e}")


def cari_berita():
    """Cari berita di Google News."""
    try:
        import webbrowser
        from urllib.parse import quote
        keyword = input("  Keyword: ").strip()
        if not keyword:
            return
        url = f"https://news.google.com/search?q={quote(keyword)}&hl=id"
        webbrowser.open(url)
        print(f"  Google News dibuka untuk: {keyword}")
        catat(f"Scraper cari: {keyword}")
    except Exception as e:
        print(f"  Error: {e}")


def harga_saham():
    """Cek harga saham dari Yahoo Finance."""
    try:
        import requests
        kode = input("  Kode saham (contoh: BBCA.JK, BBRI.JK, TLKM.JK): ").strip().upper()
        if not kode:
            kode = "BBCA.JK"
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10).json()
        
        hasil = r["chart"]["result"][0]
        meta = hasil["meta"]
        harga = meta["regularMarketPrice"]
        prev = meta.get("previousClose", harga)
        perubahan = harga - prev
        persen = (perubahan / prev) * 100 if prev else 0
        arah = "NAIK" if perubahan > 0 else "TURUN" if perubahan < 0 else "STAGNAN"
        
        print()
        print("=" * 60)
        print(f"  SAHAM: {meta.get('symbol', kode)}")
        print("=" * 60)
        print(f"  Harga     : Rp {harga:,.0f}")
        print(f"  Sebelumnya: Rp {prev:,.0f}")
        print(f"  Perubahan : Rp {perubahan:+,.0f} ({persen:+.2f}%)")
        print(f"  Status    : {arah}")
        print("=" * 60)
        catat(f"Scraper saham: {kode}")
    except Exception as e:
        print(f"  Error: {e}")


def kurs_mata_uang():
    """Cek kurs mata uang real-time."""
    try:
        import requests
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=10).json()
        
        rates = r["rates"]
        idr = rates.get("IDR", 0)
        
        print()
        print("=" * 60)
        print("  KURS MATA UANG (via USD)")
        print("=" * 60)
        print(f"  1 USD = Rp {idr:,.0f}")
        
        for mata in ["EUR", "GBP", "JPY", "SGD", "MYR", "CNY"]:
            if mata in rates:
                print(f"  1 {mata} = Rp {(idr / rates[mata]):,.0f}")
        
        print("=" * 60)
        catat("Scraper kurs")
    except Exception as e:
        print(f"  Error: {e}")


def scraper_menu():
    """Menu web scraper."""
    while True:
        print()
        print("=" * 60)
        print("  WEB SCRAPER ORION")
        print("=" * 60)
        print("  [1] Berita Detik")
        print("  [2] Berita Kompas")
        print("  [3] Berita CNN Indonesia")
        print("  [4] Berita Tempo")
        print("  [5] Cari Berita (Google News)")
        print("  [6] Harga Saham (Yahoo Finance)")
        print("  [7] Kurs Mata Uang")
        print("  [0] Kembali")
        print("=" * 60)
        
        p = input("  Pilih: ").strip()
        try:
            if p == "1": berita_detik()
            elif p == "2": berita_kompas()
            elif p == "3": berita_cnn()
            elif p == "4": berita_tempo()
            elif p == "5": cari_berita()
            elif p == "6": harga_saham()
            elif p == "7": kurs_mata_uang()
            elif p == "0": return
            else: print("  Pilihan tidak valid")
        except KeyboardInterrupt:
            print("\n  Dibatalkan")
        except Exception as e:
            print(f"  Error: {e}")
        input("\n  [Enter] lanjut...")

# ============ VOICE COMMAND MANUAL ============
def voice_input(durasi=5):
    """Rekam suara & transkrip pakai Google Speech API."""
    try:
        import sounddevice as sd
        import numpy as np
        import speech_recognition as sr
        import wave
        import tempfile

        SR = 44100
        print(f"  🎤 Rekam {durasi} detik... Bicara sekarang!")

        audio = sd.rec(int(durasi * SR), samplerate=SR, channels=2, dtype="int16")
        sd.wait()
        print("  ✅ Selesai rekam")

        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        audio = audio.flatten().astype(np.int16)

        temp = Path(tempfile.gettempdir()) / "orion_voice.wav"
        with wave.open(str(temp), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(audio.tobytes())

        print("  🔄 Transkrip...")
        r = sr.Recognizer()
        with sr.AudioFile(str(temp)) as source:
            audio_data = r.record(source)

        teks = r.recognize_google(audio_data, language="id-ID")
        print(f"  📝 Anda: {teks}")
        catat(f"Voice: {teks}")

        try:
            temp.unlink()
        except:
            pass

        return teks
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def voice_command():
    """Voice command manual - 50+ command."""
    teks = voice_input()
    if not teks:
        return
    teks = teks.lower()
    print(f"  🔍 Command: {teks}")

    # ============ APLIKASI ============
    if "notepad" in teks:
        subprocess.Popen("notepad", shell=True)
        tts_bicara("Membuka notepad")
    elif "kalkulator" in teks or "calculator" in teks:
        subprocess.Popen("calc", shell=True)
        tts_bicara("Membuka kalkulator")
    elif "cmd" in teks or "command prompt" in teks:
        subprocess.Popen("cmd", shell=True)
        tts_bicara("Membuka command prompt")
    elif "explorer" in teks or "file manager" in teks:
        subprocess.Popen("explorer", shell=True)
        tts_bicara("Membuka file explorer")
    elif "task manager" in teks:
        subprocess.Popen("taskmgr", shell=True)
        tts_bicara("Membuka task manager")

    # ============ BROWSER ============
    elif "youtube" in teks:
        webbrowser.open("https://youtube.com")
        tts_bicara("Membuka YouTube")
    elif "google" in teks or "browser" in teks:
        webbrowser.open("https://google.com")
        tts_bicara("Membuka browser")
    elif "wikipedia" in teks:
        webbrowser.open("https://id.wikipedia.org")
        tts_bicara("Membuka Wikipedia")
    elif "cari" in teks:
        keyword = teks.replace("cari", "").replace("di google", "").strip()
        if keyword:
            webbrowser.open(f"https://www.google.com/search?q={keyword}")
            tts_bicara(f"Mencari {keyword} di Google")

    # ============ SCREENSHOT & MEDIA ============
    elif "screenshot" in teks or "tangkapan layar" in teks:
        screenshot()
        tts_bicara("Screenshot diambil")
    elif "video" in teks or "rekam layar" in teks:
        tts_bicara("Fitur rekam layar belum tersedia")

    # ============ VOLUME ============
    elif "volume naik" in teks or "volume up" in teks or "naikkan volume" in teks:
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            device = AudioUtilities.GetSpeakers()
            iface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = cast(iface, POINTER(IAudioEndpointVolume))
            cur = round(vol.GetMasterVolumeLevelScalar() * 100)
            new = min(100, cur + 10)
            vol.SetMasterVolumeLevelScalar(new/100, None)
            tts_bicara(f"Volume {new} persen")
        except:
            tts_bicara("Gagal mengatur volume")
    elif "volume turun" in teks or "volume down" in teks or "turunkan volume" in teks:
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            device = AudioUtilities.GetSpeakers()
            iface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = cast(iface, POINTER(IAudioEndpointVolume))
            cur = round(vol.GetMasterVolumeLevelScalar() * 100)
            new = max(0, cur - 10)
            vol.SetMasterVolumeLevelScalar(new/100, None)
            tts_bicara(f"Volume {new} persen")
        except:
            tts_bicara("Gagal mengatur volume")
    elif "mute" in teks or "bisu" in teks:
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            device = AudioUtilities.GetSpeakers()
            iface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = cast(iface, POINTER(IAudioEndpointVolume))
            vol.SetMute(1, None)
            tts_bicara("Bisu")
        except:
            pass

    # ============ BRIGHTNESS ============
    elif "brightness naik" in teks or "terangkan layar" in teks:
        try:
            import screen_brightness_control as sbc
            cur = sbc.get_brightness()[0]
            new = min(100, cur + 10)
            sbc.set_brightness(new)
            tts_bicara(f"Brightness {new} persen")
        except:
            pass
    elif "brightness turun" in teks or "redupkan layar" in teks:
        try:
            import screen_brightness_control as sbc
            cur = sbc.get_brightness()[0]
            new = max(0, cur - 10)
            sbc.set_brightness(new)
            tts_bicara(f"Brightness {new} persen")
        except:
            pass

    # ============ POWER ============
    elif "lock" in teks or "kunci" in teks:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        tts_bicara("PC dikunci")
    elif "sleep" in teks or "tidur" in teks:
        tts_bicara("PC akan tidur dalam 3 detik")
        import time
        time.sleep(3)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "shutdown" in teks or "matikan" in teks:
        tts_bicara("PC akan dimatikan dalam 10 detik")
        os.system("shutdown /s /t 10")
    elif "restart" in teks or "ulangi" in teks:
        tts_bicara("PC akan restart dalam 10 detik")
        os.system("shutdown /r /t 10")
    elif "batal" in teks or "cancel" in teks:
        os.system("shutdown /a")
        tts_bicara("Dibatalkan")

    # ============ INFO ============
    elif "jam berapa" in teks or "jam" in teks:
        jam = datetime.now().strftime("%H:%M")
        tts_bicara(f"Sekarang jam {jam}")
    elif "tanggal" in teks or "hari ini" in teks:
        tgl = datetime.now().strftime("%A, %d %B %Y")
        tts_bicara(f"Hari ini {tgl}")
    elif "status" in teks or "sistem" in teks:
        status_sistem()
        tts_bicara("Sudah saya tampilkan status sistem")
    elif "cuaca" in teks:
        cuaca_plus()
        tts_bicara("Cuaca sudah ditampilkan")
    elif "berita" in teks:
        berita_detik()
        tts_bicara("Berita sudah ditampilkan")
    elif "saham" in teks or "harga saham" in teks:
        harga_saham()
        tts_bicara("Harga saham sudah ditampilkan")
    elif "kurs" in teks or "dollar" in teks:
        kurs_mata_uang()
        tts_bicara("Kurs sudah ditampilkan")
    elif "baterai" in teks:
        import psutil
        bat = psutil.sensors_battery()
        if bat:
            tts_bicara(f"Baterai {bat.percent} persen")
        else:
            tts_bicara("Tidak ada baterai")
    elif "cpu" in teks:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        tts_bicara(f"CPU {cpu} persen")
    elif "ram" in teks or "memori" in teks:
        import psutil
        mem = psutil.virtual_memory()
        tts_bicara(f"RAM {mem.percent} persen")

    # ============ AI ============
    elif "latih otak" in teks or "training" in teks:
        tts_bicara("Melatih otak, tunggu sebentar")
        otak = Otak()
        otak.latih(verbose=False)
        tts_bicara("Otak selesai dilatih")
    elif "prediksi" in teks:
        try:
            jam = int("".join(filter(str.isdigit, teks)) or "12")
            otak = Otak()
            akt, conf = otak.prediksi(jam)
            if akt:
                tts_bicara(f"Jam {jam}, prediksi {akt}")
        except:
            tts_bicara("Format prediksi: jam berapa")
    elif "chat" in teks:
        chat_echo()
        tts_bicara("Mode chat dibuka")

    # ============ PRODUKTIVITAS ============
    elif "timer" in teks:
        try:
            menit = int("".join(filter(str.isdigit, teks)) or "1")
            tts_bicara(f"Timer {menit} menit dimulai")
            import time
            time.sleep(menit * 60)
            tts_bicara(f"Timer {menit} menit selesai")
        except:
            tts_bicara("Format timer: timer 5 menit")
    elif "reminder" in teks or "ingatkan" in teks:
        tts_bicara("Gunakan menu reminder untuk set")
    elif "to-do" in teks or "tugas" in teks:
        todo()
        tts_bicara("To-Do dibuka")
    elif "grafik" in teks:
        grafik_habit()
        tts_bicara("Grafik ditampilkan")
    elif "log" in teks:
        lihat_log()
        tts_bicara("Log ditampilkan")

    # ============ SUARA ============
    elif "bicara" in teks or "speak" in teks:
        kalimat = teks.replace("bicara", "").replace("speak", "").strip()
        if kalimat:
            tts_bicara(kalimat)
        else:
            tts_bicara("Apa yang mau saya ucapkan?")
    elif "test suara" in teks or "test tts" in teks:
        tts_test()
    elif "translate" in teks or "terjemah" in teks:
        translate()
        tts_bicara("Translate dibuka")

    # ============ SAPAAN ============
    elif "halo" in teks or "hai" in teks or "hello" in teks:
        tts_bicara("Halo Riki, ada yang bisa saya bantu?")
    elif "terima kasih" in teks or "makasih" in teks:
        tts_bicara("Sama-sama Riki")
    elif "selamat pagi" in teks:
        tts_bicara("Selamat pagi Riki, semoga harimu menyenangkan")
    elif "selamat malam" in teks:
        tts_bicara("Selamat malam Riki, istirahat yang cukup")
    elif "siapa kamu" in teks or "nama kamu" in teks:
        tts_bicara("Saya ORION, asisten pribadi Anda")
    elif "apa kabar" in teks:
        tts_bicara("Saya baik, terima kasih sudah bertanya")

    # ============ LAINNYA ============
    elif "backup" in teks:
        import shutil
        from datetime import datetime
        src = Path(P["base"])
        dst = src / "backup" / f"orion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dst.parent.mkdir(exist_ok=True)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
            "backup", "__pycache__", "*.pyc", "*.bak*"))
        tts_bicara("Backup selesai")
    elif "kill" in teks or "matikan proses" in teks:
        kill_proses()
        tts_bicara("Proses dibuka")
    elif "buka app" in teks or "buka aplikasi" in teks:
        buka_app()
        tts_bicara("Menu buka aplikasi")

    else:
        print("  ⚠️  Command tidak dikenali")
        tts_bicara("Maaf, saya tidak mengerti")

def tts_test():
    """Test TTS ORION."""
    print("  🔊 Test TTS...")
    tts_bicara("Halo Riki, saya ORION, asisten pribadi Anda.")

# ============ TTS ============
def tts_bicara(teks, voice=None):
    """ORION bicara pakai Edge-TTS."""
    try:
        import tts_orion
        return tts_orion.bicara(teks, voice=voice)
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


def tts_test():
    """Test TTS ORION."""
    print("  Test TTS...")
    tts_bicara("Halo Riki, saya ORION, asisten pribadi Anda.")


def sapa_orion(nama="Riki"):
    """Fungsi sapa dari Orion."""
    from datetime import datetime
    jam = datetime.now().hour
    if jam < 12:
        salam = "Selamat pagi"
    elif jam < 18:
        salam = "Selamat siang"
    else:
        salam = "Selamat malam"
    pesan = f"{salam}, {nama}! Saya ORION."
    print(f"  ORION: {pesan}")
    return pesan


# === APPENDED ===
# ============ 31. PROTEKSI FOLDER ============
def proteksi():
    """Cek folder terlarang & aman."""
    print("\n" + "=" * 55)
    print("  PROTEKSI FOLDER - ORION")
    print("=" * 55)
    terlarang = CFG["proteksi"]["folder_terlarang"]
    aman = CFG["proteksi"]["folder_aman"]

    print("\n  [FOLDER TERLARANG]")
    for f in terlarang:
        status = "ADA" if Path(f).exists() else "TIDAK ADA"
        print(f"    - {f} [{status}]")

    print("\n  [FOLDER AMAN]")
    for f in aman:
        status = "ADA" if Path(f).exists() else "TIDAK ADA"
        print(f"    - {f} [{status}]")

    print("\n" + "=" * 55)
    catat("Cek proteksi")


# ============ 32. TO-DO LIST ============
def todo():
    """To-Do list sederhana."""
    while True:
        print("\n" + "=" * 55)
        print("  TO-DO LIST - ORION")
        print("=" * 55)

        rows = db_exec("SELECT id, tugas, selesai FROM todo ORDER BY selesai, id")
        if not rows:
            print("\n  (belum ada tugas)")
        else:
            print()
            for id_t, tugas, selesai in rows:
                mark = "[x]" if selesai else "[ ]"
                print(f"  {mark} #{id_t} {tugas}")

        print("\n  [1] Tambah  [2] Selesai  [3] Hapus  [0] Kembali")
        p = input("  Pilih: ").strip()

        if p == "1":
            tugas = input("  Tugas baru: ").strip()
            if tugas:
                db_exec("INSERT INTO todo (tugas, dibuat) VALUES (?, ?)",
                        (tugas, datetime.now().isoformat()))
                print(f"  Ditambah: {tugas}")
        elif p == "2":
            try:
                id_t = int(input("  ID yang selesai: "))
                db_exec("UPDATE todo SET selesai = 1 WHERE id = ?", (id_t,))
                print(f"  #{id_t} selesai")
            except:
                print("  ID tidak valid")
        elif p == "3":
            try:
                id_t = int(input("  ID yang dihapus: "))
                db_exec("DELETE FROM todo WHERE id = ?", (id_t,))
                print(f"  #{id_t} dihapus")
            except:
                print("  ID tidak valid")
        elif p == "0":
            return


# ============ 33. TIMER ============
def timer():
    """Timer countdown."""
    try:
        menit = float(input("  Timer (menit): ").strip())
    except:
        print("  Input tidak valid")
        return

    total = int(menit * 60)
    print(f"  Timer {menit} menit dimulai...")

    try:
        for sisa in range(total, -1, -1):
            m, s = divmod(sisa, 60)
            print(f"\r  [{m:02d}:{s:02d}] tersisa", end="", flush=True)
            time.sleep(1)
        print("\n  WAKTU HABIS!")
        try:
            tts_bicara(f"Timer {menit} menit selesai")
        except:
            pass
        catat(f"Timer {menit} menit")
    except KeyboardInterrupt:
        print("\n  Timer dibatalkan")


# ============ 34. LIHAT LOG ============
def lihat_log(limit=20):
    """Lihat log aktivitas."""
    rows = db_exec(
        "SELECT aksi, waktu FROM log_aksi ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    print("\n" + "=" * 55)
    print(f"  LOG AKTIVITAS ({len(rows)} terakhir)")
    print("=" * 55)
    if not rows:
        print("  (belum ada log)")
    else:
        for aksi, waktu in rows:
            print(f"  [{waktu[:19]}] {aksi}")
    print("=" * 55)


# ============ 35. CUACA (alias) ============
def cuaca():
    """Alias cuaca_plus()."""
    return cuaca_plus()


# ============ 36. TRANSLATE ============
def translate():
    """Buka Google Translate di browser."""
    print("  [1] Indonesia -> Inggris")
    print("  [2] Inggris -> Indonesia")
    print("  [3] Custom")
    p = input("  Pilih: ").strip()

    teks = input("  Teks yang mau diterjemah: ").strip()
    if not teks:
        return

    from urllib.parse import quote
    if p == "1":
        url = f"https://translate.google.com/?sl=id&tl=en&text={quote(teks)}"
    elif p == "2":
        url = f"https://translate.google.com/?sl=en&tl=id&text={quote(teks)}"
    else:
        url = f"https://translate.google.com/?text={quote(teks)}"

    webbrowser.open(url)
    print("  Google Translate dibuka di browser")
    catat(f"Translate: {teks[:30]}")


# ============ 37. SET REMINDER ============
def set_reminder():
    """Set reminder ke database."""
    con = sqlite3.connect(P["db"])
    con.execute("""CREATE TABLE IF NOT EXISTS reminder (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jam TEXT, pesan TEXT, aktif INTEGER DEFAULT 1,
        dibuat TEXT
    )""")
    con.commit()
    con.close()

    jam = input("  Jam (HH:MM): ").strip()
    pesan = input("  Pesan: ").strip()
    if not jam or not pesan:
        print("  Jam & pesan wajib")
        return

    db_exec(
        "INSERT INTO reminder (jam, pesan, dibuat) VALUES (?, ?, ?)",
        (jam, pesan, datetime.now().isoformat())
    )
    print(f"  Reminder set: {jam} - {pesan}")
    catat(f"Reminder: {jam}")


# ============ 38. LIHAT REMINDER ============
def lihat_reminder():
    """Lihat reminder aktif."""
    rows = db_exec("SELECT id, jam, pesan FROM reminder WHERE aktif = 1 ORDER BY jam")
    print("\n" + "=" * 55)
    print("  REMINDER AKTIF")
    print("=" * 55)
    if not rows:
        print("  (belum ada reminder)")
    else:
        for id_r, jam, pesan in rows:
            print(f"  #{id_r} [{jam}] {pesan}")
    print("=" * 55)


# ============ 39. NOTIF TEST ============
def notif_test():
    """Test notifikasi Windows."""
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(
            "ORION",
            "Test notifikasi berhasil!",
            duration=5,
            threaded=True
        )
        print("  Notifikasi dikirim")
    except ImportError:
        print("  Install dulu: pip install win10toast")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 40. GRAFIK HABIT ============
def grafik_habit():
    """Grafik aktivitas dari log."""
    try:
        rows = db_exec(
            "SELECT substr(waktu, 1, 13) as jam, COUNT(*) FROM log_aksi GROUP BY jam ORDER BY jam DESC LIMIT 10"
        )
        print("\n" + "=" * 55)
        print("  GRAFIK AKTIVITAS (10 jam terakhir)")
        print("=" * 55)
        if not rows:
            print("  (belum ada data)")
        else:
            for jam, count in rows:
                bar = "#" * min(count, 40)
                print(f"  {jam}  {bar} ({count})")
        print("=" * 55)
    except Exception as e:
        print(f"  Error: {e}")


# ============ 41. SETUP AUTOSTART ============
def setup_autostart():
    """Set ORION auto-start pas Windows nyala."""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        exe = f'pythonw "{Path(P["base"]) / "orion.py"}"'
        winreg.SetValueEx(key, "ORION", 0, winreg.REG_SZ, exe)
        winreg.CloseKey(key)
        print("  Auto-start AKTIF")
        catat("Auto-start ON")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 42. DISABLE AUTOSTART ============
def disable_autostart():
    """Matikan auto-start."""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "ORION")
            print("  Auto-start DIMATIKAN")
        except FileNotFoundError:
            print("  Auto-start belum aktif")
        winreg.CloseKey(key)
        catat("Auto-start OFF")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 43. INFO ORION ============
def info():
    """Info tentang ORION."""
    print("\n" + "=" * 55)
    print("  INFO ORION")
    print("=" * 55)
    print(f"  Nama     : {CFG.get('project', 'ORION')}")
    print(f"  Versi    : {CFG.get('version', '2.0')}")
    print(f"  Owner    : {CFG.get('owner', 'Riki Wahyudi')}")
    print(f"  Tagline  : {CFG.get('tagline', 'Personal AI Assistant')}")
    print()
    print(f"  Base     : {P['base']}")
    print(f"  Model    : {P['model']}")
    print(f"  DB       : {P['db']}")
    print()
    model = Path(P["model"])
    if model.exists():
        size = model.stat().st_size
        print(f"  Model    : ADA ({size} bytes)")
    else:
        print(f"  Model    : BELUM ADA (latih dulu)")
    print()
    print(f"  Aktivitas: {CFG['model']['aktivitas']}")
    print("=" * 55)

# ============ HELPER ORION BARU ============
def orion_ingat(topik: str, isi: str, penting: int = 0):
    """Simpan memori ke agent_memory."""
    if _MODUL_OK and MEM:
        MEM.simpan_memori(topik, isi, penting)
        log.info(f"Memori disimpan: {topik}")
        return True
    return False


def orion_recall(kata_kunci: str = "", limit: int = 5):
    """Ambil memori relevan."""
    if _MODUL_OK and MEM:
        return MEM.ambil_memori(kata_kunci, limit)
    return []


def orion_cari(query: str, limit: int = 5):
    """Cari di Wikipedia."""
    if _MODUL_OK and WEB:
        return WEB.search_wikipedia(query, limit=limit)
    return [{"error": "web_orion tidak tersedia"}]


def orion_skill(nama: str):
    """Load skill dari folder skills/."""
    if _MODUL_OK and MEM:
        return MEM.load_skill(nama)
    return ""


def orion_notif(judul: str, pesan: str, penting: int = 0):
    """Kirim notifikasi ke Riki."""
    if _MODUL_OK and NOTIF:
        NOTIF.kirim_notif(judul, pesan, penting)
        return True
    print(f"[NOTIF-FALLBACK] {judul}: {pesan}")
    return False
# ============================================
