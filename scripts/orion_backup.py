"""orion_backup.py - Backup lengkap Orion."""
import os, shutil, json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion").resolve()
os.chdir(str(BASE))

# Folder backup
TANGGAL = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = Path(f"E:/Orion_Backup/backup_{TANGGAL}")
BACKUP.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  BACKUP ORION")
print(f"  {TANGGAL}")
print("=" * 60)
print(f"📁 Tujuan: {BACKUP}")
print()

# ============ 1. FILE INTI ============
print("[1] FILE INTI")
print("-" * 60)

FILE_INTI = [
    "otak_orion.py", "core.py", "orion_hub.py",
    "model_router.py", "coding_assistant.py",
    "memory_graph.py", "experience_hub.py",
    "skill_loader.py", "skill_hub.py", "tool_eksekusi.py",
    "voice_orion.py", "orion_voice.py",
    "dashboard_orion.py", "emotion_orion.py",
    "personality_orion.py", "cron_orion.py",
    "notif_orion.py", "self_check.py", "audit_otomatis.py",
    "workflow_engine.py",
]

core_dir = BACKUP / "core"
core_dir.mkdir(exist_ok=True)

count = 0
for f in FILE_INTI:
    for loc in [BASE / f, BASE / "py" / f]:
        if loc.exists():
            shutil.copy2(loc, core_dir / f)
            count += 1
            break

print(f"   ✅ {count} file inti")

# ============ 2. CONFIG ============
print("\n[2] CONFIG")
print("-" * 60)

config_dir = BACKUP / "config"
config_dir.mkdir(exist_ok=True)

for f in [".env", "SOUL.md", "SKILL.md", "config.json", "cron_tasks.json", "requirements.txt"]:
    loc = BASE / f
    if loc.exists():
        shutil.copy2(loc, config_dir / f)
        print(f"   ✅ {f}")

# ============ 3. SKILLS ============
print("\n[3] SKILLS")
print("-" * 60)

skills_src = BASE / "skills"
skills_dst = BACKUP / "skills"

if skills_src.exists():
    shutil.copytree(skills_src, skills_dst, dirs_exist_ok=True)
    
    # Hitung
    count = len([d for d in skills_dst.iterdir() if d.is_dir()])
    print(f"   ✅ {count} skill")

# ============ 4. DATABASE ============
print("\n[4] DATABASE")
print("-" * 60)

db_dir = BACKUP / "database"
db_dir.mkdir(exist_ok=True)

for db in [BASE / "memory" / str(BASE / "memory" / "orion.db")]:
    if db.exists():
        shutil.copy2(db, db_dir / db.name)
        size = db.stat().st_size
        print(f"   ✅ {db.name} ({size:,} B)")

# ============ 5. MEMORY & OUTPUT ============
print("\n[5] MEMORY & OUTPUT")
print("-" * 60)

for folder in ["memory", "output", "voice"]:
    src = BASE / folder
    if src.exists():
        dst = BACKUP / folder
        shutil.copytree(src, dst, dirs_exist_ok=True)
        count = len(list(dst.rglob("*")))
        print(f"   ✅ {folder}/ ({count} item)")

# ============ 6. SCRIPT & SCRIPT-MAKER ============
print("\n[6] SCRIPT")
print("-" * 60)

script_dir = BACKUP / "scripts"
script_dir.mkdir(exist_ok=True)

count = 0
for pattern in ["orion_*.py", "*.bat", "*.ps1"]:
    for f in BASE.glob(pattern):
        if f.is_file():
            shutil.copy2(f, script_dir / f.name)
            count += 1

print(f"   ✅ {count} script")

# ============ 7. DASHBOARD ============
print("\n[7] DASHBOARD")
print("-" * 60)

dash_src = Path("C:/Orion Dashboard")
if dash_src.exists():
    dash_dst = BACKUP / "dashboard"
    shutil.copytree(dash_src, dash_dst, dirs_exist_ok=True)
    
    # Hapus backup lama di dashboard
    for old in (dash_dst / "_backup").glob("*"):
        shutil.rmtree(old, ignore_errors=True)
    
    count = len(list(dash_dst.rglob("*")))
    print(f"   ✅ Dashboard ({count} item)")

# ============ 8. MANIFEST ============
print("\n[8] BIKIN MANIFEST")
print("-" * 60)

manifest = {
    "tanggal": TANGGAL,
    "base": str(BASE),
    "total_size": 0,
    "folders": {},
}

# Hitung total size
total_size = 0
for f in BACKUP.rglob("*"):
    if f.is_file():
        total_size += f.stat().st_size

manifest["total_size"] = total_size

# Hitung per folder
for d in BACKUP.iterdir():
    if d.is_dir():
        count = len(list(d.rglob("*")))
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        manifest["folders"][d.name] = {
            "files": count,
            "size": size,
        }

# Simpan manifest
manifest_file = BACKUP / "MANIFEST.json"
manifest_file.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False),
    encoding="utf-8"
)
print(f"   ✅ MANIFEST.json")

# ============ 9. LAPORAN ============
print("\n" + "=" * 60)
print("  LAPORAN BACKUP")
print("=" * 60)

print(f"\n📁 Lokasi: {BACKUP}")
print(f"📏 Total size: {total_size:,} B ({total_size/1024/1024:.2f} MB)")

print(f"\n📊 Per folder:")
for name, info in manifest["folders"].items():
    size_mb = info["size"] / 1024 / 1024
    print(f"   {name:15} : {info['files']:>5} file, {size_mb:.2f} MB")

print(f"\n✅ Backup selesai!")
print(f"📁 {BACKUP}")
print("=" * 60)
