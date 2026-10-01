import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import bangun_registry, format_daftar_tool

reg = bangun_registry()

# Cari tool baca file
for name, info in reg.items():
    if 'baca' in name.lower() or 'read' in name.lower() or 'file' in name.lower():
        print(f"=== {name} ===")
        print(f"  Slug: {info.get('slug')}")
        print(f"  Nama: {info.get('nama')}")
        print(f"  Deskripsi: {info.get('deskripsi')[:100]}")
        print(f"  Schema: {info.get('schema')}")
        print()
