"""test_baca_file.py"""
import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import bangun_registry

reg = bangun_registry()
print("Total tool:", len(reg))
print("baca_file ada:", "baca_file" in reg)

if "baca_file" in reg:
    info = reg["baca_file"]
    print()
    print("=== Info baca_file ===")
    print("  Slug:", info.get("slug"))
    print("  Nama:", info.get("nama"))
    print("  Deskripsi:", info.get("deskripsi"))
    print("  Schema:", info.get("schema"))
else:
    print()
    print("X baca_file TIDAK terdaftar")
