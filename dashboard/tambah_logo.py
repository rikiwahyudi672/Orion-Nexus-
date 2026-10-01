#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tambah_logo.py -- Tambah logo konstelasi kecil di atas wordmark ORION.

Disisipkan di awal logo_anim() di dashboard/dashboard_orion.py,
sebelum baris wordmark "  ORION". Kompak (5 baris), selaras indent.

Cara pakai (dari E:\\Project Software\\Orion\\dashboard):
    python tambah_logo.py
    python tambah_logo.py --kering   -> simulasi saja
"""

import argparse
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

MARK = "tambah_logo"
TGT = Path("dashboard_orion.py")

ANCHOR = r'^    print\(c\("  ORION", C\.CYAN \+ C\.BOLD\)$'

LOGO = (
    '    print(c("      ✦", C.CYAN))  # tambah_logo 30/09\n'
    '    print(c("    ✦   ✦", C.CYAN))\n'
    '    print(c("  ✦  ", C.CYAN) + c("O", C.CYAN + C.BOLD) + c("  ✦", C.CYAN))\n'
    '    print(c("    ✦   ✦", C.CYAN))\n'
    '    print(c("      ✦", C.CYAN))\n'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kering", action="store_true")
    a = ap.parse_args()

    if not TGT.exists():
        print("!! dashboard_orion.py tidak ketemu (jalankan dari folder dashboard)")
        sys.exit(1)
    src = TGT.read_text(encoding="utf-8")
    if MARK in src:
        print("OK: logo sudah terpasang (idempoten, lewati).")
        return

    m = re.search(ANCHOR, src, flags=re.MULTILINE)
    n = 1 if m else 0
    print(f"Patch cocok: {n} titik.")
    if not m:
        print("!! Anchor tidak ketemu. Batal (file tidak diubah).")
        sys.exit(1)
    baru = src[:m.start()] + LOGO + m.group(0) + src[m.end():]
    if a.kering:
        print("Mode --kering: tidak ada yang diubah.")
        return

    bak = TGT.with_name(
        f"{TGT.stem}.bak_logo_{datetime.now():%Y%m%d_%H%M%S}{TGT.suffix}")
    shutil.copy2(TGT, bak)
    print(f"Backup: {bak}")
    TGT.write_text(baru, encoding="utf-8")
    try:
        py_compile.compile(str(TGT), doraise=True)
        print("Compile OK.")
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, TGT)
        print(f"!! Compile gagal, restore dari backup.\n{e}")
        sys.exit(1)
    print("Selesai. Restart dashboard buat lihat logonya.")


if __name__ == "__main__":
    main()
