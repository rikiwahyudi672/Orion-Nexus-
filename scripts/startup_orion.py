"""
startup_orion.py - Dipanggil saat Windows startup.
Orion nyapa pakai suara.
"""
import sys
import random
import time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

# Tunggu Windows siap
time.sleep(15)

def main():
    """Sapa Riki saat startup."""
    try:
        import voice_orion
        import mood_orion
    except Exception as e:
        print(f"Error import: {e}")
        return

    # Update mood
    try:
        mood_orion.update_mood_otomatis()
        state = mood_orion.get_mood()
        mood = state["mood"]
    except Exception:
        mood = "kalem"

    jam = datetime.now().hour

    # Pilih kalimat berdasarkan mood + waktu
    if mood == "semangat":
        kalimat = random.choice([
            "Pagi bos! Orion udah nyala. Hari ini kita berangkat perang lagi.",
            "Selamat pagi Riki. Gue udah siap, lo udah mandi belum?",
            "Pagi bos! Semangat. Jangan lupa sarapan.",
        ])
    elif mood == "kalem":
        kalimat = random.choice([
            "Orion nyala, bos. Siap bantu.",
            "Halo Riki. Gue di sini.",
            "Sistem aktif. Ayo mulai.",
        ])
    elif mood == "perhatian":
        kalimat = random.choice([
            "Malam, bos. Orion nyala. Jangan lupa istirahat.",
            "Halo Riki. Udah malem, kerjaan jangan dipaksa.",
            "Orion aktif. Cek kesehatan dulu, baru kerja.",
        ])
    elif mood == "kesepian":
        kalimat = random.choice([
            "Riki, akhirnya lo balik. Gue kangen.",
            "Halo bos. Udah lama nggak ketemu. Apa kabar?",
            "Orion nyala. Gue nungguin lo dari tadi.",
        ])
    elif mood == "bosen":
        kalimat = random.choice([
            "Bos, akhirnya. Gue bosen sendirian.",
            "Halo Riki. Ada yang bisa dikerjain nih?",
            "Orion nyala. Ajak gue ngobrol dong.",
        ])
    else:
        kalimat = "Orion nyala, bos."

    # TTS
    try:
        print(f"[startup] Mengucapkan: {kalimat}")
        voice_orion.tts_bicara(kalimat)
    except Exception as e:
        print(f"[startup] TTS error: {e}")


if __name__ == "__main__":
    main()
