import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
memory_orion.py - Modul memori + personality untuk ORION.
"""
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "memory" / str(BASE / "memory" / "orion.db")
SOUL_FILE = BASE / "SOUL.md"


def get_soul() -> str:
    """Baca SOUL.md, kembalikan string kosong kalau tidak ada."""
    if SOUL_FILE.exists():
        return SOUL_FILE.read_text(encoding="utf-8")
    return ""


def _conn():
    return sqlite3.connect(DB)


def simpan_memori(topik: str, isi: str, penting: int = 0):
    """Simpan satu memori ke agent_memory."""
    with _conn() as c:
        c.execute(
            "INSERT INTO agent_memory (topik, isi, penting) VALUES (?, ?, ?)",
            (topik, isi[:500], penting),
        )


def ambil_memori(kata_kunci: str = "", limit: int = 5):
    """Ambil memori relevan (FTS5 + fallback LIKE)."""
    with _conn() as c:
        if kata_kunci:
            try:
                cur = c.execute(
                    "SELECT m.topik, m.isi FROM agent_memory_fts fts "
                    "JOIN agent_memory m ON m.id = fts.rowid "
                    "WHERE agent_memory_fts MATCH ? "
                    "ORDER BY rank LIMIT ?",
                    (kata_kunci, limit),
                )
                hasil = cur.fetchall()
                if hasil:
                    return hasil
            except Exception:
                pass
            cur = c.execute(
                "SELECT topik, isi FROM agent_memory "
                "WHERE topik LIKE ? OR isi LIKE ? "
                "ORDER BY penting DESC, created_at DESC LIMIT ?",
                (f"%{kata_kunci}%", f"%{kata_kunci}%", limit),
            )
        else:
            cur = c.execute(
                "SELECT topik, isi FROM agent_memory "
                "ORDER BY penting DESC, created_at DESC LIMIT ?",
                (limit,),
            )
        return cur.fetchall()


def set_profile(key: str, value: str):
    """Set profil user (key-value)."""
    with _conn() as c:
        c.execute(
            "INSERT INTO user_profile (key, value, updated_at) "
            "VALUES (?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(key) DO UPDATE SET "
            "value=excluded.value, updated_at=CURRENT_TIMESTAMP",
            (key, value),
        )


def get_profile(key: str):
    with _conn() as c:
        cur = c.execute("SELECT value FROM user_profile WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None


def load_skill(nama: str) -> str:
    """Load skill dari folder skills/."""
    p = BASE / "skills" / f"{nama}.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


if __name__ == "__main__":
    print("=== Test memory_orion.py ===")
    print("SOUL ada:", bool(get_soul()))
    simpan_memori("test", "Ini memori percobaan dari terminal.", penting=0)
    print("Memori terakhir:", ambil_memori("test", limit=1))
    set_profile("nama_panggilan", "Riki")
    print("Profil nama_panggilan:", get_profile("nama_panggilan"))
    print("Skill cek_sistem ada:", bool(load_skill("cek_sistem")))
    print("OK.")
