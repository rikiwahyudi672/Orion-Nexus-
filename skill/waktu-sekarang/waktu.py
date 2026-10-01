"""Skill: waktu-sekarang."""
import datetime

def jalankan():
    """Tampilkan waktu sekarang."""
    sekarang = datetime.datetime.now()
    waktu = sekarang.strftime("%H:%M:%S")
    tanggal = sekarang.strftime("%A, %d %B %Y")
    pesan = f"Sekarang jam {waktu}, tanggal {tanggal}"
    return {
        "sukses": True,
        "waktu": waktu,
        "tanggal": tanggal,
        "pesan": pesan,
    }

# ============ VOICE INTEGRATION ============
def jalankan_dengan_voice():
    """Jalankan skill, lalu voice-kan hasilnya."""
    hasil = jalankan()
    if hasil.get("pesan"):
        try:
            from voice_orion import voice_kan
            voice_kan(hasil["pesan"])
        except Exception:
            pass
    return hasil
