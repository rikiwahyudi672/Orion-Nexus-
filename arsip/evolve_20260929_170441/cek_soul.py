from pathlib import Path

path = Path("config/SOUL.md")
content = path.read_text(encoding="utf-8")

print(f"=== SOUL.md ===")
print(f"Ukuran: {len(content)} B")
print(f"Baris: {len(content.split(chr(10)))}")
print()

# Cek mojibake
mojibake = []
if "Ã" in content: mojibake.append("Ã")
if "â€" in content: mojibake.append("â€")
if "ð" in content: mojibake.append("ð")

if mojibake:
    print(f"❌ Masih ada mojibake: {mojibake}")
    for i, line in enumerate(content.split("\n"), 1):
        if any(m in line for m in mojibake):
            print(f"  Baris {i}: {line[:80]}")
else:
    print("✅ BERSIH - tidak ada mojibake")
