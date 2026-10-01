#!/usr/bin/env python3
"""perbaiki_strip_none.py -- Cari .strip() yang rawan None di orion_tool_loop.py
dan tambahkan guard.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python perbaiki_strip_none.py
    python perbaiki_strip_none.py --scan   (cuma lihat, nggak ubah)

Surgical, reversible, idempoten. Backup .bak_strip_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"


def cari_strip_riskan(garis):
    """Cari baris .strip() yang variabelnya belum jelas bukan-None."""
    hasil = []
    for i, b in enumerate(garis):
        s = b.strip()
        # Skip baris kosong, komentar
        if not s or s.startswith("#"):
            continue
        # Cari pola: <var>.strip() di mana <var> bukan string literal
        # dan baris ini bukan bagian dari "if x:" guard yang sudah ada
        m = re.search(r"(\w+)\.strip\(\)", b)
        if m:
            var = m.group(1)
            # Skip kalau var adalah string literal atau hasil .get() dengan default
            # Ini heuristik sederhana — tandai semua, biar user cek
            hasil.append((i, b.rstrip("\n"), var))
    return hasil


def main():
    print("=== perbaiki_strip_none.py ===")
    mode_scan = "--scan" in sys.argv

    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)
    temuan = cari_strip_riskan(garis)

    print("Ditemukan %d pemanggilan .strip():" % len(temuan))
    for i, b, var in temuan[:20]:
        print("  baris %d [%s]: %s" % (i + 1, var, b.strip()[:70]))

    if mode_scan:
        print("\nMode scan — tidak ada perubahan.")
        return

    if not temuan:
        print("[sudah] tidak ada .strip() yang perlu diperbaiki.")
        return

    # Untuk patch otomatis, kita cari pola berbahaya:
    # baris seperti:  x = sesuatu.strip()  atau  return sesuatu.strip()
    # di mana 'sesuatu' adalah hasil .get() tanpa default atau variabel lain
    #
    # Karena terlalu berisiko patch buta, script ini HANYA nambahin
    # helper aman dan ngasih tau user. Patch manual tetap disarankan
    # untuk kasus spesifik.
    #
    # Tapi ada satu pola yang aman dipatch: .get("...").strip()
    # -> .get("...", "").strip()  ATAU  (x or "").strip()

    pola_get_strip = re.compile(r'(\w+(?:\.\w+)*\.get\(["\'][^"\']+["\']\))\.strip\(\)')

    diubah = 0
    baru = []
    for b in garis:
        m = pola_get_strip.search(b)
        if m:
            get_part = m.group(1)
            # Skip kalau .get() sudah punya default (ada koma di dalam)
            if "," in get_part:
                baru.append(b)
                continue
            b2 = b.replace(
                get_part + ".strip()",
                "(" + get_part + ' or "").strip()'
            )
            if b2 != b:
                diubah += 1
                b = b2
        baru.append(b)

    if diubah == 0:
        print("\nTidak ada pola .get().strip() yang berisiko.")
        print("Semua .strip() tampaknya sudah aman atau butuh cek manual.")
        print("Jalankan dengan --scan untuk lihat daftar lengkap.")
        return

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_strip_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("\nbackup: %s" % bak.name)

    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] %d pola .get().strip() diamankan, compile OK." % diubah)


if __name__ == "__main__":
    main()
