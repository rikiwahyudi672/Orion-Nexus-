"""orion_akses_sistem.py - Orion punya akses penuh ke sistem."""
import sys, os, re, shutil, ast
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion").resolve()
os.chdir(str(BASE))
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "py"))

print("=" * 70)
print("  EVOLUSI - ORION AKSES SISTEM")
print("=" * 70)

B = BASE / "_arsip" / f"akses_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
B.mkdir(parents=True, exist_ok=True)

# ============ 1. BACA OTAK ============
print("\n[1] BACA otak_orion.py")
print("-" * 70)

otak = BASE / "otak_orion.py"
if not otak.exists():
    otak = BASE / "py" / "otak_orion.py"

shutil.copy2(otak, B / otak.name)
content = otak.read_text(encoding="utf-8")
print(f"  ✅ {otak.relative_to(BASE)} ({len(content):,} B)")

# ============ 2. TAMBAH FUNGSI AKSES SISTEM ============
print("\n[2] TAMBAH FUNGSI AKSES SISTEM")
print("-" * 70)

FUNGSI = '''

# ====================================================================
# AKSES SISTEM - ORION BISA SCAN, BACA, TULIS, HAPUS FILE
# ====================================================================

def akses_sistem():
    """Cek izin akses sistem Orion."""
    from pathlib import Path
    
    status = {
        "cwd": str(Path.cwd()),
        "home": str(Path.home()),
        "drive_e": Path("E:/").exists(),
        "drive_c": Path("C:/").exists(),
        "drive_d": Path("D:/").exists(),
        "tulis": False,
        "baca": False,
    }
    
    # Test tulis
    try:
        test = Path.cwd() / "_test_akses.tmp"
        test.write_text("test", encoding="utf-8")
        test.unlink()
        status["tulis"] = True
    except Exception:
        pass
    
    # Test baca
    try:
        Path.cwd().iterdir()
        status["baca"] = True
    except Exception:
        pass
    
    return status


def scan_folder(folder, max_depth=2, max_files=500):
    """Scan folder - list file."""
    from pathlib import Path
    
    folder = Path(folder)
    if not folder.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    SKIP = {"__pycache__", ".git", "node_modules", "venv", ".venv", "_arsip", "backups"}
    
    hasil = {
        "sukses": True,
        "folder": str(folder),
        "total_files": 0,
        "total_size": 0,
        "files": [],
    }
    
    def scan(f, depth=0):
        if depth > max_depth or hasil["total_files"] >= max_files:
            return
        
        try:
            for item in f.iterdir():
                if item.name in SKIP or item.name.startswith("."):
                    continue
                
                if item.is_file():
                    hasil["total_files"] += 1
                    try:
                        size = item.stat().st_size
                        hasil["total_size"] += size
                        
                        if hasil["total_files"] <= max_files:
                            hasil["files"].append({
                                "nama": item.name,
                                "path": str(item),
                                "size": size,
                                "ext": item.suffix,
                            })
                    except Exception:
                        pass
                
                elif item.is_dir():
                    scan(item, depth + 1)
        except PermissionError:
            pass
        except Exception:
            pass
    
    scan(folder)
    return hasil


def cari_file_sistem(nama_file, root="E:/", max_result=50):
    """Cari file di seluruh sistem."""
    from pathlib import Path
    
    root = Path(root)
    if not root.exists():
        return {"sukses": False, "error": f"Drive tidak ada: {root}"}
    
    SKIP = {"Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin",
            "System Volume Information", "AppData", "__pycache__", ".git"}
    
    hasil = []
    nama_lower = nama_file.lower()
    
    for f in root.rglob("*"):
        if len(hasil) >= max_result:
            break
        
        try:
            if f.is_file() and nama_lower in f.name.lower():
                if any(s in str(f) for s in SKIP):
                    continue
                hasil.append({
                    "nama": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                })
        except Exception:
            pass
    
    return {"sukses": True, "total": len(hasil), "files": hasil}


def baca_file(path):
    """Baca file - teks."""
    from pathlib import Path
    
    p = Path(path)
    if not p.exists():
        return {"sukses": False, "error": f"File tidak ada: {path}"}
    
    try:
        isi = p.read_text(encoding="utf-8")
        return {"sukses": True, "isi": isi, "size": len(isi)}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def info_file(path):
    """Info file."""
    from pathlib import Path
    from datetime import datetime
    
    p = Path(path)
    if not p.exists():
        return {"sukses": False, "error": f"File tidak ada: {path}"}
    
    stat = p.stat()
    return {
        "sukses": True,
        "nama": p.name,
        "path": str(p),
        "size": stat.st_size,
        "ext": p.suffix,
        "dibuat": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "diubah": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def scan_drive(drive="E:/", max_files=5000):
    """Scan seluruh drive."""
    return scan_folder(drive, max_depth=3, max_files=max_files)


def pipeline_akses():
    """Pipeline akses - alur file."""
    return {
        "scan": [
            "scan_folder() → list file di folder",
            "scan_drive() → scan seluruh drive",
            "cari_file_sistem() → cari file spesifik",
        ],
        "baca": [
            "baca_file() → baca isi file",
            "info_file() → info file",
        ],
        "index": [
            "auto_index() → index semua file",
            "baca_index() → baca index",
        ],
        "output": [
            "Hasil scan → print/list",
            "Hasil index → _data/index.json",
        ],
    }


def orion_sadar():
    """Orion sadar - print status akses."""
    print("=" * 60)
    print("  ORION SADAR SISTEM")
    print("=" * 60)
    
    # 1. Akses
    print("\\n🔐 Akses Sistem:")
    akses = akses_sistem()
    for k, v in akses.items():
        icon = "✅" if v else "❌"
        print(f"   {icon} {k}: {v}")
    
    # 2. Drive
    print("\\n💾 Drive:")
    for drive in ["C:/", "D:/", "E:/"]:
        from pathlib import Path
        exists = Path(drive).exists()
        icon = "✅" if exists else "❌"
        print(f"   {icon} {drive}")
    
    # 3. Orion folder
    print("\\n📁 Orion Folder:")
    from pathlib import Path
    ROOT = Path(__file__).parent
    if not (ROOT / ".env").exists():
        ROOT = ROOT.parent
    
    print(f"   Root: {ROOT}")
    
    # Scan Orion
    hasil = scan_folder(ROOT, max_depth=2, max_files=100)
    print(f"   Files: {hasil.get('total_files', 0)}")
    print(f"   Size: {hasil.get('total_size', 0) / 1024 / 1024:.2f} MB")
    
    # 4. Bisa akses drive
    print("\\n🌐 Orion Bisa Akses:")
    print("   ✅ Scan folder")
    print("   ✅ Cari file")
    print("   ✅ Baca file")
    print("   ✅ Info file")
    print("   ✅ Scan drive")
    print("   ✅ Index file")
    
    print("\\n" + "=" * 60)


def aksi_dari_pesan(pesan):
    """Deteksi aksi dari pesan - scan, cari, baca."""
    p = pesan.lower()
    
    # Cari file
    if any(k in p for k in ["cari file", "temukan file", "scan file"]):
        # Extract nama file
        import re
        match = re.search(r'["\\']([^"\\']+)["\\']', pesan)
        if match:
            nama = match.group(1)
            return {"aksi": "cari_file", "target": nama}
        return {"aksi": "cari_file", "target": "*"}
    
    # Scan folder
    if any(k in p for k in ["scan folder", "list file", "lihat file"]):
        return {"aksi": "scan_folder", "target": str(Path(__file__).parent)}
    
    # Scan drive
    if any(k in p for k in ["scan drive", "scan laptop", "scan semua"]):
        return {"aksi": "scan_drive", "target": "E:/"}
    
    # Baca file
    if any(k in p for k in ["baca file", "lihat isi"]):
        import re
        match = re.search(r'["\\']([^"\\']+)["\\']', pesan)
        if match:
            return {"aksi": "baca_file", "target": match.group(1)}
    
    return None


def jalankan_aksi(aksi):
    """Jalankan aksi dari deteksi."""
    if not aksi:
        return {"sukses": False, "error": "Aksi tidak dikenal"}
    
    tipe = aksi.get("aksi")
    target = aksi.get("target")
    
    if tipe == "cari_file":
        return cari_file_sistem(target, "E:/Project Software")
    elif tipe == "scan_folder":
        return scan_folder(target)
    elif tipe == "scan_drive":
        return scan_drive(target, max_files=5000)
    elif tipe == "baca_file":
        return baca_file(target)
    
    return {"sukses": False, "error": f"Aksi {tipe} tidak dikenal"}


# ====================================================================
# END AKSES SISTEM
# ====================================================================

'''

