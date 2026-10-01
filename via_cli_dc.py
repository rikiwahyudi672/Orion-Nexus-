#!/usr/bin/env python3
"""via_cli_dc.py -- Discord panggil nexus_kerja.py via subprocess.

Alasan: import langsung di Discord bermasalah (cache module, cwd).
        Subprocess ke CLI dijamin identik dengan tes manual yang sukses.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"
TAG = "VIA_CLI_DC"


def main():
    print("=== via_cli_dc.py ===")
    if not TARGET.is_file():
        print("GAGAL.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Ganti blok SEDERHANA_DC/FIX_CWD_DC jadi via subprocess
    # Anchor: dari "# [SEDERHANA_DC]" sampai sebelum "await bot.process_commands"
    pola = r"([ \t]*)# \[SEDERHANA_DC\].*?(?=^[ \t]*await bot\.process_commands\(message\))"
    m = re.search(pola, teks, re.MULTILINE | re.DOTALL)
    if not m:
        print("GAGAL: anchor SEDERHANA_DC tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    start, end = m.start(), m.end()

    blok = (
        "%s# [%s] via CLI subprocess (identik dengan tes manual)\n" % (indent, TAG)
        + "%sif message.content.strip() and not message.content.strip()[0] in ('!', '/', '.'):\n" % indent
        + "%s    perintah = message.content.replace(f\"<@{bot.user.id}>\", \"\").replace(f\"<@!{bot.user.id}>\", \"\").strip()\n" % indent
        + "%s    if not perintah:\n" % indent
        + "%s        await message.reply(\"Halo bos! Ada yang bisa gue bantu?\")\n" % indent
        + "%s        await bot.process_commands(message)\n" % indent
        + "%s        return\n" % indent
        + "%s    await message.channel.typing()\n" % indent
        + "%s    try:\n" % indent
        + "%s        import subprocess\n" % indent
        + "%s        r = subprocess.run(\n" % indent
        + "%s            [\"python\", \"E:/Project Software/Orion/nexus_kerja.py\", \"jarvis\", perintah],\n" % indent
        + "%s            capture_output=True, text=True, timeout=120,\n" % indent
        + "%s            cwd=\"E:/Project Software/Orion\")\n" % indent
        + "%s        konten = r.stdout.strip() or r.stderr.strip() or \"Gue gak tau mau jawab apa bos.\"\n" % indent
        + "%s    except Exception as e:\n" % indent
        + "%s        konten = f\"Error: {e}\"\n" % indent
        + "%s    if len(konten) > 1900:\n" % indent
        + "%s        await message.reply(konten[:1900] + \"...\")\n" % indent
        + "%s    else:\n" % indent
        + "%s        await message.reply(konten)\n" % indent
        + "\n"
    )

    teks = teks[:start] + blok + teks[end:]

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_viacli_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang. Restart bot, tes lagi.")


if __name__ == "__main__":
    main()
