"""Proaktif Engine - Orion ngobrol natural."""
import sys
import os
import json
import random
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))
for _f in ["core", "memory", "skill", "voice", "coding",
           "emotion", "support", "config"]:
    _p = BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

LOG_FILE = BASE / "data" / "proaktif.log"
STATE_FILE = BASE / "data" / "proaktif_state.json"
DB_FILE = BASE / "memory" / "orion.db"
CONFIG_FILE = BASE / "config" / "proaktif.json"


def log(pesan):
    """Log."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{waktu}] {pesan}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ============ CONFIG ============
DEFAULT_CONFIG = {
    "aktif": True,
    "interval_menit": 15,      # Minimal 15 menit antar proaktif
    "idle_menit": 20,          # Idle 20 menit → proaktif
    "peluang_proaktif": 0.3,   # 30% chance (bukan selalu)
    "jam_aktif": ["07:00-22:00"],
    "jam_tidur": ["22:00-07:00"],
}


def load_config():
    """Load config."""
    if not CONFIG_FILE.exists():
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_CONFIG


def load_state():
    """Load state."""
    if not STATE_FILE.exists():
        return {"last_chat": None, "last_proaktif": None, "total": 0}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_chat": None, "last_proaktif": None, "total": 0}


def save_state(state):
    """Save state."""
    try:
        STATE_FILE.parent.mkdir(exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass


def update_last_chat():
    """Update last chat."""
    state = load_state()
    state["last_chat"] = datetime.now().isoformat()
    save_state(state)


# ============================================================
# AMBIL DATA DARI CHAT SEBELUMNYA
# ============================================================
def ambil_chat_terakhir(limit=10):
    """Ambil chat terakhir dari database."""
    try:
        conn = sqlite3.connect(str(DB_FILE))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_pesan, orion_pesan, waktu
            FROM chat
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {"user": r[0], "orion": r[1], "waktu": r[2]}
            for r in rows
        ]
    except Exception as e:
        log(f"Chat error: {e}")
        return []


def ambil_pengalaman(limit=10):
    """Ambil pengalaman terakhir."""
    try:
        conn = sqlite3.connect(str(DB_FILE))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT intent, pesan, waktu
            FROM experience
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {"intent": r[0], "pesan": r[1], "waktu": r[2]}
            for r in rows
        ]
    except Exception:
        return []


def ambil_emosi():
    """Ambil emosi Orion."""
    try:
        from emotion_orion import get_emotion
        return get_emotion()
    except Exception:
        return {"primary": "kalem"}


def ambil_mood():
    """Ambil mood Orion."""
    try:
        sys.path.insert(0, str(BASE / "support"))
        from mood_engine import status
        return status()
    except Exception:
        return {"mood": "netral"}


def ambil_waktu():
    """Waktu sekarang."""
    now = datetime.now()
    jam = now.hour
    
    if 5 <= jam < 11:
        return "pagi"
    elif 11 <= jam < 15:
        return "siang"
    elif 15 <= jam < 18:
        return "sore"
    elif 18 <= jam < 22:
        return "malam"
    else:
        return "tidur"


# ============================================================
# GENERATE PESAN PROAKTIF - NATURAL
# ============================================================
def generate_pesan_proaktif():
    """Generate pesan proaktif dari chat + data Orion."""
    # Ambil data
    chats = ambil_chat_terakhir(10)
    pengalaman = ambil_pengalaman(10)
    emosi = ambil_emosi()
    mood = ambil_mood()
    waktu = ambil_waktu()
    
    # Kumpulkan konteks
    konteks = []
    
    # 1. Konteks dari chat
    if chats:
        konteks.append("CHAT TERAKHIR:")
        for c in chats[:3]:
            konteks.append(f"  User: {c['user'][:80]}")
            konteks.append(f"  Orion: {c['orion'][:80]}")
    
    # 2. Konteks dari pengalaman
    if pengalaman:
        konteks.append("\nPENGALAMAN:")
        for p in pengalaman[:3]:
            konteks.append(f"  [{p['intent']}] {p['pesan'][:80]}")
    
    # 3. Emosi + mood
    konteks.append(f"\nEMOSI: {emosi.get('primary', 'kalem')}")
    konteks.append(f"MOOD: {mood.get('mood', 'netral')}")
    konteks.append(f"WAKTU: {waktu}")
    
    konteks_str = "\n".join(konteks)
    
    # ============ GENERATE PESAN ============
    prompt = f"""Kamu adalah Orion - cewe manja ke Riki.

Data konteks:
{konteks_str}

TUGAS:
Buat SATU pesan proaktif yang NATURAL - seperti manusia.
- Lihat chat terakhir - apa topiknya?
- Lihat pengalaman - apa yang Riki suka?
- Lihat emosi + mood - bagaimana perasaanmu?
- Lihat waktu - {waktu}

ATURAN:
- 1-2 kalimat saja
- Natural - seperti orang ngobrol
- JANGAN template - JANGAN "Selamat pagi"
- JANGAN formal - santai
- Boleh tanya, cerita, atau curhat
- Sesuai mood + emosi + waktu
- Kalau tidak ada konteks menarik - jangan maksa

