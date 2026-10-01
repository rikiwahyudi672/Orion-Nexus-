"""Skill: sapa-voice - Sapa user dengan suara."""

def jalankan(nama="User"):
    """Sapa user."""
    pesan = f"Halo {nama}! Orion di sini. Ada yang bisa dibantu?"
    return {
        "sukses": True,
        "pesan": pesan,
        "nama": nama,
    }

if __name__ == "__main__":
    import sys
    nama = sys.argv[1] if len(sys.argv) > 1 else "User"
    hasil = jalankan(nama)
    print(hasil["pesan"])


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

