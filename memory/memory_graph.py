import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent  # ROOT Orion
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

import sys
from pathlib import Path
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""memory_graph.py - Memory Graph untuk Orion."""
import sqlite3
from pathlib import Path

DB = _BASE / "memory" / str(_BASE / "memory" / str(_BASE / "memory" / "orion.db"))


def init_graph():
    """Bikin tabel memory_graph."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            relation TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence REAL DEFAULT 0.8,
            sumber TEXT DEFAULT 'chat',
            waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    return True


def tambah_relasi(subject, relation, object, confidence=0.8):
    """Tambah relasi."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memory_graph (subject, relation, object, confidence) VALUES (?, ?, ?, ?)",
        (subject, relation, object, confidence)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def cari_relasi(subject):
    """Cari relasi by subject."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("SELECT * FROM memory_graph WHERE subject=?", (subject,))
    rows = cur.fetchall()
    conn.close()
    return rows


def cari_relasi_object(object):
    """Cari relasi by object."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("SELECT * FROM memory_graph WHERE object=?", (object,))
    rows = cur.fetchall()
    conn.close()
    return rows


def cari_semua():
    """Cari semua relasi."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("SELECT * FROM memory_graph ORDER BY subject, relation")
    rows = cur.fetchall()
    conn.close()
    return rows


def hapus_relasi(id):
    """Hapus relasi."""
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("DELETE FROM memory_graph WHERE id=?", (id,))
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n > 0


def format_graph():
    """Format graph untuk tampilan."""
    semua = cari_semua()
    if not semua:
        return "Memory graph kosong."
    
    from collections import defaultdict
    by_subject = defaultdict(list)
    for r in semua:
        by_subject[r[1]].append(r)
    
    lines = []
    lines.append("=" * 50)
    lines.append("  MEMORY GRAPH")
    lines.append("=" * 50)
    
    for subject, relasi in by_subject.items():
        lines.append(f"\n📌 {subject}:")
        for r in relasi:
            lines.append(f"  → {r[2]} → {r[3]} ({r[4]:.1f})")
    
    lines.append("")
    lines.append(f"Total: {len(semua)} relasi")
    lines.append("=" * 50)
    return "\n".join(lines)


if __name__ == "__main__":
    init_graph()
    print("Memory graph initialized")
    print("Fungsi: init_graph, tambah_relasi, cari_relasi, cari_relasi_object, cari_semua, hapus_relasi, format_graph")
