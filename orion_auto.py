"""orion_auto.py - Auto evolve tiap 1 jam."""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
LOG = BASE / "arsip" / "auto_evolve.log"
INTERVAL = 3600  # 1 jam

def log(msg):
    """Log ke file + console."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{waktu}] {msg}"
    print(line)
    
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def jalankan_evolve():
    """Jalankan evolve v3."""
    try:
        result = subprocess.run(
            [sys.executable, "orion_evolve_v3.py"],
            capture_output=True,
            text=True,
            cwd=str(BASE),
            timeout=300,
        )
        
        # Parse output
        output = result.stdout
        errors = 0
        fixed = 0
        
        for line in output.split("\n"):
            if "Total error:" in line:
                try:
                    errors = int(line.split(":")[-1].strip())
                except Exception:
                    pass
            if line.strip().startswith("Fixed:"):
                try:
                    fixed = int(line.split(":")[-1].strip())
                except Exception:
                    pass
        
        log(f"Evolve selesai - Error: {errors}, Fixed: {fixed}")
        
        # Notif kalau ada error
        if errors > 0:
            try:
                from orion_alert import notif_windows
                notif_windows(f"Orion - {errors} Error", f"Fixed: {fixed}")
            except Exception:
                pass
        
        return errors, fixed
    except Exception as e:
        log(f"Evolve error: {e}")
        return 0, 0

if __name__ == "__main__":
    log("=== ORION AUTO START ===")
    log(f"Interval: {INTERVAL} detik ({INTERVAL//60} menit)")
    
    try:
        while True:
            log("Cek...")
            jalankan_evolve()
            log(f"Tunggu {INTERVAL//60} menit...")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        log("=== ORION AUTO STOP ===")
