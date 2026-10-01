"""Skill: hitung-matematika - Hitung matematika sederhana."""

def jalankan(a, b, operasi="+"):
    """Hitung matematika."""
    try:
        a = float(a)
        b = float(b)
        if operasi == "+": return a + b
        if operasi == "-": return a - b
        if operasi == "*": return a * b
        if operasi == "/": return a / b if b != 0 else "Error: bagi nol"
        return "Operasi tidak dikenal"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        print(jalankan(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        print("Pakai: python hitung.py 5 + 3")


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

