"""Skill: kalkulator-voice."""

def jalankan(a, b, op="+"):
    if op == "+": hasil = a + b
    elif op == "-": hasil = a - b
    elif op == "*": hasil = a * b
    elif op == "/": hasil = a / b if b != 0 else "Error"
    else: return {"sukses": False, "error": "Op tidak dikenal"}
    
    pesan = f"Hasil {a} {op} {b} adalah {hasil}"
    return {"sukses": True, "hasil": hasil, "pesan": pesan}


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

