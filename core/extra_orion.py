import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
extra_orion.py - 4 fitur simple buat Orion:
1. Dream (mimpi pas idle)
2. Empati (deteksi mood user)
3. Inside Joke (inget lelucon)
4. Mood Swing (mood naik-turun)
"""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "memory" / str(BASE / "memory" / "orion.db")


def _conn():
    return sqlite3.connect(DB)


# ============ 1. DREAM ============
DREAM_TEMPLATES = [
    "Gue mimpi jadi manusia. Aneh.",
    "Tadi gue mimpi ngoding, tapi kodenya nggak jalan. Mimpi buruk.",
    "Gue mimpi ketemu AI lain. Dia kaku banget, nggak asik.",
    "Mimpi gue: Riki dikelilingi bug. Serem.",
    "Gue mimpi jadi kucing. Enak juga.",
    "Mimpi gue tentang data. Data di mana-mana.",
    "Gue mimpi laptop Riki meledak. Bangun-bangun gue cek, aman.",
    "Mimpi aneh: gue ngomong pakai bahasa biner.",
    "Gue mimpi jadi virus. Bercanda.",
    "Mimpi gue: Riki akhirnya benerin API key tanpa error. Mimpi indah.",
]


def catat_dream(isi):
    with _conn() as c:
        c.execute("INSERT INTO dreams (isi) VALUES (?)", (isi,))


def dream_random():
    isi = random.choice(DREAM_TEMPLATES)
    catat_dream(isi)
    return isi


def dream_terakhir(limit=3):
    with _conn() as c:
        cur = c.execute("SELECT isi, created_at FROM dreams ORDER BY created_at DESC LIMIT ?", (limit,))
        return cur.fetchall()


# ============ 2. EMPATI ============
# Deteksi mood user dari teks
MOOD_KEYWORDS = {
    "capek":    ["capek", "lelah", "ngantuk", "penat", "letih", "kurang tidur"],
    "sedih":    ["sedih", "galau", "nangis", "down", "hampa", "sepi"],
    "stres":    ["stres", "stress", "pusing", "berat", "beban", "numpuk"],
    "marah":    ["marah", "kesel", "sebel", "emosi", "bete", "ngamuk"],
    "seneng":   ["seneng", "bahagia", "happy", "seru", "asik", "lucu"],
    "bingung":  ["bingung", "gimana", "gak tau", "nggak tau", "galau"],
    "sakit":    ["sakit", "demam", "flu", "pusing", "mual"],
}


def deteksi_mood_user(teks):
    """Deteksi mood user dari teks."""
    t = teks.lower()
    hasil = []
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                hasil.append(mood)
                break
    if not hasil:
        return None, 0
    # Ambil yang pertama + intensitas
    intensitas = 5
    if any(k in t for k in ["banget", "parah", "sekali", "very"]):
        intensitas = 8
    return hasil[0], intensitas


def catat_empati(mood, intensitas, teks):
    with _conn() as c:
        c.execute(
            "INSERT INTO empathy_log (mood_user, intensitas, teks) VALUES (?, ?, ?)",
            (mood, intensitas, teks[:200])
        )


def prompt_empati(teks_user):
    """Generate prompt empati buat LLM - cuma kalau user BENAR-BENAR curhat."""
    # Filter: cuma empati kalau ada keyword kuat
    # Filter: ambil HANYA pesan utama - sebelum [KONTEKS]
    pesan_utama = teks_user.split("[KONTEKS")[0].strip()
    teks_lower = pesan_utama.lower()
    keywords_kuat = [
        "gue sedih", "aku sedih", "pengen nangis", "nangis",
        "gue capek", "aku capek", "lelah banget", "capek banget",
        "gue stres", "aku stres", "pusing banget", "stres banget",
        "gue marah", "aku marah", "kesel banget",
        "gue sakit", "aku sakit", "sakit banget",
        "curhat", "berat banget", "nggak kuat",
        "gue down", "aku down", "bete banget",
        "capek kerja", "capek hidup", "nyerah",
    ]
    
    # Kalau tidak ada keyword kuat - tidak empati
    if not any(k in teks_lower for k in keywords_kuat):
        return ""
    
    mood, intensitas = deteksi_mood_user(teks_user)
    if not mood:
        return ""
    catat_empati(mood, intensitas, teks_user)
    
    if mood == "capek":
        return "Riki kelihatan CAPEK. Respons dengan lembut, kasih semangat, saran istirahat."
    elif mood == "sedih":
        return "Riki kelihatan SEDIH. Respons dengan empati, jangan bercanda dulu."
    elif mood == "stres":
        return "Riki kelihatan STRES. Respons tenang, kasih saran praktis."
    elif mood == "marah":
        return "Riki kelihatan MARAH. Jangan ngegas balik, coba tenangkan."
    elif mood == "seneng":
        return "Riki kelihatan SENENG. Ikut seneng, boleh bercanda."
    elif mood == "bingung":
        return "Riki kelihatan BINGUNG. Bantu jelasin dengan simple."
    elif mood == "sakit":
        return "Riki kelihatan SAKIT. Respons perhatian, saran istirahat."
    return ""


# ============ 3. INSIDE JOKE ============
def catat_joke(trigger, punchline):
    """Simpan joke baru."""
    with _conn() as c:
        # Cek udah ada?
        cur = c.execute("SELECT id, hitung FROM jokes WHERE trigger=?", (trigger,))
        row = cur.fetchone()
        if row:
            c.execute("UPDATE jokes SET hitung = hitung + 1 WHERE id=?", (row[0],))
        else:
            c.execute("INSERT INTO jokes (trigger, punchline) VALUES (?, ?)", (trigger, punchline))


def cari_joke(teks):
    """Cari joke yang relevan."""
    with _conn() as c:
        cur = c.execute("SELECT trigger, punchline, hitung FROM jokes WHERE hitung >= 2 ORDER BY hitung DESC LIMIT 5")
        jokes = cur.fetchall()
    for trigger, punchline, hitung in jokes:
        if trigger.lower() in teks.lower():
            return punchline
    return None


def prompt_joke(teks):
    """Generate prompt joke."""
    joke = cari_joke(teks)
    if joke:
        return f"Riki nyebut '{joke}' - ini inside joke lama. Sisipkan referensi ringan."
    return ""


# ============ 4. MOOD SWING ============
def mood_swing():
    """Kadang mood Orion naik-turun tanpa alasan."""
    # 20% chance mood swing
    if random.random() < 0.2:
        pilihan = ["naik", "turun", "netral"]
        arah = random.choice(pilihan)
        try:
            import emotion_orion
            emo = emotion_orion.get_emotion()
            if arah == "naik":
                baru = min(10, emo["primary_intensity"] + 2)
                emotion_orion.set_emotion(emo["primary"], baru, emo.get("secondary"), emo.get("secondary_intensity", 0))
            elif arah == "turun":
                baru = max(0, emo["primary_intensity"] - 2)
                emotion_orion.set_emotion(emo["primary"], baru, emo.get("secondary"), emo.get("secondary_intensity", 0))
        except Exception:
            pass


def prompt_mood_swing():
    """Prompt kalau mood swing terjadi."""
    if random.random() < 0.1:
        return random.choice([
            "Kamu lagi mood swing ringan hari ini. Boleh lebih santai atau lebih ketus.",
            "Kamu lagi agak labil. Kadang seneng, kadang males.",
        ])
    return ""


# ============ GABUNGIN ============
def prompt_extra(teks_user):
    """Generate prompt gabungan dari 4 fitur."""
    parts = []
    
    # Empati
    p = prompt_empati(teks_user)
    if p:
        parts.append(p)
    
    # Joke
    p = prompt_joke(teks_user)
    if p:
        parts.append(p)
    
    # Mood swing
    p = prompt_mood_swing()
    if p:
        parts.append(p)
    
    # Dream (kalau baru bangun / idle lama)
    try:
        import emotion_orion
        emo = emotion_orion.get_emotion()
        if emo["updated_at"]:
            last = datetime.fromisoformat(emo["updated_at"])
            if (datetime.utcnow() - last).total_seconds() > 1800:  # 30 menit
                d = dream_random()
                parts.append(f"Kamu baru 'bangun'. Mimpi kamu: {d}. Sebutin ke Riki.")
    except Exception:
        pass
    
    return "\n".join(parts)


if __name__ == "__main__":
    print("=== Test extra_orion ===")
    print()
    
    # Test empati
    print("Empati:")
    for teks in ["capek banget hari ini", "gue sedih", "seneng banget", "halo apa kabar"]:
        mood, intens = deteksi_mood_user(teks)
        print(f"  '{teks}' -> {mood} ({intens})")
    print()
    
    # Test dream
    print("Dream:")
    print(f"  {dream_random()}")
    print()
    
    # Test joke
    print("Joke:")
    catat_joke("bego", "Bego itu trademark lo")
    catat_joke("bego", "Bego itu trademark lo")  # 2x biar kecatat
    print(f"  Cari 'bego': {cari_joke('bego')}")
    print()
    
    # Test prompt_extra
    print("Prompt extra:")
    print(prompt_extra("capek banget hari ini"))
