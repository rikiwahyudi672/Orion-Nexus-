import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""cek_chat_memory.py"""
import sqlite3

conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
cur = conn.cursor()

cur.execute("SELECT id, user_pesan, orion_pesan, waktu FROM chat ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()

print(f"Total chat: {len(rows)}")
print("=" * 60)
for r in rows:
    print(f"ID: {r[0]} | {r[3]}")
    print(f"User: {r[1][:150]}")
    print(f"Orion: {r[2][:150]}")
    print("-" * 60)

conn.close()
