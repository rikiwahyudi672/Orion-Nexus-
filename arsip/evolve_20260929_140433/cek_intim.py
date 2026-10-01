from pathlib import Path

content = Path("config/SOUL.md").read_text(encoding="utf-8")
lines = content.split("\n")

# Cek INTIM
print("=== Cek ATURAN INTIM ===")
found_intim = False
for i, line in enumerate(lines, 1):
    if "INTIM" in line.upper():
        print(f"  Baris {i}: {line[:80]}")
        found_intim = True

if not found_intim:
    print("  ❌ ATURAN INTIM TIDAK ADA")
else:
    print()
    print("  ✅ ATURAN INTIM ADA")

# Cek ROMANTIS
print()
print("=== Cek ROMANTIS ===")
if "ROMANTIS" in content.upper():
    print("  ✅ ROMANTIS ADA")
else:
    print("  ❌ ROMANTIS TIDAK ADA")

# Cek ATURAN NATURAL
print()
print("=== Cek ATURAN NATURAL ===")
if "ATURAN NATURAL" in content.upper():
    print("  ✅ NATURAL ADA")
else:
    print("  ❌ NATURAL TIDAK ADA")

print()
print("=== 5 baris terakhir ===")
for line in lines[-10:]:
    print(f"  {line}")
