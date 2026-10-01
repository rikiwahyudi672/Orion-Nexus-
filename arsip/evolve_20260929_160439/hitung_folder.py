import sys
from pathlib import Path
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import SKILL_DIR

print(f"SKILL_DIR: {SKILL_DIR}")
print(f"Exists: {SKILL_DIR.is_dir()}")
print()

folders = [f for f in SKILL_DIR.iterdir() if f.is_dir() and not f.name.startswith((".", "__"))]
print(f"Total folder: {len(folders)}")
print()

# Cek 5 folder pertama
for f in sorted(folders)[:5]:
    skill_md = f / "SKILL.md"
    py_files = list(f.glob("*.py"))
    print(f"  {f.name}:")
    print(f"    SKILL.md: {skill_md.exists()}")
    print(f"    .py: {[p.name for p in py_files]}")
