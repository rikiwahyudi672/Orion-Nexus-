"""fix_soul_encoding.py - Fix encoding SOUL.md"""
from pathlib import Path

path = Path("config/SOUL.md")
print(f"File: {path}")
print()

# Baca sebagai byte
raw = path.read_bytes()
print(f"Ukuran: {len(raw)} B")
print(f"20 byte pertama: {raw[:20].hex()}")
print()

# Coba baca sebagai UTF-8
try:
    content = raw.decode("utf-8")
    print("[OK] Bisa dibaca UTF-8")
    print(f"20 char pertama: {repr(content[:20])}")
except UnicodeDecodeError as e:
    print(f"[!] Bukan UTF-8: {e}")
    # Coba latin-1
    content = raw.decode("latin-1")
    print("[OK] Bisa dibaca Latin-1")
    print(f"20 char pertama: {repr(content[:20])}")

# Cek mojibake
if "â€" in content or "Ã" in content:
    print()
    print("[!] MOJIBAKE terdeteksi")
    
    # Coba fix - encode latin-1 → decode utf-8
    try:
        fixed = content.encode("latin-1").decode("utf-8")
        print(f"[OK] Bisa di-fix")
        print(f"20 char pertama setelah fix: {repr(fixed[:20])}")
        
        # Simpan
        path.write_text(fixed, encoding="utf-8")
        print(f"[OK] File disimpan")
    except Exception as e:
        print(f"[X] Gagal fix: {e}")
else:
    print()
    print("[OK] Tidak ada mojibake")
