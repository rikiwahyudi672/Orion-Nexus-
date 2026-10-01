"""fix_soul_loop.py - Fix mojibake berulang"""
from pathlib import Path

path = Path("config/SOUL.md")

# Baca
content = path.read_text(encoding="utf-8")

# Cek - fix berulang
for i in range(5):
    # Cek apakah masih ada mojibake
    if "Ã" not in content and "â" not in content:
        print(f"[OK] Bersih setelah {i} iterasi")
        break
    
    try:
        # Fix 1 lapis
        content = content.encode("latin-1").decode("utf-8")
        print(f"[{i+1}] Fix 1 lapis - 20 char: {repr(content[:20])}")
    except UnicodeDecodeError as e:
        print(f"[{i+1}] Tidak bisa fix lagi: {e}")
        break
    except UnicodeEncodeError as e:
        print(f"[{i+1}] Tidak bisa encode: {e}")
        break

# Simpan
path.write_text(content, encoding="utf-8")
print()
print("=== 10 baris pertama ===")
for line in content.split("\n")[:10]:
    print(line)
