#!/usr/bin/env python3
"""fix_web_cli.py -- Web server panggil nexus_kerja.py via subprocess.

Masalah: /api/chat pake buat_workflow() yang bikin halu.
Solusi: ganti jadi subprocess ke nexus_kerja.py (terbukti bener).
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "gui_web" / "server.py"
TAG = "FIX_WEB_CLI"


def main():
    print("=== fix_web_cli.py ===")
    if not TARGET.is_file():
        print("GAGAL: file tidak ketemu.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Anchor: blok try yang panggil buat_workflow di api_chat_post
    pola = (
        r"([ \t]*)try:\n"
        r"\1[ \t]*from graph\.workflow import buat_workflow\n"
        r"\1[ \t]*graph = buat_workflow\(\)\n"
    )
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    # Ganti dari "try:" sampai "next_node = hasil.get" dengan subprocess
    # Cari akhir blok: baris "next_node = hasil.get("next", "?")"
    start = m.start()
    end_pola = r"([ \t]*)next_node = hasil\.get\(\"next\", \"\?\"\)\n"
    em = re.search(end_pola, teks[start:])
    if not em:
        print("GAGAL: akhir blok tidak ketemu.")
        sys.exit(1)
    end = start + em.end()

    blok = (
        "%s# [%s] via CLI subprocess\n" % (indent, TAG)
        + "%stry:\n" % indent
        + "%s    import subprocess\n" % indent
        + "%s    agen = agen_fokus or \"jarvis\"\n" % indent
        + "%s    r = subprocess.run(\n" % indent
        + "%s        [\"python\", \"E:/Project Software/Orion/nexus_kerja.py\", agen, pesan],\n" % indent
        + "%s        capture_output=True, text=True, timeout=120,\n" % indent
        + "%s        cwd=\"E:/Project Software/Orion\")\n" % indent
        + "%s    konten = r.stdout.strip() or r.stderr.strip() or \"Tidak ada hasil.\"\n" % indent
        + "%s    next_node = agen\n" % indent
    )

    teks = teks[:start] + blok + teks[end:]

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_webcli_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang. Restart web server.")


if __name__ == "__main__":
    main()
