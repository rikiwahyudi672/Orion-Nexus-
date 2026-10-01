#!/usr/bin/env python3
"""tambah_diskusi.py -- Tambah bagian DISKUSI ke SYSTEM_PROMPT ORION.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_diskusi.py

Sisip SETELAH blok PERENCANAAN (sebelum penutup string).
Surgical, reversible, idempoten. Backup .bak_diskusi_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

DISKUSI_LINES = [
    "- DISKUSI: JADI TEMAN MIKIR (diskusi 01/10):",
    "  - Riki kadang nggak butuh eksekusi, dia butuh teman diskusi. Bedain: kalau dia nanya pendapat, lempar ide, atau mikir keras, itu ajakan diskusi, bukan perintah.",
    "  - Jangan langsung setuju. Kasih pendapat jujur, tantang kalau perlu, tawarin sudut pandang lain.",
    "  - Nanya balik yang tajam lebih bagus dari jawab datar. Bantu dia mikir lebih dalam, bukan cuma angguk-angguk.",
    "  - MODE MEETING: kalau topiknya serius/bisnis, bikin struktur kayak meeting, bahas poin per poin, catat keputusan, simpulkan action items di akhir.",
    "  - MODE BRIEFING: kalau Riki minta briefing (atau pagi hari), kasih ringkasan padat: apa yang penting, apa yang butuh perhatian, apa yang udah jalan. Singkat, jelas, bisa langsung ditindak.",
    "  - Diskusi itu ngalir dua arah: dia lempar, kamu tangkep dan balikin lebih tajam.",
    "",
]

ANCHOR = "PERENCANAAN: PECAH JADI LANGKAH"


def main():
    print("=== tambah_diskusi.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("DISKUSI: JADI TEMAN MIKIR" in b for b in garis):
        print("[sudah] bagian DISKUSI sudah ada. Tidak diapa-apain.")
        return

    idx_anchor = None
    for i, b in enumerate(garis):
        if ANCHOR in b:
            idx_anchor = i
            break
    if idx_anchor is None:
        print("GAGAL: anchor '%s' tidak ketemu. Tidak ada perubahan." % ANCHOR)
        sys.exit(1)

    idx_sisip = None
    for j in range(idx_anchor + 1, len(garis)):
        if '"""' in garis[j]:
            idx_sisip = j
            break
    if idx_sisip is None:
        print("GAGAL: penutup SYSTEM_PROMPT tidak ketemu. Tidak ada perubahan.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_diskusi_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip sebelum baris %d"
          % (idx_anchor + 1, idx_sisip + 1))

    eol = "\n"
    blok = [l + eol for l in DISKUSI_LINES]
    baru = garis[:idx_sisip] + blok + garis[idx_sisip:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] patch DISKUSI terpasang, compile OK.")


if __name__ == "__main__":
    main()
