"""orion_supervisor.py -- Penjaga jantung ORION.

Tugasnya cuma dua:
  1. Kalau jantung (orion_hidup.py) mati/crash -> hidupkan lagi.
  2. Kalau file kode berubah -> restart jantung saja (biar patch langsung ngefek).

Yang TIDAK dia lakukan: mematikan proses Python lain (webchat, bot, dsb).
Dia hanya mengelola proses jantung yang dia lahirkan sendiri, plus
membersihkan jantung yatim (orion_hidup.py yang jalan tanpa supervisor)
saat pertama start.

Cara pakai: python orion_supervisor.py   (gantikan double-click ORION-HIDUP.bat)
Berhenti: Ctrl+C di jendela ini.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEART = ROOT / "orion_hidup.py"
LOG_FILE = ROOT / "support" / "logs" / "supervisor.log"

# File yang dipantau. Kalau salah satunya berubah -> restart jantung.
WATCH = [
    ROOT / "orion_hidup.py",
    ROOT / "orion_tool_loop.py",
    ROOT / "support" / "cron_orion.py",
    ROOT / "core" / "otonom" / "kontrol" / "kontrol_utama.py",
]

POLL_DETIK = 5
BATAS_CRASH_CEPAT = 3   # mati <10 detik sebanyak ini -> jeda panjang
JEDA_CRASH_DETIK = 60


def log(msg):
    baris = f"[supervisor {time.strftime('%H:%M:%S')}] {msg}"
    print(baris, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def bersihkan_jantung_yatim():
    """Matikan proses orion_hidup.py yang tidak dilahirkan supervisor ini.

    Hanya menyentuh proses yang commandline-nya mengandung 'orion_hidup.py'.
    TIDAK pakai taskkill /im python.exe (itu membunuh semua Python).
    """
    try:
        out = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'",
             "get", "processid,commandline", "/format:csv"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception as e:
        log(f"lewati bersih-bersih yatim (wmic gagal: {e})")
        return
    dibunuh = 0
    for baris in out.stdout.splitlines():
        b = baris.strip().strip(",")
        if not b or "orion_hidup" not in b.lower():
            continue
        if "orion_supervisor" in b.lower():
            continue
        # format CSV: Node,CommandLine,ProcessId -> PID = kolom terakhir
        pid = b.rsplit(",", 1)[-1].strip()
        if pid.isdigit() and int(pid) != 0:
            try:
                subprocess.run(["taskkill", "/f", "/pid", pid],
                               capture_output=True, timeout=10)
                dibunuh += 1
            except Exception:
                pass
    if dibunuh:
        log(f"membersihkan {dibunuh} jantung yatim.")


def luncurkan():
    return subprocess.Popen([sys.executable, str(HEART)], cwd=str(ROOT))


def snapshot():
    return {str(p): p.stat().st_mtime for p in WATCH if p.is_file()}


def main():
    if not HEART.is_file():
        log(f"GAGAL: {HEART} tidak ketemu.")
        return 1
    log(f"mengawasi {len(WATCH)} file, cek tiap {POLL_DETIK} detik.")
    bersihkan_jantung_yatim()
    proc = luncurkan()
    log(f"jantung hidup (PID {proc.pid}). Ctrl+C untuk berhenti.")
    terakhir = snapshot()
    crash_cepat = 0
    try:
        while True:
            time.sleep(POLL_DETIK)
            if proc.poll() is not None:
                # jantung mati sendiri -> hidupkan lagi
                umur = time.time() - getattr(proc, "_start", time.time())
                if umur < 10:
                    crash_cepat += 1
                else:
                    crash_cepat = 0
                if crash_cepat >= BATAS_CRASH_CEPAT:
                    log(f"jantung crash {crash_cepat}x beruntun, jeda {JEDA_CRASH_DETIK}s...")
                    time.sleep(JEDA_CRASH_DETIK)
                    crash_cepat = 0
                else:
                    log("jantung mati, menghidupkan lagi...")
                proc = luncurkan()
                proc._start = time.time()
                terakhir = snapshot()
                continue
            if snapshot() != terakhir:
                log("file berubah, restart jantung...")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                proc = luncurkan()
                proc._start = time.time()
                terakhir = snapshot()
                log(f"jantung restart (PID {proc.pid}).")
    except KeyboardInterrupt:
        log("berhenti. Mematikan jantung...")
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
