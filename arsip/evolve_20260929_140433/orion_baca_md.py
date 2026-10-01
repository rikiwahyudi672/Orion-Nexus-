"""
orion_baca_md.py - Orion baca semua MD di _data/md
"""
import sys
from pathlib import Path

sys.path.insert(0, 'core')
sys.path.insert(0, '.')

BASE = Path(".")
MD_DIR = BASE / "_data" / "md"

print("=" * 70)
print("  ORION BACA MD")
print("=" * 70)
print()

if not MD_DIR.exists():
    print(f"Folder tidak ada: {MD_DIR}")
    exit(1)

md_files = sorted(MD_DIR.rglob("*.md"), key=lambda x: x.name)
print(f"Folder: {MD_DIR}")
print(f"Total file .md: {len(md_files)}")
print()

if not md_files:
    print("Tidak ada file .md")
    exit(1)

# Baca satu per satu
total_size = 0
for i, f in enumerate(md_files, 1):
    print("=" * 70)
    print(f"  [{i}/{len(md_files)}] {f.relative_to(MD_DIR)}")
    print("=" * 70)
    print()
    
    try:
        content = f.read_text(encoding='utf-8', errors='ignore')
        size = len(content)
        total_size += size
        
        print(f"  Ukuran: {size:,} B")
        print(f"  Baris: {len(content.split(chr(10)))}")
        print()
        print("  --- 15 baris pertama ---")
        for j, line in enumerate(content.split('\n')[:15], 1):
            print(f"  {j:3}: {line[:80]}")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()

print("=" * 70)
print("  RINGKASAN")
print("=" * 70)
print()
print(f"  Total file: {len(md_files)}")
print(f"  Total ukuran: {total_size:,} B")
print()

# Test Orion - baca file
print("=" * 70)
print("  TEST ORION - BACA FILE")
print("=" * 70)
print()

if md_files:
    file_test = md_files[0]
    print(f"  Test file: {file_test.name}")
    print()
    
    try:
        from orion_tool_loop import chat as tool_loop_chat
        hasil = tool_loop_chat(f"baca file {file_test}", riwayat=[], verbose=True)
        print()
        print(f"  Hasil: {hasil[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

print()
print("=" * 70)
print("  SELESAI")
print("=" * 70)
