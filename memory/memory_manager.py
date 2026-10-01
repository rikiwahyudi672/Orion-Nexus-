import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
memory_manager.py - Manajemen memory ORION.
- Simpan chat
- Ambil konteks
- Ekstrak fakta
- Cari memory
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

_BASE = Path(__file__).parent
DB = _BASE / "orion.db"


def _conn():
    """Buka koneksi ke memory/orion.db."""
    import sqlite3
    from pathlib import Path
    _paths = [
        Path(__file__).parent.parent / "memory" / "orion.db",
        Path(__file__).parent / "orion.db",
        Path(__file__).parent.parent / "orion.db",
    ]
    for _p in _paths:
        if _p.exists():
            return sqlite3.connect(str(_p))
    return sqlite3.connect(str(_paths[0]))

def init():
    """Pastikan tabel ada."""
    conn = _conn()
    cur = conn.cursor()
    
    # Tabel chat
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_pesan TEXT,
            orion_pesan TEXT,
            waktu TEXT
        )
    """)
    
    # Tabel fakta
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fakta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            kategori TEXT,
            dibuat TEXT
        )
    """)
    
    # Index untuk pencarian cepat
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_waktu ON chat(waktu)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fakta_key ON fakta(key)")
    
    conn.commit()
    conn.close()


def simpan_chat(user_pesan, orion_pesan):
    """Simpan chat ke database."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat (user_pesan, orion_pesan, waktu) VALUES (?, ?, ?)",
            (user_pesan[:500], orion_pesan[:500], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[memory] Error simpan: " + str(e))
        return False


def ambil_konteks(jumlah=5):
    """Ambil chat terakhir untuk konteks - filter jawaban buruk."""
    try:
        conn = _conn()
        cur = conn.cursor()
        # Ambil lebih banyak - untuk filter
        cur.execute(
            "SELECT user_pesan, orion_pesan, waktu FROM chat ORDER BY id DESC LIMIT ?",
            (jumlah * 3,)
        )
        rows = cur.fetchall()
        conn.close()

        # Balik urutan - dari lama ke baru
        rows.reverse()

        # Filter jawaban buruk
        KATA_BURUK = [
            '"cd"', "kebanyakan cd", "cd ke folder", "udah cd",
            "cd tadi", "kebawa cd", "pindah folder", "masuk folder",
            "sudah berhasil dibuat", "sudah dibuat", "udah selesai",
            "file berhasil dibuat", "file sudah", "udah jadi",
        ]

        konteks = []
        for r in rows:
            user = r[0] or ""
            orion = r[1] or ""

            # Skip kalau ada kata buruk di orion
            if any(k in orion.lower() for k in KATA_BURUK):
                continue

            # Skip kalau user minta "cd"
            if any(k in user.lower() for k in ["cd ", 'cd"', '"cd']):
                continue

            # Skip kalau orion kosong
            if not orion.strip():
                continue

            konteks.append({
                "user": user,
                "orion": orion,
                "waktu": r[2],
            })

        # Ambil `jumlah` terakhir
        return konteks[-jumlah:]
    except Exception as e:
        return []


def cari_chat(keyword, limit=5):
    """Cari chat berdasarkan keyword."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_pesan, orion_pesan, waktu FROM chat WHERE user_pesan LIKE ? OR orion_pesan LIKE ? ORDER BY id DESC LIMIT ?",
            ("%" + keyword + "%", "%" + keyword + "%", limit)
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def simpan_fakta(key, value, kategori="umum"):
    """Simpan fakta."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO fakta (key, value, kategori, dibuat) VALUES (?, ?, ?, ?)",
            (key, value, kategori, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def ambil_fakta(key):
    """Ambil fakta."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM fakta WHERE key = ?", (key,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def semua_fakta():
    """Ambil semua fakta."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT key, value, kategori FROM fakta")
        rows = cur.fetchall()
        conn.close()
        return [{"key": r[0], "value": r[1], "kategori": r[2]} for r in rows]
    except Exception:
        return []


def cleanup_chat(hari=30):
    """Hapus chat lama > 30 hari."""
    try:
        batas = (datetime.now() - timedelta(days=hari)).isoformat()
        conn = _conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat WHERE waktu < ?", (batas,))
        count = cur.rowcount
        conn.commit()
        conn.close()
        return count
    except Exception:
        return 0


def cek_status():
    """Cek status memory."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chat")
        chat = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM fakta")
        fakta = cur.fetchone()[0]
        conn.close()
        return "Memory: " + str(chat) + " chat, " + str(fakta) + " fakta"
    except Exception:
        return "Memory: error"


if __name__ == "__main__":
    print("=== Test memory_manager ===")
    init()
    print(cek_status())
    
    # Test simpan
    simpan_chat("halo orion", "Halo juga, Rik!")
    simpan_chat("bikin folder test", "Folder test dibuat")
    print(cek_status())
    
    # Test ambil konteks
    print()
    print("=== Konteks terakhir ===")
    for k in ambil_konteks(3):
        print("  User: " + k["user"])
        print("  Orion: " + k["orion"])
        print()
    
    # Test cari
    print("=== Cari 'folder' ===")
    for r in cari_chat("folder"):
        print("  " + str(r[0]))
    
    # Test fakta
    simpan_fakta("nama", "Riki Wahyudi", "profil")
    print()
    print("Fakta nama: " + str(ambil_fakta("nama")))


# ============ MEMORI PANJANG (Level 12) ============

def simpan_chat_panjang(user_pesan, orion_pesan, topik=None, emosi=None, penting=False):
    """Simpan chat dengan metadata (topik, emosi, penting)."""
    init()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat (user_pesan, orion_pesan, waktu, topik, emosi, penting) VALUES (?, ?, ?, ?, ?, ?)",
        (user_pesan, orion_pesan, datetime.now().isoformat(), topik, emosi, 1 if penting else 0)
    )
    conn.commit()
    conn.close()


def cari_chat_panjang(keyword, limit=10):
    """Cari chat by keyword (di user_pesan atau orion_pesan)."""
    init()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_pesan, orion_pesan, waktu, topik, emosi, penting FROM chat "
        "WHERE user_pesan LIKE ? OR orion_pesan LIKE ? "
        "ORDER BY waktu DESC LIMIT ?",
        (f"%{keyword}%", f"%{keyword}%", limit)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def ambil_penting(limit=10):
    """Ambil chat yang ditandai penting."""
    init()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_pesan, orion_pesan, waktu, topik, emosi FROM chat "
        "WHERE penting = 1 ORDER BY waktu DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def ringkasan_memori_panjang(jumlah=15):
    """Ringkasan memori panjang untuk prompt LLM."""
    init()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_pesan, orion_pesan, waktu, topik, emosi, penting FROM chat "
        "ORDER BY waktu DESC LIMIT ?",
        (jumlah,)
    )
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        return "Belum ada memori."
    
    lines = ["MEMORI JANGKA PANJANG:"]
    for r in reversed(rows):
        waktu = r[2][:16].replace("T", " ") if r[2] else "?"
        topik_str = f" [{r[3]}]" if r[3] else ""
        emosi_str = f" ({r[4]})" if r[4] else ""
        penting_str = " ⭐" if r[5] else ""
        lines.append(f"[{waktu}]{topik_str}{emosi_str}{penting_str}")
        lines.append(f"  Rik: {r[0][:80]}")
        lines.append(f"  Orion: {r[1][:80]}")
    
    return "\n".join(lines)
