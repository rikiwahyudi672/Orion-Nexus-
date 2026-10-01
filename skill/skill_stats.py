import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
skill_stats.py - Catat & ambil statistik pemakaian skill.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
DB = Path(__file__).parent.parent / "memory" / "orion.db"


def _conn():
    return sqlite3.connect(str(DB))


def catat_pemakaian(skill_name: str, sukses: bool = True, catatan: str = ""):
    """Catat pemakaian skill."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO skill_log (skill_name, sukses, catatan, created_at) VALUES (?, ?, ?, ?)",
            (skill_name, 1 if sukses else 0, catatan[:200], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[skill_stats] Error: " + str(e))
        return False


def get_stats(skill_name: str) -> dict:
    """Ambil statistik 1 skill."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*), SUM(sukses) FROM skill_log WHERE skill_name = ?",
            (skill_name,)
        )
        row = cur.fetchone()
        total = row[0] or 0
        sukses = row[1] or 0
        gagal = total - sukses
        conn.close()
        return {
            "skill_name": skill_name,
            "total": total,
            "sukses": sukses,
            "gagal": gagal,
        }
    except Exception as e:
        return {"skill_name": skill_name, "total": 0, "sukses": 0, "gagal": 0, "error": str(e)}


def get_semua_stats() -> dict:
    """Ambil statistik semua skill."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT skill_name, COUNT(*), SUM(sukses) FROM skill_log GROUP BY skill_name"
        )
        rows = cur.fetchall()
        conn.close()
        hasil = {}
        for r in rows:
            nama = r[0]
            total = r[1] or 0
            sukses = r[2] or 0
            hasil[nama] = {
                "total": total,
                "sukses": sukses,
                "gagal": total - sukses,
            }
        return hasil
    except Exception as e:
        return {}


def hitung_skor(skill_name: str) -> int:
    """Hitung skor kontribusi."""
    s = get_stats(skill_name)
    skor = (s["total"] * 2) + (s["sukses"] * 3) - (s["gagal"] * 1)
    return max(0, skor)


if __name__ == "__main__":
    print("=== Test skill_stats ===")
    catat_pemakaian("buat-pdf", True, "test")
    catat_pemakaian("buat-pdf", True, "test 2")
    catat_pemakaian("cari-wikipedia", False, "gagal")
    print("Stats buat-pdf:", get_stats("buat-pdf"))
    print("Stats cari-wikipedia:", get_stats("cari-wikipedia"))
    print("Skor buat-pdf:", hitung_skor("buat-pdf"))
    print("Semua stats:", get_semua_stats())
