import sys
from pathlib import Path
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

import orion_tool_loop as otl

# Manual scan
folders = sorted([f for f in otl.SKILL_DIR.iterdir() if f.is_dir() and not f.name.startswith((".", "__"))])
print(f"Folder valid: {len(folders)}")
print()

manual = {}
for f in folders:
    if not (f / "SKILL.md").exists():
        continue
    tool_name = f.name.replace("-", "_")
    try:
        fn = otl._load_jalankan(f)
        if fn is None:
            print(f"  [skip-None] {f.name}")
            continue
        manual[tool_name] = f.name
    except Exception as e:
        print(f"  [skip-err] {f.name}: {e}")
        continue

print(f"Manual: {len(manual)}")
print()

# Registry
reg = otl.bangun_registry()
print(f"Registry: {len(reg)}")
print()

# Cek script_maker
print(f"script_maker di manual: {'script_maker' in manual}")
print(f"script_maker di registry: {'script_maker' in reg}")
print()

# Beda
print("=== Beda ===")
manual_set = set(manual.keys())
reg_set = set(reg.keys())
print(f"Manual - Registry: {manual_set - reg_set}")
print(f"Registry - Manual: {reg_set - manual_set}")

# Cek apakah script_maker di registry dengan nama lain
for name in reg.keys():
    if 'script' in name.lower() or 'maker' in name.lower():
        print(f"  Found di registry: {name}")
