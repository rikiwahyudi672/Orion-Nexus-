#!/usr/bin/env python3
"""sederhana_dc.py -- Sederhanakan on_message: langsung ke jarvis_node.

Masalah: alur on_message kebanyakan lapisan (skill check -> workflow ->
         formal ga nyambung).
Solusi: pesan biasa langsung panggil jarvis_node(state) kayak CLI.
         Sama persis kayak nexus_kerja.py jalaninnya.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python sederhana_dc.py
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"
TAG = "SEDERHANA_DC"


def main():
    print("=== sederhana_dc.py ===")
    if not TARGET.is_file():
        print("GAGAL: file tidak ketemu.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Ganti isi blok if pesan biasa: langsung ke jarvis_node
    # Anchor: dari "# [AUTO_CHAT_DC]" sampai sebelum "await bot.process_commands"
    pola = (
        r"([ \t]*)# \[AUTO_CHAT_DC\] respon semua pesan teks biasa\n"
        r"\1if message\.content\.strip\(\) and not message\.content\.strip\(\)\[0\] in \('!', '/', '\.'\):\n"
    )
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor AUTO_CHAT_DC tidak ketemu.")
        print("Pastikan auto_chat_dc.py sudah dijalankan.")
        sys.exit(1)

    indent = m.group(1)
    # Cari akhir blok: dari anchor sampai baris "await bot.process_commands"
    start = m.start()
    end_m = re.search(r"^([ \t]*)await bot\.process_commands\(message\)", teks[m.end():], re.MULTILINE)
    if not end_m:
        print("GAGAL: process_commands tidak ketemu.")
        sys.exit(1)
    end = m.end() + end_m.start()

    blok_baru = (
        "%s# [%s] langsung ke jarvis_node kayak CLI\n" % (indent, TAG)
        + "%sif message.content.strip() and not message.content.strip()[0] in ('!', '/', '.'):\n" % indent
        + "%s    perintah = message.content.replace(f\"<@{bot.user.id}>\", \"\").replace(f\"<@!{bot.user.id}>\", \"\").strip()\n" % indent
        + "%s    if not perintah:\n" % indent
        + "%s        await message.reply(\"Halo bos! Ada yang bisa gue bantu?\")\n" % indent
        + "%s        await bot.process_commands(message)\n" % indent
        + "%s        return\n" % indent
        + "%s    try:\n" % indent
        + "%s        from tools.chat_log import tambah_chat\n" % indent
        + "%s        tambah_chat(message.author.name, perintah, \"discord\", \"user\")\n" % indent
        + "%s    except Exception:\n" % indent
        + "%s        pass\n" % indent
        + "%s    await message.channel.typing()\n" % indent
        + "%s    try:\n" % indent
        + "%s        from agents.jarvis import jarvis_node\n" % indent
        + "%s        state = {'perintah': perintah, 'mode': '', 'agen_fokus': 'jarvis',\n" % indent
        + "%s                 'data_riset': None, 'konten': None, 'prospek': None,\n" % indent
        + "%s                 'output': None, 'next': None, 'riwayat': []}\n" % indent
        + "%s        hasil = jarvis_node(state)\n" % indent
        + "%s        konten = (hasil.get('konten') if hasil else None) or \"Gue gak tau mau jawab apa bos.\"\n" % indent
        + "%s    except Exception as e:\n" % indent
        + "%s        import traceback; traceback.print_exc()\n" % indent
        + "%s        konten = f\"Error: {e}\"\n" % indent
        + "%s    try:\n" % indent
        + "%s        from tools.chat_log import tambah_chat\n" % indent
        + "%s        tambah_chat(\"Jarvis\", konten, \"discord\", \"bot\")\n" % indent
        + "%s    except Exception:\n" % indent
        + "%s        pass\n" % indent
        + "%s    if len(konten) > 1900:\n" % indent
        + "%s        await message.reply(konten[:1900] + \"...\")\n" % indent
        + "%s    else:\n" % indent
        + "%s        await message.reply(konten)\n" % indent
        + "\n"
    )

    teks = teks[:start] + blok_baru + teks[end:]

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_sederhana_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    TARGET.write_text(teks, encoding="utf-8")

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
