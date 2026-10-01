#!/usr/bin/env python3
"""fix_cwd_dc.py -- Samakan working directory Discord bot kayak CLI.

Masalah: CLI (nexus_kerja.py) chdir ke Nexus.ai dulu sebelum import,
         Discord bot tidak. Akibatnya file persona/config keload salah.
Solusi: tambah os.chdir di blok SEDERHANA_DC sebelum import jarvis_node.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "bot" / "discord_bot.py"


def main():
    print("=== fix_cwd_dc.py ===")
    if not TARGET.is_file():
        print("GAGAL.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if "FIX_CWD_DC" in teks:
        print("[sudah] patch sudah terpasang.")
        return

    # Anchor: baris import jarvis_node di blok SEDERHANA_DC
    pola = r"([ \t]*)from agents\.jarvis import jarvis_node\n"
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor tidak ketemu. Pastikan sederhana_dc.py sudah jalan.")
        sys.exit(1)

    indent = m.group(1)
    lama = m.group(0)
    baru = (
        "%s# [FIX_CWD_DC] samakan cwd kayak CLI\n" % indent
        + "%simport os as _os_cwd\n" % indent
        + "%s_NEXUS_DIR = _os_cwd.path.dirname(_os_cwd.path.dirname(_os_cwd.path.abspath(__file__)))\n" % indent
        + "%s_os_cwd.chdir(_NEXUS_DIR)\n" % indent
        + "%simport sys as _sys_cwd\n" % indent
        + "%sif _NEXUS_DIR not in _sys_cwd.path: _sys_cwd.path.insert(0, _NEXUS_DIR)\n" % indent
        + lama
    )
    teks = teks.replace(lama, baru, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_cwd_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang. Restart bot, tes lagi.")


if __name__ == "__main__":
    main()
