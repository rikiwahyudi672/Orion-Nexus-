"""rekomendasi-api-llm-gratis-legal.py - Skill rekomendasi-api-llm-gratis-legal."""

from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent


def info():
    """Info skill."""
    return {
        "nama": "rekomendasi-api-llm-gratis-legal",
        "deskripsi": "Skill rekomendasi-api-llm-gratis-legal",
        "waktu": datetime.now().isoformat(),
    }


def jalankan(**kwargs):
    """Jalankan skill."""
    return {
        "sukses": True,
        "skill": "rekomendasi-api-llm-gratis-legal",
        "pesan": f"Skill rekomendasi-api-llm-gratis-legal jalan",
        "kwargs": kwargs,
    }


if __name__ == "__main__":
    print(f"Skill: {info()['nama']}")
    print(f"Hasil: {jalankan()}")


# ============ VOICE INTEGRATION ============
# Ditambahkan otomatis oleh Orion - Evolusi Skill
def jalankan_dengan_voice(*args, **kwargs):
    """Jalankan skill, lalu voice-kan hasilnya."""
    hasil = jalankan(*args, **kwargs)
    
    # Cari pesan untuk di-voice
    pesan = None
    if isinstance(hasil, dict):
        pesan = hasil.get("pesan") or hasil.get("message")
    elif isinstance(hasil, str):
        pesan = hasil
    
    # Voice-kan kalau ada pesan
    if pesan:
        try:
            from voice_orion import voice_kan
            voice_kan(pesan)
        except Exception:
            pass
    
    return hasil

