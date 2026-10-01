import sys
from pathlib import Path

sys.path.insert(0, 'core')
sys.path.insert(0, '.')

print("=" * 60)
print("  CEK 1: KONTEKS DI OTAK")
print("=" * 60)

p = Path("core/otak_orion.py")
if p.exists():
    content = p.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')
    keywords = ["konteks", "context", "opsi", "history", "riwayat", "perintah_terakhir"]
    for kw in keywords:
        found = [(i, l.strip()[:80]) for i, l in enumerate(lines, 1) if kw.lower() in l.lower()]
        if found:
            print(f"\n  🔍 '{kw}': {len(found)} hasil")
            for ln, txt in found[:5]:
                print(f"     {ln}: {txt}")
        else:
            print(f"\n  ❌ '{kw}': TIDAK ADA")
else:
    print("  ❌ core/otak_orion.py TIDAK ADA")

print()
print("=" * 60)
print("  CEK 2: FUNGSI DI OTAK")
print("=" * 60)

if p.exists():
    content = p.read_text(encoding='utf-8', errors='ignore')
    for i, line in enumerate(content.split('\n'), 1):
        s = line.strip()
        if s.startswith('def ') or s.startswith('class ') or s.startswith('async def '):
            print(f"  {i}: {s[:90]}")
