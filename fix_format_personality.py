#!/usr/bin/env python3
"""fix_format_personality.py -- Include anti_halu di prompt.

Masalah: format_personality() cuma format field tertentu,
         anti_halu_spesifik nggak kebawa ke prompt.
Solusi: tambah blok ATURAN ANTI-HALU di format_personality().
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "tools" / "personality.py"
TAG = "FIX_FORMAT_HALU"


def main():
    print("=== fix_format_personality.py ===")
    if not TARGET.is_file():
        print("GAGAL.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Anchor: setelah loop contoh_voice, sebelum return teks
    pola = r"([ \t]*)for voice in p\.get\('contoh_voice', \[\]\):\n\1[ \t]*teks \+= f'- \"\{voice\}\"\\n'\n"
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    lama = m.group(0)
    baru = (
        lama
        + "\n"
        + "%s# [%s] include aturan anti-halu\n" % (indent, TAG)
        + "%sfor _k in ('anti_halu', 'anti_halu_spesifik', 'aturan', 'rules'):\n" % indent
        + "%s    _rules = p.get(_k, [])\n" % indent
        + "%s    if _rules:\n" % indent
        + "%s        teks += \"\\nATURAN ANTI-HALU (WAJIB DIPATUHI):\\n\"\n" % indent
        + "%s        for _r in _rules:\n" % indent
        + "%s            teks += f\"- {_r}\\n\"\n" % indent
        + "%s        break\n" % indent
    )
    teks = teks.replace(lama, baru, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".py.bak_format_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang.")


if __name__ == "__main__":
    main()
