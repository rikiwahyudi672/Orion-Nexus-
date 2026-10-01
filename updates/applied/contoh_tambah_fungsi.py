# ===PATCH===
# TYPE: add_func
# TARGET: core.py
# FUNC: sapa_orion
# DESC: Contoh patch - tambah fungsi sapa_orion
# ===END===

def sapa_orion(nama="Riki"):
    """Fungsi sapa dari Orion."""
    from datetime import datetime
    jam = datetime.now().hour
    if jam < 12:
        salam = "Selamat pagi"
    elif jam < 18:
        salam = "Selamat siang"
    else:
        salam = "Selamat malam"
    pesan = f"{salam}, {nama}! Saya ORION."
    print(f"  ORION: {pesan}")
    return pesan