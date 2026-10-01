#!/usr/bin/env python3
"""auto_chat_dc.py -- Patch simpel: bot respon semua pesan.

Ubah 1 baris kondisi di on_message jadi respon semua teks
(kecuali command prefix ! / .).

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python auto_chat_dc.py
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"


def main():
    print("=== auto_chat_dc.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    teks = TARGET.read_text(encoding="utf-8")
    if "AUTO_CHAT_DC" in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Ganti kondisi mention/DM jadi: semua pesan teks biasa
    pola = (
        r"^([ \t]*)if bot\.user\.mentioned_in\(message\)"
        r" or isinstance\(message\.channel, discord\.DMChannel\)[^\n]*:\n"
    )
    pengganti = (
        r"\1# [AUTO_CHAT_DC] respon semua pesan teks biasa" "\n"
        r"\1if message.content.strip() and not message.content.strip()[0] in ('!', '/', '.'):" "\n"
    )
    baru, n = re.subn(pola, pengganti, teks, count=1, flags=re.MULTILINE)

    if n == 0:
        print("GAGAL: baris kondisi tidak ketemu.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_autochat_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    TARGET.write_text(baru, encoding="utf-8")

    import py_compile

    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("[OK] terpasang, compile OK. Restart bot.")
    except Exception as e:
        print("GAGAL: %s. Restore." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)


if __name__ == "__main__":
    main()
