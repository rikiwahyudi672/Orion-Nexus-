#!/usr/bin/env python3
"""perbaiki_jawaban_none.py -- Guard jawaban None di orion_tool_loop.py.

Target: baris _simpan_memori(pesan, jawaban.strip()) dan return jawaban.strip()
Kalau jawaban None (LLM gagal), kasih pesan ramah, jangan crash.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python perbaiki_jawaban_none.py

Surgical, reversible, idempoten. Backup .bak_jnone_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"


def main():
    print("=== perbaiki_jawaban_none.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)
    teks = "".join(garis)

    # Cek idempoten DULU sebelum cari anchor
    if 'jawaban = jawaban or ""' in teks:
        print("[sudah] guard jawaban None sudah ada. Tidak diapa-apain.")
        return

    # Cari pola:
    #         if not nama_tool:
    #             _simpan_memori(pesan, jawaban.strip())
    #             return jawaban.strip()  # jawaban final
    idx = None
    for i, b in enumerate(garis):
        if "_simpan_memori(pesan, jawaban.strip())" in b:
            idx = i
            break
    if idx is None:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    # Cek baris sebelumnya harus "if not nama_tool:"
    if "if not nama_tool:" not in garis[idx - 1]:
        print("GAGAL: struktur tidak sesuai ekspektasi.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_jnone_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    # Dapatkan indentasi dari baris anchor
    indent = garis[idx][: len(garis[idx]) - len(garis[idx].lstrip())]
    eol = "\n"

    # Sisipkan guard SEBELUM _simpan_memori
    guard = [
        indent + 'jawaban = jawaban or ""  # guard: LLM gagal -> string kosong' + eol,
    ]

    baru = garis[:idx] + guard + garis[idx:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] guard jawaban None terpasang, compile OK.")


if __name__ == "__main__":
    main()
