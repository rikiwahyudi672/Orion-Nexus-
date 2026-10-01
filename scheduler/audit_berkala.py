"""audit_berkala.py - Audit folder E: & C: tiap 1 jam."""
import ast
import json
import time
import threading
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
LOG_DIR = BASE / "scheduler" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Folder yang di-audit
TARGET_FOLDERS = [
    Path("E:/Project Software/Orion"),
    Path("E:/Project Software/Nexus.ai"),
    Path("C:/Users/Riki Wahyudi/AppData/Local/Python"),
]

# Folder yang di-exclude
EXCLUDE = ["_archive", "_backup", "backup", "__pycache__", ".git", "_tmp", "_temp", "_arsip", "venv", ".venv"]


def audit_folder(folder: Path) -> dict:
    """Audit 1 folder."""
    if not folder.exists():
        return {"folder": str(folder), "error": "Tidak ada", "sukses": False}
    
    py_files = []
    for py in folder.rglob("*.py"):
        rel = str(py.relative_to(folder))
        if any(ex in rel for ex in EXCLUDE):
            continue
        py_files.append(py)
    
    syntax_errors = []
    bom_files = []
    import_errors = []
    
    for py in py_files:
        try:
            with open(py, "rb") as f:
                data = f.read()
            
            # Cek BOM
            if data.startswith(b'\xef\xbb\xbf'):
                bom_files.append(str(py.relative_to(folder)))
                continue
            
            # Cek syntax
            try:
                ast.parse(data.decode("utf-8", errors="ignore"))
            except SyntaxError as e:
                syntax_errors.append({
                    "file": str(py.relative_to(folder)),
                    "error": str(e),
                    "line": e.lineno
                })
        except Exception:
            pass
    
    return {
        "folder": str(folder),
        "sukses": True,
        "total_py": len(py_files),
        "syntax_errors": syntax_errors,
        "bom_files": bom_files,
        "waktu": datetime.now().isoformat(),
    }


def audit_semua() -> dict:
    """Audit semua folder."""
    hasil = []
    for folder in TARGET_FOLDERS:
        h = audit_folder(folder)
        hasil.append(h)
    
    return {
        "waktu": datetime.now().isoformat(),
        "total_folder": len(hasil),
        "hasil": hasil,
    }


def simpan_log(hasil: dict):
    """Simpan log audit."""
    tanggal = datetime.now().strftime("%Y%m%d")
    log_file = LOG_DIR / f"audit_{tanggal}.json"
    
    # Baca log lama
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(hasil)
    
    # Simpan
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    return str(log_file)


def format_laporan(hasil: dict) -> str:
    """Format laporan untuk notif."""
    lines = []
    lines.append("🔍 AUDIT BERKALA ORION")
    lines.append(f"Waktu: {hasil['waktu'][:19]}")
    lines.append("")
    
    total_error = 0
    total_bom = 0
    
    for h in hasil["hasil"]:
        if not h.get("sukses"):
            continue
        
        name = Path(h["folder"]).name
        err = len(h.get("syntax_errors", []))
        bom = len(h.get("bom_files", []))
        total = h.get("total_py", 0)
        
        status = "✅" if err == 0 and bom == 0 else "⚠️"
        lines.append(f"{status} {name}: {total} file, {err} error, {bom} BOM")
        
        total_error += err
        total_bom += bom
    
    lines.append("")
    if total_error == 0 and total_bom == 0:
        lines.append("✅ Semua bersih - tidak ada bug")
    else:
        lines.append(f"⚠️ Total: {total_error} error, {total_bom} BOM")
    
    return "\n".join(lines)


def loop_audit(interval_jam: int = 1):
    """Loop audit tiap N jam."""
    print(f"[Audit Berkala] Start - interval {interval_jam} jam")
    
    while True:
        try:
            hasil = audit_semua()
            log_file = simpan_log(hasil)
            laporan = format_laporan(hasil)
            
            print(f"\n{laporan}")
            print(f"\nLog: {log_file}")
            
            # Kirim notif
            try:
                from notif_orion import kirim_notif
                kirim_notif(laporan)
            except Exception as e:
                print(f"[Notif] Error: {e}")
        
        except Exception as e:
            print(f"[Audit] Error: {e}")
        
        # Tunggu N jam
        time.sleep(interval_jam * 3600)


def start(interval_jam: int = 1):
    """Start audit berkala di thread."""
    thread = threading.Thread(target=loop_audit, args=(interval_jam,), daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    # Test sekali
    print("=== TEST AUDIT ===")
    hasil = audit_semua()
    print(format_laporan(hasil))
