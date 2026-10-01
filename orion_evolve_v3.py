"""orion_evolve_v3.py - Evolve + Learn (1 klik)."""
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
MANIFEST = BASE / "orion_manifest.json"
BACKUP = BASE / "arsip" / f"evolve_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

print("=" * 70)
print("  ORION EVOLVE v3 - 1 KLIK (EVOLVE + LEARN)")
print("=" * 70)
print(f"  Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 70)

# === Setup path ===
sys.path.insert(0, str(BASE))
for _f in ["scripts", "core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard", "config"]:
    _p = BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

# === 1. Build manifest (kalau perlu) ===
if not MANIFEST.exists():
    print("\n[1] Build manifest...")
    subprocess.run([sys.executable, "orion_build_manifest.py"])

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
print(f"\n[1] Manifest: {manifest['total']} modul")

# === 2. Scan error ===
print("\n[2] Scan error...")
print("-" * 70)

errors = []

for mod_name, info in manifest["modules"].items():
    file_path = BASE / info["file"]
    
    if not file_path.exists():
        errors.append({"type": "missing", "mod": mod_name, "file": str(file_path), "msg": "File tidak ada"})
        continue
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        ast.parse(content)
    except SyntaxError as e:
        errors.append({"type": "syntax", "mod": mod_name, "file": str(file_path), "msg": f"Syntax baris {e.lineno}: {e.msg}"})

# Scan root
for f in BASE.glob("*.py"):
    if f.name in ["orion_evolve.py", "orion_evolve_v3.py", "orion_health.py", "orion_build_manifest.py", "orion_healer.py", "orion_sandbox.py", "orion_learn.py", "orion_improve.py", "orion_report.py", "orion_alert.py", "orion_monitor.py"]:
        continue
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
        ast.parse(content)
    except SyntaxError as e:
        errors.append({"type": "syntax", "mod": f.stem, "file": str(f), "msg": f"Syntax baris {e.lineno}: {e.msg}"})

print(f"  Total error: {len(errors)}")

# === 3. Klasifikasi + Fix ===
print("\n[3] Klasifikasi:")
print("-" * 70)

bisa_fix = []
manual = []

try:
    from orion_healer import pilih_fixer, fix_error
    HAS_HEALER = True
except ImportError:
    HAS_HEALER = False

for err in errors:
    if HAS_HEALER:
        fixer = pilih_fixer(err["msg"])
        if fixer:
            bisa_fix.append(err)
            continue
    
    msg = err["msg"].lower()
    if "bom" in msg or "non-printable" in msg or "u+feff" in msg or "mojibake" in msg:
        bisa_fix.append(err)
    else:
        manual.append(err)

print(f"  Bisa fix: {len(bisa_fix)}")
print(f"  Manual: {len(manual)}")

# === 4. Backup + Fix ===
if bisa_fix:
    BACKUP.mkdir(parents=True, exist_ok=True)
    for err in bisa_fix:
        file_path = Path(err["file"])
        if file_path.exists():
            rel = file_path.relative_to(BASE)
            backup_path = BACKUP / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

print(f"\n[4] Backup: {BACKUP.name if bisa_fix else 'Tidak ada'}")

print("\n[5] Auto-fix...")
print("-" * 70)

fixed = 0
for err in bisa_fix:
    file_path = Path(err["file"])
    if not file_path.exists():
        continue
    
    if HAS_HEALER:
        try:
            ok, msg = fix_error(file_path, err["msg"])
            if ok:
                print(f"  OK {file_path.name}: {msg}")
                fixed += 1
        except Exception:
            pass

print(f"  Fixed: {fixed}")

# === 6. Simpan laporan ===
BACKUP.mkdir(parents=True, exist_ok=True)

laporan = {
    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "versi": "v3",
    "total_modul": manifest["total"],
    "error_awal": len(errors),
    "auto_fix": fixed,
    "manual": len(manual),
    "backup": str(BACKUP.name),
    "details": errors,
}

(BACKUP / "laporan.json").write_text(json.dumps(laporan, indent=2, ensure_ascii=False), encoding="utf-8")

# === 7. Learn ===
print("\n[6] Learn (analisa pola)...")
print("-" * 70)

try:
    subprocess.run([sys.executable, "orion_learn.py"], cwd=str(BASE), timeout=30)
except Exception as e:
    print(f"  Learn error: {e}")

# === 8. Ringkasan ===
print("\n" + "=" * 70)
print("  LAPORAN")
print("=" * 70)
print(f"  Modul: {manifest['total']}")
print(f"  Error awal: {len(errors)}")
print(f"  Auto-fix: {fixed}")
print(f"  Manual: {len(manual)}")

if manual:
    print(f"\n  Butuh perhatian:")
    for err in manual[:5]:
        print(f"    - {err['mod']}: {err['msg'][:60]}")

print("=" * 70)
print("  SELESAI")
print("=" * 70)
