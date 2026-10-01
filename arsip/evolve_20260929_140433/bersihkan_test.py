import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(".")
ARSIP = BASE / "arsip_test" / f"test_bekas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
ARSIP.mkdir(parents=True, exist_ok=True)

test_patterns = ["cek_*.py", "test_*.py", "orion_cek_*.py", "patch_*.py", "clean_*.py", "reset_*.py", "coba_*.py", "debug_*.py"]
files = []
for p in test_patterns:
    files.extend([f for f in BASE.glob(p) if f.is_file()])
files.extend([f for f in BASE.glob("*.bak*") if f.is_file()])
files.extend([f for f in (BASE / "core").glob("*.bak*") if f.is_file()])
files.extend([f for f in (BASE / "memory").glob("*.bak*") if f.is_file()])
files.extend([f for f in (BASE / "skill").rglob("*.bak*") if f.is_file()])

moved = 0
for f in files:
    try:
        rel = f.relative_to(BASE)
        dest = ARSIP / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(dest))
        moved += 1
    except Exception:
        pass

print(f"[OK] Dipindah: {moved} file")
print(f"     Ke: {ARSIP}")
