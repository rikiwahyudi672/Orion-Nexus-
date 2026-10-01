"""safety.py - Keamanan evolusi kode Orion (Level 3)."""
import os
import re
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")

# === Folder yang DILARANG diubah ===
FOLDER_TERLARANG = [
    "C:/Windows",
    "C:/Program Files",
    "C:/Program Files (x86)",
    "C:/Users",
    "E:/Windows",
]

# === File yang DILARANG diubah ===
FILE_TERLARANG = [
    "otak_orion.py",
    "SOUL.md",
    "config/.env",
]

# === Folder yang DIIZINKAN (pakai Path object) ===
FOLDER_DIIZINKAN = [
    BASE / "core" / "otonom" / "evolusi" / "output",
    BASE / "core" / "otonom" / "evolusi" / "modul",
    BASE / "evolusi" / "sandbox",
]

# === Batas evolusi ===
MAX_EVOLUSI_PER_HARI = 3
MAX_LINE_KODE = 200
MAX_FILE_BARU = 5


def _normalize(path) -> str:
    """Normalisasi path — pakai forward slash + lowercase."""
    return str(Path(path).resolve()).replace("\\", "/").lower()


def cek_path_aman(path: str) -> tuple:
    """
    Cek apakah path aman untuk ditulis.
    Return: (aman: bool, alasan: str)
    """
    p = Path(path).resolve()
    p_norm = _normalize(p)
    
    # Cek folder terlarang
    for folder in FOLDER_TERLARANG:
        folder_norm = _normalize(folder)
        if p_norm.startswith(folder_norm):
            return False, f"Folder terlarang: {folder}"
    
    # Cek file terlarang
    for file in FILE_TERLARANG:
        if p.name == file or p_norm.endswith(file.lower()):
            return False, f"File terlarang: {file}"
    
    # Cek folder diizinkan
    diizinkan = False
    for folder in FOLDER_DIIZINKAN:
        folder_norm = _normalize(folder)
        if p_norm.startswith(folder_norm):
            diizinkan = True
            break
    
    if not diizinkan:
        return False, f"Folder tidak diizinkan. Hanya: {[str(f) for f in FOLDER_DIIZINKAN]}"
    
    return True, "Aman"


def cek_kode_aman(kode: str) -> tuple:
    """Cek apakah kode aman."""
    pattern_bahaya = [
        (r'import\s+os\s*;.*os\.system', "os.system — berbahaya"),
        (r'subprocess\.(call|run|Popen)', "subprocess — berbahaya"),
        (r'rm\s+-rf', "rm -rf — berbahaya"),
        (r'del\s+/[fs]', "del — berbahaya"),
        (r'format\s+[c-z]:', "format drive — berbahaya"),
        (r'shutil\.rmtree', "shutil.rmtree — berbahaya"),
        (r'os\.remove.*\*', "os.remove wildcard — berbahaya"),
        (r'open\(.*[\'"]w[\'"].*C:', "tulis ke C: — berbahaya"),
        (r'eval\(', "eval — berbahaya"),
        (r'exec\(', "exec — berbahaya"),
        (r'__import__\(', "__import__ — berbahaya"),
    ]
    
    for pattern, alasan in pattern_bahaya:
        if re.search(pattern, kode, re.IGNORECASE):
            return False, alasan
    
    lines = kode.split("\n")
    if len(lines) > MAX_LINE_KODE:
        return False, f"Kode terlalu panjang: {len(lines)} baris (max {MAX_LINE_KODE})"
    
    return True, "Aman"


def cek_limit_evolusi() -> tuple:
    """Cek apakah masih bisa evolusi hari ini."""
    log_file = BASE / "evolusi" / "log_evolusi.json"
    
    if not log_file.exists():
        return True, "Belum ada evolusi hari ini"
    
    import json
    try:
        log = json.loads(log_file.read_text(encoding="utf-8"))
    except Exception:
        return True, "Log tidak bisa dibaca"
    
    hari_ini = datetime.now().strftime("%Y-%m-%d")
    evolusi_hari_ini = [e for e in log if e.get("tanggal", "").startswith(hari_ini)]
    
    if len(evolusi_hari_ini) >= MAX_EVOLUSI_PER_HARI:
        return False, f"Sudah {len(evolusi_hari_ini)} evolusi hari ini (max {MAX_EVOLUSI_PER_HARI})"
    
    return True, f"Masih bisa ({len(evolusi_hari_ini)}/{MAX_EVOLUSI_PER_HARI})"


def catat_evolusi(file_path: str, aksi: str, sukses: bool):
    """Catat evolusi ke log."""
    import json
    
    log_file = BASE / "evolusi" / "log_evolusi.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    if log_file.exists():
        try:
            log = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            log = []
    else:
        log = []
    
    log.append({
        "tanggal": datetime.now().isoformat(),
        "file": file_path,
        "aksi": aksi,
        "sukses": sukses,
    })
    
    log_file.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST SAFETY EVOLUSI")
    print("=" * 60)
    
    print("\n=== Cek Path ===")
    for path in [
        "E:/Project Software/Orion/core/otonom/evolusi/output/test.py",
        "E:\\Project Software\\Orion\\core\\otonom\\evolusi\\output\\test.py",
        "E:/Project Software/Orion/core/otak_orion.py",
        "C:/Windows/system32/test.py",
    ]:
        aman, alasan = cek_path_aman(path)
        print(f"  {'OK' if aman else 'X'} {path}")
        print(f"     → {alasan}")
    
    print("\n=== Cek Kode ===")
    for kode in [
        "print('halo')",
        "import os; os.system('dir')",
    ]:
        aman, alasan = cek_kode_aman(kode)
        print(f"  {'OK' if aman else 'X'} {kode[:40]}: {alasan}")
    
    print("\n=== Cek Limit ===")
    bisa, alasan = cek_limit_evolusi()
    print(f"  {'OK' if bisa else 'X'} {alasan}")
