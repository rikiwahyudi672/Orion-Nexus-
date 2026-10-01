import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
skill_loader.py - Baca skill ORION dengan progressive disclosure.
Kompatibel dengan format lama (*.md) dan format baru (*/SKILL.md).
"""
import re
from pathlib import Path

BASE = Path(__file__).parent
SKILLS_DIR = BASE / "."


def _parse_frontmatter(teks: str) -> dict:
    """Parse YAML frontmatter sederhana (tanpa library)."""
    hasil = {}
    match = re.match(r"^\ufeff?---\s*\r?\n(.*?)\r?\n---\s*\r?\n", teks, re.DOTALL)
    if not match:
        return hasil
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            hasil[key.strip()] = value.strip().strip('"').strip("'")
    return hasil


def _baca_skill_lama(path: Path) -> dict:
    """Baca skill format lama (*.md langsung di skills/)."""
    teks = path.read_text(encoding="utf-8")
    # Coba ekstrak nama dari "# Skill: [nama]"
    match = re.search(r"#\s*Skill:\s*(.+)", teks)
    nama = match.group(1).strip() if match else path.stem
    # Ambil deskripsi dari baris pertama setelah header
    deskripsi = ""
    for line in teks.split("\n"):
        if line.strip() and not line.startswith("#"):
            deskripsi = line.strip()[:200]
            break
    return {
        "nama": nama,
        "slug": path.stem,
        "deskripsi": deskripsi,
        "versi": "1.0.0",
        "format": "lama",
        "path": str(path),
        "tipe": "file",
    }


def _baca_skill_baru(folder: Path) -> dict:
    """Baca skill format baru (folder dengan SKILL.md)."""
    skill_file = folder / "SKILL.md"
    if not skill_file.exists():
        return None
    teks = skill_file.read_text(encoding="utf-8")
    meta = _parse_frontmatter(teks)
    return {
        "nama": meta.get("name", folder.name),
        "slug": folder.name,
        "deskripsi": meta.get("description", ""),
        "versi": meta.get("version", "1.0.0"),
        "format": "baru",
        "path": str(skill_file),
        "folder": str(folder),
        "tipe": "folder",
    }


def daftar_skill() -> list:
    """Daftar SEMUA skill (format lama + baru). Cuma metadata, hemat token."""
    hasil = []
    if not SKILLS_DIR.exists():
        return hasil

    # Format lama: file *.md langsung di skills/
    for f in SKILLS_DIR.glob("*.md"):
        if f.name == "SKILL.md":
            continue  # skip kalau ada di root
        hasil.append(_baca_skill_lama(f))

    # Format baru: folder dengan SKILL.md
    for folder in SKILLS_DIR.iterdir():
        if not folder.is_dir():
            continue
        skill = _baca_skill_baru(folder)
        if skill:
            hasil.append(skill)

    return hasil


# Sinonim untuk pencarian skill
SINONIM = {
    # Coding - prioritas tinggi
    "program": "coding-master",
    "coding": "coding-master",
    "kode": "coding-master",
    "code": "coding-master",
    "script": "coding-master",
    "aplikasi": "coding-master",
    "software": "coding-master",
    "fungsi": "coding-master",
    "class": "coding-master",
    "debug": "coding-master",
    "refactor": "coding-master",
    "excel": "xlsx",
    "xlsx": "xlsx",
    "spreadsheet": "xlsx",
    "word": "docx",
    "docx": "docx",
    "document": "docx",
    "powerpoint": "pptx",
    "ppt": "pptx",
    "pptx": "pptx",
    "presentasi": "pptx",
    "slide": "pptx",
    "pdf": "pdf",
    "wikipedia": "cari-wikipedia",
    "wiki": "cari-wikipedia",
    "reminder": "reminder",
    "ingatkan": "reminder",
    "pengingat": "reminder",
}


def _expand_query(query: str) -> set:
    """Expand query dengan sinonim."""
    kata = set(re.findall(r"\w+", query.lower()))
    tambahan = set()
    for k in kata:
        if k in SINONIM:
            tambahan.add(SINONIM[k])
    return kata | tambahan


def skill_relevan(query: str, limit: int = 3) -> list:
    """Cari skill relevan berdasarkan overlap kata + sinonim."""
    kata_query = _expand_query(query)
    hasil = []

    for skill in daftar_skill():
        skor = 0
        
        # 1. Cek nama skill (bobot tinggi)
        nama = skill.get("nama", "").lower()
        slug = skill.get("slug", "").lower()
        for k in kata_query:
            if k == nama or k == slug:
                skor += 20
            elif k in nama or k in slug:
                skor += 10
        
        # 2. Cek deskripsi (bobot sedang)
        deskripsi = skill.get("deskripsi", "").lower()
        kata_deskripsi = set(re.findall(r"\w+", deskripsi))
        skor += len(kata_query & kata_deskripsi) * 3
        
        # 3. Cek isi SKILL.md (bobot rendah, tapi tetap dihitung)
        try:
            path = Path(skill["path"])
            if path.exists():
                isi = path.read_text(encoding="utf-8").lower()
                for k in kata_query:
                    if len(k) > 3:  # skip kata pendek
                        skor += isi.count(k) * 1
        except Exception:
            pass
        
        if skor > 0:
            hasil.append((skill, skor))

    hasil.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in hasil[:limit]]


def load_skill(nama: str, level: int = 2) -> str:
    """
    Load skill dengan progressive disclosure.

    Level 1: cuma metadata (nama + deskripsi) - ~100 token
    Level 2: isi lengkap SKILL.md - ~5000 token
    Level 3: load file references/ juga
    """
    for skill in daftar_skill():
        if skill["slug"] == nama or skill["nama"].lower() == nama.lower():
            if level == 1:
                return f"[{skill['nama']}] {skill['deskripsi']}"
            elif level == 2:
                return Path(skill["path"]).read_text(encoding="utf-8")
            elif level == 3:
                # Load SKILL.md + semua file di references/
                teks = Path(skill["path"]).read_text(encoding="utf-8")
                if skill["tipe"] == "folder":
                    ref_dir = Path(skill["folder"]) / "references"
                    if ref_dir.exists():
                        for ref in ref_dir.rglob("*"):
                            if ref.is_file():
                                teks += f"\n\n=== {ref.name} ===\n"
                                teks += ref.read_text(encoding="utf-8")
                return teks
    return ""


def cek_status() -> str:
    skills = daftar_skill()
    lama = sum(1 for s in skills if s["format"] == "lama")
    baru = sum(1 for s in skills if s["format"] == "baru")
    return f"Skill: {len(skills)} total ({lama} lama, {baru} baru)"


def lihat_daftar() -> str:
    skills = daftar_skill()
    if not skills:
        return "Belum ada skill."
    teks = f"SKILL ORION ({len(skills)}):\n"
    for s in skills:
        teks += f"  - {s['nama']} (v{s['versi']}, {s['format']}): {s['deskripsi'][:80]}\n"
    return teks


__all__ = [
    "daftar_skill",
    "skill_relevan",
    "load_skill",
    "cek_status",
    "lihat_daftar",
]
