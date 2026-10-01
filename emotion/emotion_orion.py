"""emotion_orion.py - Emosi Orion."""
import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

import sqlite3
from datetime import datetime


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


def init_db():
    """Inisialisasi tabel emotion."""
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS emotion_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_emosi TEXT DEFAULT 'kalem',
                primary_intensity INTEGER DEFAULT 5,
                secondary_emosi TEXT,
                secondary_intensity INTEGER DEFAULT 0,
                last_event_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.commit()
        
        # Insert default kalau kosong
        c.execute("SELECT COUNT(*) FROM emotion_state")
        if c.fetchone()[0] == 0:
            c.execute("""
                INSERT INTO emotion_state (primary_emosi, primary_intensity)
                VALUES ('kalem', 5)
            """)
            c.commit()


def get_emotion():
    """Ambil emosi sekarang."""
    try:
        init_db()
        with _conn() as c:
            cur = c.execute("SELECT primary_emosi, primary_intensity, secondary_emosi, secondary_intensity, updated_at FROM emotion_state WHERE id=1")
            row = cur.fetchone()
            if not row:
                return {"primary": "kalem", "primary_intensity": 5, "secondary": None, "secondary_intensity": 0}
            return {
                "primary": row[0],
                "primary_intensity": row[1],
                "secondary": row[2],
                "secondary_intensity": row[3],
                "updated_at": row[4],
            }
    except Exception:
        return {"primary": "kalem", "primary_intensity": 5, "secondary": None, "secondary_intensity": 0}


def set_emotion(primary, intensity=5, secondary=None, secondary_intensity=0):
    """Set emosi."""
    try:
        init_db()
        with _conn() as c:
            c.execute("SELECT COUNT(*) FROM emotion_state")
            if c.fetchone()[0] == 0:
                c.execute("""
                    INSERT INTO emotion_state (primary_emosi, primary_intensity, secondary_emosi, secondary_intensity)
                    VALUES (?, ?, ?, ?)
                """, (primary, intensity, secondary, secondary_intensity))
            else:
                c.execute("""
                    UPDATE emotion_state SET primary_emosi=?, primary_intensity=?, secondary_emosi=?, secondary_intensity=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=1
                """, (primary, intensity, secondary, secondary_intensity))
            c.commit()
        return True
    except Exception:
        return False


def deteksi_event(teks):
    """Deteksi event dari teks."""
    teks_lower = teks.lower()
    if any(k in teks_lower for k in ["sedih", "capek", "stres"]):
        return "sedih"
    if any(k in teks_lower for k in ["senang", "happy", "bagus"]):
        return "senang"
    if any(k in teks_lower for k in ["marah", "kesal", "ngamuk"]):
        return "marah"
    return None


def prompt_modifier():
    """Modifier prompt berdasarkan emosi."""
    emo = get_emotion()
    primary = emo.get("primary", "netral")
    intensity = emo.get("primary_intensity", 5)
    if intensity >= 7:
        return f"Emosi kamu SEKARANG: {primary} (KUAT). Tunjukkan ini di nada bicara."
    return f"Emosi kamu sekarang: {primary}."


def get_relationship():
    """Ambil relationship."""
    return {"user": "Rik", "level": 1, "trust": 50}


def event_terakhir(limit=3):
    """Event terakhir."""
    return []
