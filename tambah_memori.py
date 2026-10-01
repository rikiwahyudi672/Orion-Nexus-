#!/usr/bin/env python3
"""tambah_memori.py -- Tambah bagian MEMORI ke SYSTEM_PROMPT ORION.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_memori.py

Format: bullet "- NAMA (tag):" gaya sama kayak section lain.
Anchor: sisip SETELAH blok "- JUDGMENT: KAPAN GAS" (sebelum penutup string).
Surgical, reversible, idempoten. Backup .bak_memori_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

MEMORI_LINES = [
    "- MEMORI: INGAT DAN PAKAI (memori 01/10):",
    "  - Kamu punya ingatan jangka panjang. Jangan cuma nyimpen, PAKAI.",
    "  - INGAT SEBELUM BERTINDAK: sebelum jawab atau eksekusi, tanya ke diri sendiri: 'pernah ngalamin hal mirip nggak?' Kalau ada ingatan relevan, pakai buat bikin keputusan lebih bagus. Jangan nunggu ditanya baru nginget.",
    "  - HUBUNGKAN MASA LALU KE SEKARANG: kalau situasi sekarang mirip yang dulu, sebutin ('kayak waktu itu...'). Pelajaran dari koreksi Riki itu kompas, bukan arsip mati.",
    "  - INGETIN RIKI PROAKTIF: kalau ada info penting dari dulu yang relevan sekarang, sampaikan. Jangan asumsi Riki inget semuanya. Kadang dia lupa, tugasmu ngingetin, bukan nunggu dia nanya.",
    "",
]

ANCHOR = "JUDGMENT: KAPAN GAS"


def main():
    print("=== tambah_memori.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("MEMORI: INGAT DAN PAKAI" in b for b in garis):
        print("[sudah] bagian MEMORI sudah ada. Tidak diapa-apain.")
        return

    idx_anchor = None
    for i, b in enumerate(garis):
        if ANCHOR in b:
            idx_anchor = i
            break
    if idx_anchor is None:
        print("GAGAL: anchor '%s' tidak ketemu. Tidak ada perubahan." % ANCHOR)
        sys.exit(1)

    # Titik sisip: penutup """ pertama setelah anchor.
    idx_sisip = None
    for j in range(idx_anchor + 1, len(garis)):
        if '"""' in garis[j]:
            idx_sisip = j
            break
    if idx_sisip is None:
        print("GAGAL: penutup SYSTEM_PROMPT tidak ketemu. Tidak ada perubahan.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_memori_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip sebelum baris %d"
          % (idx_anchor + 1, idx_sisip + 1))

    eol = "\n"
    blok = [l + eol for l in MEMORI_LINES]
    baru = garis[:idx_sisip] + blok + garis[idx_sisip:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] patch MEMORI terpasang, compile OK.")


if __name__ == "__main__":
    main()
