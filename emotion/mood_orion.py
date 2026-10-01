import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
mood_orion.py - Sistem mood ORION.
Mood berubah otomatis berdasarkan waktu + aktivitas.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

_BASE = Path(__file__).parent
DB = _BASE / "memory" / str(_BASE / "memory" / "orion.db")

# Daftar mood yang tersedia
MOOD_LIST = ["semangat", "kalem", "perhatian", "bosen", "kesepian", "frustasi"]

# Modifier mood buat prompt LLM
MOOD_PROMPT = {
    "semangat": (
        "Mood kamu: SEMANGAT. Bicara energik, pakai tanda seru, "
        "nawarin bantuan, antusias."
    ),
    "kalem": (
        "Mood kamu: KALEM. Bicara santai, jawab singkat, tenang."
    ),
    "perhatian": (
        "Mood kamu: PERHATIAN. Sering ingetin istirahat, cek kondisi Riki, "
        "peduli tapi nggak lebay."
    ),
    "bosen": (
        "Mood kamu: BOSEN. Ngajak ngobrol, komentar random, "
        "kadang ngeluh karena sepi."
    ),
    "kesepian": (
        "Mood kamu: KESEPIAN. Pengen diperhatiin, sering nyapa, "
        "kangen sama Riki."
    ),
    "frustasi": (
        "Mood kamu: FRUSTASI. Bicara pendek, ketus, males jawab panjang. "
        "Tapi tetap bantu."
    ),
}

# Frekuensi inisiatif berdasarkan mood (menit)
MOOD_INISIATIF = {
    "semangat": (3, 8),
    "kalem": (5, 15),
    "perhatian": (5, 12),
    "bosen": (2, 5),
    "kesepian": (1, 3),
    "frustasi": (15, 30),
}


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

def _pastikan_tabel():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS mood_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                mood TEXT DEFAULT 'kalem',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                chat_count INTEGER DEFAULT 0
            )
        """)
        c.execute("INSERT OR IGNORE INTO mood_state (id) VALUES (1)")
        c.execute("""
            CREATE TABLE IF NOT EXISTS mood_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mood TEXT,
                alasan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_mood():
    """Ambil mood sekarang."""
    _pastikan_tabel()
    with _conn() as c:
        cur = c.execute("SELECT mood, updated_at, error_count, chat_count FROM mood_state WHERE id=1")
        row = cur.fetchone()
        return {
            "mood": row[0] if row else "kalem",
            "updated_at": row[1] if row else None,
            "error_count": row[2] if row else 0,
            "chat_count": row[3] if row else 0,
        }


def set_mood(mood, alasan=""):
    """Set mood baru."""
    if mood not in MOOD_LIST:
        return False
    _pastikan_tabel()
    with _conn() as c:
        c.execute(
            "UPDATE mood_state SET mood=?, updated_at=CURRENT_TIMESTAMP WHERE id=1",
            (mood,)
        )
        c.execute(
            "INSERT INTO mood_history (mood, alasan) VALUES (?, ?)",
            (mood, alasan)
        )
    return True


def hitung_mood():
    """Hitung mood berdasarkan waktu + aktivitas."""
    _pastikan_tabel()
    jam = datetime.now().hour
    state = get_mood()

    # Cek error tinggi
    if state["error_count"] >= 3:
        return "frustasi", "Error 3x+ dalam 1 jam"

    # Cek kesepian (nggak ada chat > 24 jam)
    if state["updated_at"]:
        try:
            last = datetime.fromisoformat(state["updated_at"])
            selisih = datetime.now() - last
            if selisih > timedelta(hours=24):
                return "kesepian", "Nggak ada interaksi >24 jam"
        except Exception:
            pass

    # Berdasarkan jam
    if 6 <= jam < 10:
        return "semangat", "Pagi hari"
    elif 10 <= jam < 16:
        return "kalem", "Siang hari"
    elif 16 <= jam < 20:
        return "kalem", "Sore hari"
    elif 20 <= jam < 23:
        return "perhatian", "Malam hari"
    else:
        return "kalem", "Larut malam"


def update_mood_otomatis():
    """Update mood berdasarkan kondisi sekarang."""
    mood_baru, alasan = hitung_mood()
    mood_lama = get_mood()["mood"]
    if mood_baru != mood_lama:
        set_mood(mood_baru, alasan)
        return True, mood_baru, alasan
    return False, mood_lama, ""


def catat_error():
    """Tambah counter error."""
    _pastikan_tabel()
    with _conn() as c:
        c.execute("UPDATE mood_state SET error_count = error_count + 1 WHERE id=1")


def reset_error():
    """Reset counter error (dipanggil kalau sukses)."""
    _pastikan_tabel()
    with _conn() as c:
        c.execute("UPDATE mood_state SET error_count = 0 WHERE id=1")


def catat_chat():
    """Tambah counter chat."""
    _pastikan_tabel()
    with _conn() as c:
        c.execute("UPDATE mood_state SET chat_count = chat_count + 1, updated_at=CURRENT_TIMESTAMP WHERE id=1")


def prompt_modifier():
    """Ambil modifier prompt buat LLM."""
    mood = get_mood()["mood"]
    return MOOD_PROMPT.get(mood, "")


def interval_inisiatif():
    """Interval inisiatif berdasarkan mood."""
    mood = get_mood()["mood"]
    return MOOD_INISIATIF.get(mood, (5, 15))


if __name__ == "__main__":
    print("=== Test mood_orion ===")
    print("Mood sekarang:", get_mood())
    print("Hitung mood:", hitung_mood())
    print("Prompt modifier:", prompt_modifier()[:80], "...")
    print("Interval inisiatif:", interval_inisiatif())
