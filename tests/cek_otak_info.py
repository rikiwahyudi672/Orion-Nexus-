"""cek_otak_info.py - Cek info lengkap otak ORION"""
import core
from pathlib import Path
from datetime import datetime

model = Path(core.P["model"])

if model.exists():
    print("INFO MODEL:")
    print(f"  Path: {model}")
    print(f"  Ukuran: {model.stat().st_size} bytes")
    print(f"  Terakhir dilatih: {datetime.fromtimestamp(model.stat().st_mtime)}")
    print()
    print("KONFIGURASI:")
    print(f"  Input: 2 fitur (sin, cos)")
    print(f"  Hidden: [32, 16, 8]")
    print(f"  Output: {len(core.CFG['model']['aktivitas'])} aktivitas")
    print(f"  Aktivitas: {core.CFG['model']['aktivitas']}")
    print()
    print("DATA TRAINING:")
    print(f"  Total: {len(core.DATA_HABIT)} titik")
    for j, a in core.DATA_HABIT[:10]:
        print(f"    {j:02d}:00 -> {a}")
    print("    ...")
else:
    print("Model belum ada")