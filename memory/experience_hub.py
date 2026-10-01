import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent  # ROOT Orion
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
experience_hub.py - Saraf Pengalaman Orion.
Catat pengalaman, belajar dari sukses/gagal.
"""
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = _BASE / "memory" / str(_BASE / "memory" / "orion.db")


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
    """Bikin tabel experience kalau belum ada."""
    conn = _conn()
    with conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                pesan TEXT,
                hasil_sukses INTEGER DEFAULT 0,
                langkah TEXT,
                error TEXT,
                tools TEXT,
                waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_exp_intent ON experience(intent)")
    conn.commit()
    conn.close()


def catat_pengalaman(pesan, intent, hasil, tools=None):
    """
    Catat pengalaman setelah eksekusi.
    
    Args:
        pesan: pesan user
        intent: intent (coding, scan, fix, dll)
        hasil: dict hasil eksekusi
        tools: list tool yang dipakai
    """
    init_db()
    
    sukses = 1 if hasil.get("sukses") else 0
    error = hasil.get("error", "")
    langkah = json.dumps(hasil.get("hasil", {}))[:500] if isinstance(hasil.get("hasil"), dict) else str(hasil.get("hasil", ""))[:500]
    tools_str = json.dumps(tools) if tools else ""
    
    conn = _conn()
    with conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO experience (intent, pesan, hasil_sukses, langkah, error, tools, waktu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (intent, pesan[:200], sukses, langkah, error[:500], tools_str, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    
    print(f"[Experience] Catat: {intent} → {'SUKSES' if sukses else 'GAGAL'}")


def ambil_pengalaman(intent=None, jumlah=5):
    """Ambil pengalaman terakhir untuk intent tertentu."""
    init_db()
    
    # FIX_CURSOR
# FIX_COMMIT
    conn = _conn()
    c = conn.cursor()
    if intent:
        c.execute("""
            SELECT id, intent, pesan, hasil_sukses, langkah, error, waktu
            FROM experience 
            WHERE intent = ?
            ORDER BY id DESC LIMIT ?
        """, (intent, jumlah))
    else:
        c.execute("""
            SELECT id, intent, pesan, hasil_sukses, langkah, error, waktu
            FROM experience 
            ORDER BY id DESC LIMIT ?
        """, (jumlah,))
    
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "intent": r[1],
            "pesan": r[2],
            "sukses": bool(r[3]),
            "langkah": r[4],
            "error": r[5],
            "waktu": r[6],
        }
        for r in rows
    ]


def pengalaman_relevan(pesan, max_hasil=3):
    """
    Cari pengalaman relevan dengan pesan saat ini.
    Pakai keyword matching sederhana.
    """
    init_db()
    
    p = pesan.lower()
    
    conn = _conn()
    with conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, intent, pesan, hasil_sukses, langkah, error, waktu
            FROM experience 
            ORDER BY id DESC LIMIT 100
        """)
        rows = c.fetchall()
    
    # Skor relevansi
    hasil = []
    for r in rows:
        pesan_lama = (r[2] or "").lower()
        skor = 0
        
        # Cek keyword sama
        kata_pesan = set(p.split())
        kata_lama = set(pesan_lama.split())
        skor = len(kata_pesan & kata_lama)
        
        if skor > 0:
            hasil.append({
                "id": r[0],
                "intent": r[1],
                "pesan": r[2],
                "sukses": bool(r[3]),
                "error": r[5],
                "waktu": r[6],
                "skor": skor,
            })
    
    hasil.sort(key=lambda x: x["skor"], reverse=True)
    return hasil[:max_hasil]


def ringkasan_pengalaman(intent=None, jumlah=5):
    """Ringkas pengalaman - sukses vs gagal."""
    pengalaman = ambil_pengalaman(intent=intent, jumlah=jumlah)
    
    if not pengalaman:
        return {"total": 0, "sukses": 0, "gagal": 0, "persen_sukses": 0}
    
    total = len(pengalaman)
    sukses = sum(1 for p in pengalaman if p["sukses"])
    gagal = total - sukses
    
    return {
        "total": total,
        "sukses": sukses,
        "gagal": gagal,
        "persen_sukses": round(sukses / total * 100, 1) if total > 0 else 0,
    }


def prompt_pengalaman(pesan):
    """
    Generate prompt dari pengalaman relevan.
    Return: string atau "".
    """
    pengalaman = pengalaman_relevan(pesan, max_hasil=3)
    if not pengalaman:
        return ""
    
    teks = "\n\n[PENGALAMAN SEBELUMNYA]"
    for p in pengalaman:
        status = "✅ sukses" if p["sukses"] else "❌ gagal"
        teks += f"\n- {p['intent']} {status}: {p['pesan'][:80]}"
        if not p["sukses"] and p["error"]:
            teks += f"\n  Error: {p['error'][:100]}"
    
    return teks


# ============ TEST ============
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST EXPERIENCE HUB")
    print("=" * 60)
    print()
    
    # 1. Init
    init_db()
    print("1. DB init OK")
    print()
    
    # 2. Catat pengalaman
    print("2. Catat pengalaman:")
    catat_pengalaman(
        "coding buat script hello",
        "coding",
        {"sukses": True, "hasil": {"file": "output.py"}},
        tools=["coding_loop"]
    )
    catat_pengalaman(
        "scan folder E:\\test",
        "scan",
        {"sukses": True, "hasil": {"file": "scan.txt", "total": 100}},
        tools=["scan_folder"]
    )
    catat_pengalaman(
        "coding buat Flask",
        "coding",
        {"sukses": False, "error": "LLM timeout"},
        tools=["coding_loop"]
    )
    print()
    
    # 3. Ambil pengalaman
    print("3. Pengalaman coding:")
    for p in ambil_pengalaman(intent="coding", jumlah=3):
        print(f"   - {p['pesan'][:50]} → {'SUKSES' if p['sukses'] else 'GAGAL'}")
    print()
    
    # 4. Ringkasan
    print("4. Ringkasan coding:")
    print(f"   {ringkasan_pengalaman(intent='coding')}")
    print()
    
    # 5. Cari relevan
    print("5. Pengalaman relevan 'coding Flask':")
    for p in pengalaman_relevan("coding Flask"):
        print(f"   - {p['pesan'][:50]} → {'SUKSES' if p['sukses'] else 'GAGAL'} (skor: {p['skor']})")
    print()
    
    # 6. Prompt
    print("6. Prompt pengalaman:")
    print(f"   {prompt_pengalaman('coding Flask')}")