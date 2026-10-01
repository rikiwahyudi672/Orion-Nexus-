"""fix_soul_mojibake.py - Fix mojibake di SOUL.md"""
from pathlib import Path

path = Path("config/SOUL.md")
content = path.read_text(encoding="utf-8")

# Fix berulang - sampai bersih
for i in range(5):
    if "Ã" not in content and "â€" not in content and "ð" not in content:
        print(f"[OK] Bersih setelah {i} iterasi")
        break
    try:
        content = content.encode("latin-1").decode("utf-8")
        print(f"[{i+1}] Fix 1 lapis")
    except Exception as e:
        print(f"[{i+1}] Gagal: {e}")
        break

# Simpan
path.write_text(content, encoding="utf-8")
print()
print("=== 10 baris terakhir ===")
for line in content.split("\n")[-15:]:
    print(line)