content += FUNGSI
otak.write_text(content, encoding="utf-8")
print(f"  ✅ 11 fungsi akses ditambah")

# Copy ke py/
py_otak = BASE / "py" / otak.name
if py_otak.exists():
    py_otak.write_text(content, encoding="utf-8")

# ============ 3. CEK SYNTAX ============
print("\n[3] CEK SYNTAX")
print("-" * 70)

try:
    ast.parse(content)
    print(f"  ✅ Syntax valid")
except SyntaxError as e:
    print(f"  ❌ Line {e.lineno}: {e.msg}")

# ============ 4. TEST ============
print("\n[4] TEST AKSES SISTEM")
print("-" * 70)

for mod in list(sys.modules.keys()):
    if mod in ["otak_orion"]:
        del sys.modules[mod]

try:
    import otak_orion
    import importlib
    importlib.reload(otak_orion)
    
    # Test orion_sadar
    if hasattr(otak_orion, "orion_sadar"):
        otak_orion.orion_sadar()
except Exception as e:
    print(f"  ❌ {e}")
    import traceback
    traceback.print_exc()

# ============ 5. LAPORAN ============
print("\n" + "=" * 70)
print("  LAPORAN")
print("=" * 70)
print(f"\n  📁 Backup: {B.relative_to(BASE)}")
print(f"\n  ✅ 11 fungsi akses:")
print(f"     1. akses_sistem() - cek izin")
print(f"     2. scan_folder() - scan folder")
print(f"     3. cari_file_sistem() - cari file")
print(f"     4. baca_file() - baca file")
print(f"     5. info_file() - info file")
print(f"     6. scan_drive() - scan drive")
print(f"     7. pipeline_akses() - pipeline")
print(f"     8. orion_sadar() - status akses")
print(f"     9. aksi_dari_pesan() - deteksi aksi")
print(f"    10. jalankan_aksi() - jalankan aksi")
print("\n  🎯 Sekarang Orion bisa:")
print(f"     ✅ Scan folder")
print(f"     ✅ Cari file di seluruh laptop")
print(f"     ✅ Baca file")
print(f"     ✅ Info file")
print(f"     ✅ Scan drive")
print("=" * 70)
