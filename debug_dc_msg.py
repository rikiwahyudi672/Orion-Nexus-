#!/usr/bin/env python3
"""debug_dc_msg.py -- Tambah print debug sementara di on_message.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python debug_dc_msg.py
Jalankan lagi untuk hapus debugnya (toggle).
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"
DEBUG_LINE = '    print("[DEBUG-DC] author=%s content=%r ch=%s" % (message.author, message.content[:60], type(message.channel).__name__))\n'
ANCHOR = "    if message.author == bot.user:\n        return\n"


def main():
    if not TARGET.is_file():
        print("GAGAL: file tidak ketemu.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_dbg_" + t)
    shutil.copy2(str(TARGET), str(bak))

    if "[DEBUG-DC]" in teks:
        # hapus debug (toggle off)
        teks = teks.replace(DEBUG_LINE, "")
        TARGET.write_text(teks, encoding="utf-8")
        print("[OK] debug dihapus. Restart bot.")
    else:
        assert ANCHOR in teks, "anchor tidak ketemu"
        teks = teks.replace(ANCHOR, ANCHOR + DEBUG_LINE, 1)
        TARGET.write_text(teks, encoding="utf-8")
        print("[OK] debug dipasang. Restart bot, kirim 1 pesan biasa, liat console.")
        print("     Jalankan lagi script ini untuk hapus debugnya.")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("compile OK.")


if __name__ == "__main__":
    main()
