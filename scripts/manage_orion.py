"""
manage_orion.py - Launcher Orion dengan auto-reload.
Pantau file .py, restart Orion kalau ada perubahan.
"""
import sys
import subprocess
import time
from pathlib import Path

BASE = Path(__file__).parent

# File yang dipantau (folder)
WATCH_DIR = BASE

# File yang di-ignore (biar nggak restart pas backup/log berubah)
IGNORE_PATTERNS = [
    "backups", "logs", "output", "__pycache__", ".git",
    "voice_bank.json", str(BASE / "memory" / "orion.db"), "cron_tasks.json",
    ".bak", ".old", ".pyc",
]


def _perlu_ignore(path):
    """Cek apakah file perlu di-ignore."""
    p = str(path).lower()
    for pat in IGNORE_PATTERNS:
        if pat.lower() in p:
            return True
    return False


def start_orion():
    """Jalankan Orion sebagai subprocess."""
    return subprocess.Popen(
        [sys.executable, str(BASE / "orion.py")],
        cwd=str(BASE),
    )


def jalankan_dengan_reload():
    """Launcher utama dengan auto-reload."""
    try:
        from watchfiles import watch
    except ImportError:
        print("Install dulu: pip install watchfiles")
        return
    
    print("=" * 50)
    print("ORION MANAGER - Auto-Reload")
    print("=" * 50)
    print(f"Pantau folder: {BASE}")
    print("Edit file .py -> Orion restart otomatis")
    print("Tekan Ctrl+C buat stop")
    print("=" * 50)
    print()
    
    # Start Orion pertama kali
    print("[manager] Menjalankan Orion...")
    proses = start_orion()
    
    try:
        # Pantau perubahan file
        for changes in watch(str(WATCH_DIR), debounce=1000):
            # Filter: cuma file .py yang berubah
            py_changes = [
                (change, path) for change, path in changes
                if path.endswith(".py") and not _perlu_ignore(path)
            ]
            
            if not py_changes:
                continue
            
            # Ada perubahan .py
            print()
            print(f"[manager] Perubahan terdeteksi:")
            for change, path in py_changes[:5]:
                nama = Path(path).name
                print(f"  - {nama}")
            
            # Matiin Orion lama
            if proses.poll() is None:
                print("[manager] Menghentikan Orion...")
                proses.terminate()
                try:
                    proses.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proses.kill()
            
            # Tunggu sebentar biar file selesai ditulis
            time.sleep(0.5)
            
            # Start Orion baru
            print("[manager] Menjalankan ulang Orion...")
            proses = start_orion()
            print("[manager] Siap. Edit lagi kapan aja.")
            print()
    
    except KeyboardInterrupt:
        print()
        print("[manager] Stop. Menghentikan Orion...")
        if proses.poll() is None:
            proses.terminate()
            try:
                proses.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proses.kill()
        print("[manager] Selesai.")


if __name__ == "__main__":
    jalankan_dengan_reload()
