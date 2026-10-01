import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
skill_evo.py - Self-improving skill loop untuk ORION.
"""
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
SKILLS_DIR = BASE / "skills"
SKILLS_DIR.mkdir(exist_ok=True)

_session_trace = []
_MIN_TOOLS_FOR_SKILL = 2


def catat_langkah(tool, args, hasil):
    _session_trace.append({
        "tool": tool,
        "args": args,
        "hasil": str(hasil)[:300],
        "waktu": datetime.now().isoformat(),
    })


def reset_trace():
    global _session_trace
    _session_trace = []


def trace_kompleks():
    return len(_session_trace) >= _MIN_TOOLS_FOR_SKILL


def daftar_skill():
    return [f.stem for f in SKILLS_DIR.glob("*.md")]


def skill_relevan(query, limit=3):
    query_lower = query.lower()
    hasil = []
    for f in SKILLS_DIR.glob("*.md"):
        teks = f.read_text(encoding="utf-8").lower()
        kata_query = set(re.findall(r"\w+", query_lower))
        kata_skill = set(re.findall(r"\w+", teks))
        overlap = len(kata_query & kata_skill)
        if overlap > 0:
            hasil.append((f.stem, overlap))
    hasil.sort(key=lambda x: x[1], reverse=True)
    return [nama for nama, _ in hasil[:limit]]


def load_skill(nama):
    p = SKILLS_DIR / f"{nama}.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def distill_dan_simpan(prompt_user, jawaban_final, llm_func):
    if not trace_kompleks():
        return None
    trace_teks = "\n".join([
        f"- {t['tool']}({t['args']}) -> {t['hasil'][:100]}"
        for t in _session_trace
    ])
    prompt_distill = (
        "Kamu adalah Orion, asisten AI. Baru saja kamu menyelesaikan task untuk Riki.\n\n"
        f"Task user: {prompt_user}\n"
        f"Jawaban akhir: {jawaban_final[:500]}\n\n"
        f"Langkah-langkah yang kamu lakukan:\n{trace_teks}\n\n"
        "Tugas kamu: Buat file SKILL.md yang mendokumentasikan CARA menyelesaikan task ini, "
        "supaya lain kali kamu bisa langsung eksekusi tanpa mikir dari nol.\n\n"
        "Format SKILL.md:\n"
        "# Skill: [nama-skill-singkat]\n\n"
        "## Kapan dipakai\n"
        "[deskripsi kondisi/query yang memicu skill ini]\n\n"
        "## Langkah\n"
        "[langkah-langkah konkret]\n\n"
        "## Contoh\n"
        "[contoh query dan hasil]\n\n"
        "Buat HANYA isi SKILL.md, tanpa penjelasan tambahan."
    )
    try:
        skill_md = llm_func(prompt_distill)
        if not skill_md or len(skill_md) < 50:
            return None
        match = re.search(r"#\s*Skill:\s*(.+)", skill_md)
        if match:
            nama = match.group(1).strip().lower()
            nama = re.sub(r"[^a-z0-9]+", "_", nama)
            nama = nama.strip("_")[:40]
        else:
            nama = f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        p = SKILLS_DIR / f"{nama}.md"
        p.write_text(skill_md, encoding="utf-8")
        return nama
    except Exception as e:
        print(f"[skill_evo] Gagal distill: {e}")
        return None


def distill_dan_simpan_v2(prompt_user, jawaban_final, llm_func):
    """
    Versi baru: simpan skill dalam format folder + frontmatter.
    Kompatibel dengan skill_loader & skill_reviewer.
    """
    if not trace_kompleks():
        return None
    
    trace_teks = "\n".join([
        f"- {t['tool']}({t['args']}) -> {t['hasil'][:100]}"
        for t in _session_trace
    ])
    
    prompt_distill = (
        "Kamu adalah Orion, asisten AI. Baru saja kamu menyelesaikan task untuk Riki.\n\n"
        f"Task user: {prompt_user}\n"
        f"Jawaban akhir: {jawaban_final[:500]}\n\n"
        f"Langkah-langkah yang kamu lakukan:\n{trace_teks}\n\n"
        "Tugas kamu: Buat file SKILL.md dengan format frontmatter YAML + Markdown.\n\n"
        "Format WAJIB:\n"
        "---\n"
        "name: [nama-skill-singkat]\n"
        "description: [1 kalimat deskripsi kapan skill ini dipakai]\n"
        "version: 1.0.0\n"
        "author: Orion\n"
        "---\n\n"
        "# [Judul Skill]\n\n"
        "## Kapan Digunakan\n"
        "- [kondisi 1]\n"
        "- [kondisi 2]\n\n"
        "## Prosedur\n"
        "1. [langkah 1]\n"
        "2. [langkah 2]\n"
        "3. [langkah 3]\n\n"
        "## Contoh\n"
        "[contoh query dan hasil]\n\n"
        "Buat HANYA isi SKILL.md, tanpa penjelasan tambahan."
    )
    
    try:
        skill_md = llm_func(prompt_distill)
        if not skill_md or len(skill_md) < 50:
            return None
        
        # Extract nama dari frontmatter
        import re as _re
        match = _re.search(r"name:\s*(.+)", skill_md)
        if match:
            nama = match.group(1).strip()
        else:
            # Fallback: cari di "# [Judul]"
            match2 = _re.search(r"#\s*(.+)", skill_md)
            nama = match2.group(1).strip() if match2 else f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Slugify
        slug = _re.sub(r"[^a-z0-9]+", "-", nama.lower()).strip("-")[:50]
        if not slug:
            slug = f"skill-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Bikin folder + SKILL.md
        folder = SKILLS_DIR / slug
        folder.mkdir(exist_ok=True)
        skill_file = folder / "SKILL.md"
        skill_file.write_text(skill_md, encoding="utf-8")
        
        print(f"[skill_evo] Skill baru (format baru): {slug}")
        return slug
    except Exception as e:
        print(f"[skill_evo] Gagal distill v2: {e}")
        return None


def kurasi_skill(max_umur_hari=30):
    import time
    sekarang = time.time()
    dihapus = []
    for f in SKILLS_DIR.glob("*.md"):
        umur_hari = (sekarang - f.stat().st_mtime) / 86400
        if umur_hari > max_umur_hari:
            f.unlink()
            dihapus.append(f.stem)
    return dihapus


if __name__ == "__main__":
    print("=== Test skill_evo ===")
    print(f"Skills dir: {SKILLS_DIR}")
    print(f"Skill existing: {daftar_skill()}")
    print(f"Skill relevan 'cari': {skill_relevan('cari tokoh')}")