import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""lihat_memory.py - Lihat chat terakhir di orion.db."""
import sqlite3

conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
cur = conn.cursor()

# Cek tabel
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tabel:", [t[0] for t in tables])
print()

# Lihat 10 chat terakhir
cur.execute("SELECT id, user_pesan, orion_pesan, waktu FROM chat ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()

print(f"Total 10 chat terakhir:")
print("=" * 60)
for r in rows:
    print(f"ID: {r[0]} | Waktu: {r[3]}")
    print(f"User: {r[1][:100]}")
    print(f"Orion: {r[2][:150]}")
    print("-" * 60)

conn.close()
