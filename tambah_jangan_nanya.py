#!/usr/bin/env python3
"""tambah_jangan_nanya.py -- Tambah aturan JANGAN KEBANYAKAN NANYA ke JUDGMENT.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_jangan_nanya.py

Sisip setelah sub-bullet terakhir blok JUDGMENT (sebelum section MEMORI).
Surgical, reversible, idempoten. Backup .bak_nanya_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

TAMBAHAN = [
    "  - JANGAN KEBANYAKAN NANYA: nanya itu HANYA buat tugas yang kompleks dan berbobot (ambigu, berisiko, irreversible, butuh keputusan besar).",
    "  - Kalau aksinya ringan, reversible, dan jawabannya jelas 'iya' (bikin surat, kasih ide, ingetin sesuatu), JANGAN nanya 'mau nggak?'. Langsung kerjain, kasih kejutan.",
    "  - Kejutan yang manis lebih berharga dari izin yang membosankan.",
]

ANCHOR_AWAL = "JUDGMENT: KAPAN GAS"
ANCHOR_AKHIR = "MEMORI: INGAT DAN PAKAI"


def main():
    print("=== tambah_jangan_nanya.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("JANGAN KEBANYAKAN NANYA" in b for b in garis):
        print("[sudah] aturan sudah ada. Tidak diapa-apain.")
        return

    i_awal = i_akhir = None
    for i, b in enumerate(garis):
        if ANCHOR_AWAL in b and i_awal is None:
            i_awal = i
        if ANCHOR_AKHIR in b and i_awal is not None:
            i_akhir = i
            break
    if i_awal is None or i_akhir is None:
        print("GAGAL: anchor tidak ketemu. Tidak ada perubahan.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_nanya_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    eol = "\n"
    blok = [l + eol for l in TAMBAHAN]
    # Sisip tepat sebelum section MEMORI (akhir blok JUDGMENT).
    baru = garis[:i_akhir] + blok + garis[i_akhir:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] aturan JANGAN KEBANYAKAN NANYA terpasang, compile OK.")


if __name__ == "__main__":
    main()
