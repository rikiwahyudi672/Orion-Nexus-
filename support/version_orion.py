import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
version_orion.py - Versi ORION.
"""
__version__ = "2.7"
__codename__ = "Unified Edition"
__pencipta__ = "Riki Wahyudi"
__tanggal__ = "2026-09-26"

INFO = {
    "versi": __version__,
    "codename": __codename__,
    "pencipta": __pencipta__,
    "tanggal": __tanggal__,
    "fitur": [
        "Dashboard modern + logo berwarna",
        "500 variasi suara Ardi + 14 emosi",
        "Mood + emotional state + empati",
        "Loyalty + identity anchor",
        "Memori FTS5 + event + narrative",
        "Multi-agent Commander + 5 agent",
        "Auto-distill skill + dedup",
        "Cron LLM + TTS + maintenance",
        "Background 24/7 + auto-restart",
        "Personality: hobi, mimpi, ngeluh, nangis, playlist",
        "Monitor aktivitas laptop",
        "Backup otomatis + health check",
    ],
}


def info_lengkap():
    """Info lengkap Orion."""
    lines = [
        f"🤖 ORION v{INFO['versi']} ({INFO['codename']})",
        f"👤 Pencipta: {INFO['pencipta']}",
        f"📅 Tanggal: {INFO['tanggal']}",
        "",
        "Fitur:",
    ]
    for i, f in enumerate(INFO["fitur"], 1):
        lines.append(f"  {i}. {f}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(info_lengkap())
