"""audit_otomatis.py - Audit berkala otomatis - 1 jam sekali."""
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "skills" / "audit-folder"))

# Target folder audit
TARGET_FOLDERS = [
    "E:/Project Software/Orion",
    "E:/Project Software/Nexus.ai",
]

INTERVAL_JAM = 1
LOG_FILE = BASE / "scheduler" / "logs" / "audit_otomatis.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    """Log ke file & console."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{waktu}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def audit_semua():
    """Audit semua target folder."""
    from audit import audit_folder, format_audit
    
    hasil_list = []
    total_error = 0
    total_bom = 0
    
    for folder in TARGET_FOLDERS:
        try:
            h = audit_folder(folder)
            hasil_list.append(h)
            
            if h.get("sukses"):
                err = len(h.get("syntax_errors", []))
                bom = len(h.get("bom_files", []))
                total_error += err
                total_bom += bom
                
                name = Path(folder).name
                log(f"  {name}: {h.get('total_py', 0)} file, {err} error, {bom} BOM")
        except Exception as e:
            log(f"  Error audit {folder}: {e}")
    
    return {
        "total_error": total_error,
        "total_bom": total_bom,
        "hasil": hasil_list,
    }


def kirim_notif(pesan: str):
    """Kirim notif via notif_orion."""
    try:
        from notif_orion import kirim_notif
        kirim_notif(judul="Audit Orion", pesan=pesan, penting=1)
        log("  Notif terkirim")
    except Exception as e:
        log(f"  Notif error: {e}")


def loop_audit():
    """Loop audit tiap 1 jam."""
    log("=" * 50)
    log("AUDIT OTOMATIS START")
    log(f"Target: {len(TARGET_FOLDERS)} folder")
    log(f"Interval: {INTERVAL_JAM} jam")
    log("=" * 50)
    
    while True:
        try:
            log("")
            log("--- AUDIT MULAI ---")
            
            hasil = audit_semua()
            
            total_error = hasil["total_error"]
            total_bom = hasil["total_bom"]
            
            log(f"--- SELESAI: {total_error} error, {total_bom} BOM ---")
            
            # Kirim notif kalau ada masalah
            if total_error > 0 or total_bom > 0:
                pesan = f"⚠️ AUDIT ORION\n{total_error} syntax error\n{total_bom} BOM files\n\nCek: scheduler/logs/audit_otomatis.log"
                kirim_notif(pesan)
            else:
                log("  Semua bersih - tidak ada notif")
        
        except Exception as e:
            log(f"ERROR: {e}")
        
        # Tunggu 1 jam
        log(f"Tunggu {INTERVAL_JAM} jam...")
        time.sleep(INTERVAL_JAM * 3600)


def start():
    """Start audit otomatis di background."""
    thread = threading.Thread(target=loop_audit, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    loop_audit()
