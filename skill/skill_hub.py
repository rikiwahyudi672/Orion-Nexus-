import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))


'''skill_hub.py - Hub semua skill Orion.'''

import importlib
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
SKILLS_DIR = BASE.parent / "skills"


def daftar_semua_skill():
    '''Daftar semua skill yang tersedia.'''
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    
    for folder in SKILLS_DIR.iterdir():
        if folder.is_dir():
            skill_md = folder / "SKILL.md"
            if skill_md.exists():
                skills.append({
                    "nama": folder.name,
                    "path": str(folder),
                    "skill_md": str(skill_md),
                    "size": skill_md.stat().st_size,
                })
    return skills


def baca_skill(nama):
    '''Baca isi SKILL.md.'''
    skill_md = SKILLS_DIR / nama / "SKILL.md"
    if skill_md.exists():
        return skill_md.read_text(encoding="utf-8")
    return None


def jalankan_skill(nama, *args, **kwargs):
    '''Jalankan skill.'''
    # Coba import dari folder skill
    skill_folder = SKILLS_DIR / nama
    
    if not skill_folder.exists():
        return {"sukses": False, "error": f"Skill {nama} tidak ada"}
    
    # Cari file .py
    py_files = list(skill_folder.glob("*.py"))
    if not py_files:
        return {"sukses": False, "error": f"Skill {nama} tidak punya file .py"}
    
    # Import
    import sys
    sys.path.insert(0, str(skill_folder))
    
    try:
        modul = importlib.import_module(py_files[0].stem)
        return {"sukses": True, "modul": modul}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def status_semua_skill():
    '''Status semua skill.'''
    skills = daftar_semua_skill()
    hasil = []
    
    for s in skills:
        # Cek - ada file .py?
        skill_folder = SKILLS_DIR / s["nama"]
        py_files = list(skill_folder.glob("*.py"))
        
        hasil.append({
            "nama": s["nama"],
            "ada_skill_md": True,
            "ada_py": len(py_files) > 0,
            "jumlah_py": len(py_files),
            "size_md": s["size"],
        })
    
    return hasil


if __name__ == "__main__":
    print("=== SKILL HUB ===")
    skills = daftar_semua_skill()
    print(f"Total skill: {len(skills)}")
    
    for s in skills:
        print(f"  - {s['nama']} ({s['size']} char)")
    
    print()
    print("=== STATUS ===")
    status = status_semua_skill()
    for s in status:
        print(f"  {s['nama']}: MD={s['ada_skill_md']}, PY={s['ada_py']} ({s['jumlah_py']})")
