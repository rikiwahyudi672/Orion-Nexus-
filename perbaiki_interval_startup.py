#!/usr/bin/env python3
"""perbaiki_interval_startup.py -- Anti-spam interval pas restart.

Bug: _last_run (dict memori) kosong tiap engine restart, jadi semua
interval aktif langsung dianggap kelewat dan nembak bareng pas startup.

Fix: pas jalankan() mulai, isi _last_run dengan waktu sekarang untuk
semua interval aktif. Interval baru nembak setelah durasinya beneran
terlewati, bukan langsung pas startup.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python perbaiki_interval_startup.py

Target: support/inisiatif_engine.py
Surgical, reversible, idempoten. Backup .bak_ispam_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "support" / "inisiatif_engine.py"

PATCH_LINES = [
    "    # FIX 01/10: anti-spam interval pas startup.",
    "    # Isi _last_run dgn waktu sekarang biar interval nggak langsung",
    "    # nembak bareng pas engine restart. Interval baru jalan setelah",
    "    # durasinya beneran terlewati.",
    "    try:",
    "        _lr = globals().setdefault(\"_last_run\", {})",
    "        _mnit = int(time.time() / 60)",
    "        for _it in config.get(\"interval\", []):",
    "            if _it.get(\"aktif\") and _it.get(\"id\"):",
    "                _lr[\"interval_\" + str(_it[\"id\"])] = _mnit",
    "    except Exception:",
    "        pass",
    "",
]

ANCHOR_RE = r"^    _running = True$"


def main():
    print("=== perbaiki_interval_startup.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("anti-spam interval pas startup" in b for b in garis):
        print("[sudah] fix anti-spam sudah ada. Tidak diapa-apain.")
        return

    idx_anchor = None
    for i, b in enumerate(garis):
        if re.match(ANCHOR_RE, b.rstrip("\n")):
            idx_anchor = i
            break
    if idx_anchor is None:
        print("GAGAL: anchor '_running = True' tidak ketemu. Tidak ada perubahan.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_ispam_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip setelahnya" % (idx_anchor + 1))

    eol = "\n"
    blok = [l + eol for l in PATCH_LINES]
    baru = garis[:idx_anchor + 1] + blok + garis[idx_anchor + 1:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] fix anti-spam terpasang, compile OK.")


if __name__ == "__main__":
    main()
