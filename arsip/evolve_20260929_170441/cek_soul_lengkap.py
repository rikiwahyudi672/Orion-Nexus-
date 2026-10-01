from pathlib import Path

content = Path("config/SOUL.md").read_text(encoding="utf-8")
lines = content.split("\n")

print(f"Total baris: {len(lines)}")
print()
print("=== Baris 1-50 ===")
for i, line in enumerate(lines[:50], 1):
    print(f"{i:3}: {line}")

# Cek mojibake di seluruh file
print()
print("=== Cek mojibake ===")
if "Ã" in content:
    print("❌ Masih ada 'Ã' - mojibake")
    # Cari baris
    for i, line in enumerate(lines, 1):
        if "Ã" in line:
            print(f"  Baris {i}: {line[:80]}")
else:
    print("✅ Tidak ada mojibake 'Ã'")

if "â€" in content:
    print("❌ Masih ada 'â€' - mojibake")
    for i, line in enumerate(lines, 1):
        if "â€" in line:
            print(f"  Baris {i}: {line[:80]}")
else:
    print("✅ Tidak ada mojibake 'â€'")

if "ð" in content:
    print("❌ Masih ada 'ð' - mojibake emoji")
    for i, line in enumerate(lines, 1):
        if "ð" in line:
            print(f"  Baris {i}: {line[:80]}")
else:
    print("✅ Tidak ada mojibake 'ð'")
