import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
konsolidasi_memory.py - Ringkas chat lama jadi fakta.
Jalan tiap 7 hari.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent
DB = (BASE / "orion.db") if BASE.name == "memory" else (BASE / "memory" / "orion.db")  # DB live: memory/orion.db (betulkan_konsolidasi_v2 30/09)


def _conn():
    """Buka koneksi ke orion.db live (memory/orion.db). (betulkan_konsolidasi_v2 30/09)"""
    from pathlib import Path as _P
    _b = _P(__file__).parent
    _mem = _b if _b.name == "memory" else _b / "memory"
    _root = _b.parent if _b.name == "memory" else _b
    for _p in [_mem / "orion.db", _root / "orion.db"]:
        if _p.exists():
            return sqlite3.connect(str(_p))
    return sqlite3.connect(str(_mem / "orion.db"))


def konsolidasi():
    """Ringkas chat > 7 hari jadi fakta."""
    batas = (datetime.now() - timedelta(days=7)).isoformat()
    
    conn = _conn()
    cur = conn.cursor()
    
    # Ambil chat lama
    cur.execute("SELECT user_pesan, orion_pesan FROM chat WHERE waktu < ? LIMIT 50", (batas,))
    rows = cur.fetchall()
    
    if not rows:
        conn.close()
        print("[konsolidasi] Tidak ada chat lama")
        return 0
    
    # Gabung teks
    teks_gabung = " | ".join([r[0][:100] + " -> " + r[1][:100] for r in rows])
    
    # Simpan sebagai fakta
    cur.execute("""
        INSERT OR REPLACE INTO fakta (key, value, kategori, dibuat)
        VALUES (?, ?, ?, ?)
    """, (
        "ringkasan_" + datetime.now().strftime("%Y%m%d_%H%M"),
        teks_gabung[:3000],
        "konsolidasi",
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    print("[konsolidasi] " + str(len(rows)) + " chat dikonsolidasi")
    return len(rows)


def hapus_chat_lama(hari=30):
    """Hapus chat > 30 hari setelah konsolidasi."""
    batas = (datetime.now() - timedelta(days=hari)).isoformat()
    
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat WHERE waktu < ?", (batas,))
    count = cur.rowcount
    conn.commit()
    conn.close()
    print("[konsolidasi] " + str(count) + " chat lama dihapus")
    return count


if __name__ == "__main__":
    print("=== Konsolidasi memory ===")
    konsolidasi()
    hapus_chat_lama(30)
    print("Selesai!")


def konsolidasi_jika_perlu(hari=7):
    """Jalankan konsolidasi kalau terakhir kali > hari. Fail-safe."""
    try:
        import time
        from pathlib import Path as _P
        _stamp = _P(__file__).parent / ".konsolidasi_terakhir"
        now = time.time()
        if _stamp.exists():
            try:
                if now - float(_stamp.read_text().strip()) < hari * 86400:
                    return 0
            except Exception:
                pass
        hasil = konsolidasi()
        try:
            _stamp.write_text(str(now))
        except Exception:
            pass
        return hasil
    except Exception as e:
        print("[konsolidasi] skip: " + str(e))
        return 0
