#!/usr/bin/env python3
"""perbaiki_bridge_path.py -- Benerin nexus_kerja.py: kembalikan os.chdir +
sys.path yang kehapus pas patch retry, dan pindahkan ke dalam loop.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python perbaiki_bridge_path.py

Surgical, reversible, idempoten. Backup .bak_bpath_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "nexus_kerja.py"


def main():
    print("=== perbaiki_bridge_path.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)
    teks = "".join(garis)

    if "os.chdir(NEXUS_DIR)" in teks and "sys.path.insert(0, NEXUS_DIR)" in teks:
        # Cek apakah keduanya ada DI DALAM fungsi nexus_kerja (bukan cuma di docstring)
        # Kalau sudah ada dan posisinya benar (sebelum import_module), skip
        idx_chdir = teks.find("os.chdir(NEXUS_DIR)")
        idx_import = teks.find("importlib.import_module(mod_name)")
        if 0 < idx_chdir < idx_import:
            print("[sudah] os.chdir + sys.path sudah benar. Tidak diapa-apain.")
            return

    # Cari blok retry yang rusak (tanpa chdir/sys.path)
    # Anchor: "# maksimal 2x percobaan"
    idx_retry = None
    for i, b in enumerate(garis):
        if "maksimal 2x percobaan" in b:
            idx_retry = i
            break
    if idx_retry is None:
        print("GAGAL: blok retry tidak ketemu.")
        sys.exit(1)

    # Cari "    try:" tepat sebelum komentar retry
    idx_try = None
    for i in range(idx_retry, -1, -1):
        if re.match(r"^    try:$", garis[i].rstrip("\n")):
            idx_try = i
            break
    if idx_try is None:
        print("GAGAL: try tidak ketemu.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_bpath_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    eol = "\n"
    # Sisipkan chdir + sys.path SETELAH "    try:" dan SEBELUM komentar retry
    sisipan = [
        "        os.chdir(NEXUS_DIR)  # worker baca path relatif (prompts/, .env)" + eol,
        "        if NEXUS_DIR not in sys.path:" + eol,
        "            sys.path.insert(0, NEXUS_DIR)" + eol,
    ]
    baru = garis[:idx_try + 1] + sisipan + garis[idx_try + 1:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] os.chdir + sys.path dikembalikan, compile OK.")


if __name__ == "__main__":
    main()