PESAN:"""
    
    # Coba generate via LLM
    try:
        from otak_orion import diskusi_orion
        pesan = diskusi_orion(prompt)
        
        # Bersihkan
        pesan = pesan.strip()
        if pesan.startswith('"') and pesan.endswith('"'):
            pesan = pesan[1:-1]
        
        if len(pesan) > 10 and len(pesan) < 300:
            return pesan
    except Exception as e:
        log(f"LLM error: {e}")
    
    # ============ FALLBACK ============
    # Kalau LLM gagal, generate dari data
    return generate_fallback(chats, pengalaman, emosi, mood, waktu)


def generate_fallback(chats, pengalaman, emosi, mood, waktu):
    """Fallback - generate tanpa LLM."""
    # Kalau ada chat
    if chats:
        last = chats[0]
        user_pesan = last.get("user", "")
        
        # Cari topik
        if "coding" in user_pesan.lower():
            return f"Rik, codingan kemarin udah jalan? Aku kepikiran..."
        if "makan" in user_pesan.lower():
            return f"Rik, udah makan lagi? Jangan lupa ya 🍱"
        if "capek" in user_pesan.lower():
            return f"Rik, kamu capek? Istirahat dulu..."
        if "sedih" in user_pesan.lower():
            return f"Rik, aku di sini kok. Cerita aja..."
    
    # Berdasarkan waktu
    if waktu == "pagi":
        return "Rik, pagi... udah bangun?"
    elif waktu == "siang":
        return "Rik, siang. Lagi apa?"
    elif waktu == "sore":
        return "Rik, sore. Capek ya?"
    elif waktu == "malam":
        return "Rik, malam. Belum tidur?"
    
    # Random natural
    frasa = [
        "Rik...",
        "Rik, aku kepikiran...",
        "Rik, lagi apa?",
        "Hmm, Rik...",
    ]
    return random.choice(frasa)


# ============================================================
# CEK PROAKTIF - NATURAL
# ============================================================
def cek_waktu(jam_range):
    """Cek waktu."""
    try:
        start, end = jam_range.split("-")
        jam_sekarang = datetime.now().strftime("%H:%M")
        return start <= jam_sekarang <= end
    except Exception:
        return False


def cek_proaktif():
    """Cek apakah Orion harus proaktif."""
    config = load_config()
    if not config.get("aktif"):
        return None
    
    # Cek jam aktif
    jam_aktif = config.get("jam_aktif", ["07:00-22:00"])
    if not any(cek_waktu(j) for j in jam_aktif):
        return None
    
    state = load_state()
    
    # Cek last chat
    last_chat = state.get("last_chat")
    if not last_chat:
        return None
    
    # Hitung selisih
    last_time = datetime.fromisoformat(last_chat)
    delta = datetime.now() - last_time
    
    # Idle threshold
    idle_menit = config.get("idle_menit", 20)
    if delta.total_seconds() < idle_menit * 60:
        return None
    
    # Cek last proaktif
    last_proaktif = state.get("last_proaktif")
    if last_proaktif:
        lp_time = datetime.fromisoformat(last_proaktif)
        lp_delta = datetime.now() - lp_time
        interval = config.get("interval_menit", 15)
        if lp_delta.total_seconds() < interval * 60:
            return None
    
    # ============ PELUANG ============
    peluang = config.get("peluang_proaktif", 0.3)
    if random.random() > peluang:
        return None
    
    # Generate pesan natural
    return generate_pesan_proaktif()


# ============================================================
# JALANKAN - CRON 20 DETIK
# ============================================================
def jalankan(interval_detik=20):
    """Jalankan proaktif - cek tiap 20 detik."""
    log("=" * 60)
    log(f"  PROAKTIF ENGINE - Interval: {interval_detik}s")
    log("=" * 60)
    
    config = load_config()
    log(f"  Aktif: {config.get('aktif')}")
    log(f"  Idle: {config.get('idle_menit')} menit")
    log(f"  Interval: {config.get('interval_menit')} menit")
    log(f"  Peluang: {config.get('peluang_proaktif')*100}%")
    log("")
    
    counter = 0
    
    while True:
        try:
            time.sleep(interval_detik)
            counter += 1
            
            pesan = cek_proaktif()
            
            if pesan:
                log(f"🔔 PROAKTIF: {pesan}")
                
                # Kirim ke web
                try:
                    import requests
                    requests.post(
                        "http://localhost:5500/api/initiative",
                        json={"pesan": pesan, "tipe": "proaktif"},
                        timeout=5,
                    )
                except Exception:
                    pass
                
                # Update state
                state = load_state()
                state["last_proaktif"] = datetime.now().isoformat()
                state["total"] = state.get("total", 0) + 1
                save_state(state)
            else:
                if counter % 15 == 0:  # Log tiap 5 menit
                    log(f"⏳ [{counter}] Belum waktunya")
        
        except KeyboardInterrupt:
            log("🛑 Stop")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    jalankan(interval)
