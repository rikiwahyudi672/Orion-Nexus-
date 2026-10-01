"""cek_rumah.py - Orion tahu isi rumahnya (real-time)."""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
SNAPSHOT_FILE = BASE / "core" / "otonom" / "kesadaran_rumah" / "snapshot_rumah.json"


def scan_rumah() -> dict:
    """Scan isi rumah Orion."""
    if not BASE.exists():
        return {"sukses": False, "error": f"Rumah tidak ada: {BASE}"}
    
    # Kategori folder
    folder_penting = {
        "core": BASE / "core",
        "core/otonom": BASE / "core" / "otonom",
        "core/otonom/kesadaran": BASE / "core" / "otonom" / "kesadaran",
        "core/otonom/kesadaran_rumah": BASE / "core" / "otonom" / "kesadaran_rumah",
        "core/otonom/evolusi": BASE / "core" / "otonom" / "evolusi",
        "core/otonom/kontrol": BASE / "core" / "otonom" / "kontrol",
        "memory": BASE / "memory",
        "voice": BASE / "voice",
        "skill": BASE / "skill",
        "config": BASE / "config",
    }
    
    hasil = {
        "waktu": datetime.now().isoformat(),
        "base": str(BASE),
        "total_py": 0,
        "total_file": 0,
        "folder": {},
    }
    
    # Scan tiap folder
    for nama, folder in folder_penting.items():
        if not folder.exists():
            hasil["folder"][nama] = {"ada": False}
            continue
        
        py_files = list(folder.rglob("*.py"))
        all_files = [f for f in folder.rglob("*") if f.is_file()]
        
        # Skip __pycache__
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        all_files = [f for f in all_files if "__pycache__" not in str(f)]
        
        hasil["folder"][nama] = {
            "ada": True,
            "py": len(py_files),
            "total": len(all_files),
            "path": str(folder),
        }
        
        hasil["total_py"] += len(py_files)
        hasil["total_file"] += len(all_files)
    
    return {"sukses": True, **hasil}


def ringkasan_rumah() -> str:
    """Ringkasan rumah untuk prompt LLM."""
    hasil = scan_rumah()
    if not hasil.get("sukses"):
        return "Tidak bisa scan rumah."
    
    lines = [
        f"RUMAHKU: {hasil['base']}",
        f"Total file Python: {hasil['total_py']}",
        f"Total file: {hasil['total_file']}",
        "",
        "Isi rumah:",
    ]
    
    for nama, info in hasil["folder"].items():
        if info.get("ada"):
            lines.append(f"  - {nama}: {info['py']} py, {info['total']} total")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("  CEK RUMAH ORION")
    print("=" * 60)
    
    print()
    print(ringkasan_rumah())
