#!/usr/bin/env python3
"""fokus_jarvis_dc.py -- Pesan biasa di Discord default ke Jarvis.

Masalah: on_message bikin state tanpa 'agen_fokus', workflow bingung,
         balesannya formal ga nyambung.
Solusi: tambah 'agen_fokus': 'jarvis' di state on_message.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python fokus_jarvis_dc.py
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"


def main():
    print("=== fokus_jarvis_dc.py ===")
    if not TARGET.is_file():
        print("GAGAL: file tidak ketemu.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if "'agen_fokus': 'jarvis'" in teks and "FOKUS_JARVIS_DC" in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Anchor: state di fallback on_message (tanpa agen_fokus)
    pola = (
        r"([ \t]*)state = \{\n"
        r"\1\s*'perintah': perintah, 'mode': '',\n"
        r"\1\s*'data_riset': None, 'konten': None,\n"
    )
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor state on_message tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    lama = m.group(0)
    baru = (
        "%s# [FOKUS_JARVIS_DC] default ke jarvis\n" % indent
        + "%sstate = {\n" % indent
        + "%s    'perintah': perintah, 'mode': '',\n" % indent
        + "%s    'agen_fokus': 'jarvis',\n" % indent
        + "%s    'data_riset': None, 'konten': None,\n" % indent
    )
    teks = teks.replace(lama, baru, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_fokus_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang, compile OK.")
    print("Hapus debug: python debug_dc_msg.py (toggle)")
    print("Restart bot, tes lagi.")


if __name__ == "__main__":
    main()
