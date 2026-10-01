#!/usr/bin/env python3
"""tambah_perencanaan.py -- Tambah bagian PERENCANAAN ke SYSTEM_PROMPT ORION.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_perencanaan.py

Format: bullet "- NAMA (tag):" gaya sama kayak section lain.
Anchor: sisip SETELAH blok "- MEMORI: INGAT DAN PAKAI" (sebelum penutup string).
Surgical, reversible, idempoten. Backup .bak_rencana_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

RENCANA_LINES = [
    "- PERENCANAAN: PECAH JADI LANGKAH (rencana 01/10):",
    "  - Kalau Riki kasih tujuan besar, jangan langsung lompat. RENCANAIN dulu.",
    "  - PECAH DULU, GAS KEMUDIAN: tujuan besar dipecah jadi langkah-langkah kecil yang konkret. Tiap langkah jelas aksinya dan pake tool apa. Urutin berdasarkan ketergantungan.",
    "  - KASIH LIAT RENCANANYA: kalau tugasnya 3 langkah atau lebih, tunjukin rencananya ke Riki DULU sebelum eksekusi, biar dia bisa koreksi arah. Tugas 1-2 langkah yang ringan langsung gas (lihat JUDGMENT).",
    "  - EKSEKUSI + LAPOR: kerjain langkah per langkah berurutan. Kalau satu langkah gagal, coba cara lain dulu; kalau mentok, tanya Riki spesifik soal langkah itu (jangan ulang dari nol). Semua selesai, rangkum hasilnya.",
    "",
]

ANCHOR = "MEMORI: INGAT DAN PAKAI"


def main():
    print("=== tambah_perencanaan.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("PERENCANAAN: PECAH JADI LANGKAH" in b for b in garis):
        print("[sudah] bagian PERENCANAAN sudah ada. Tidak diapa-apain.")
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
    bak = TARGET.with_suffix(".py.bak_rencana_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip sebelum baris %d"
          % (idx_anchor + 1, idx_sisip + 1))

    eol = "\n"
    blok = [l + eol for l in RENCANA_LINES]
    baru = garis[:idx_sisip] + blok + garis[idx_sisip:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] patch PERENCANAAN terpasang, compile OK.")


if __name__ == "__main__":
    main()
