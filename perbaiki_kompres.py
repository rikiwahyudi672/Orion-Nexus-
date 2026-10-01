#!/usr/bin/env python3
"""perbaiki_kompres.py — FIX GEMA 01/10.

Masalah: kompres_konteks() memprioritaskan baris "Aku Orion" (masuk daftar
PENTING) sehingga tembok identitas dimuat di depan dan memakan jatah
max_char; memori beneran kepotong -> "... [dipotong]".

Perbaikan (3 titik, di file yang sama):
  1. "Aku Orion" keluar dari daftar PENTING.
  2. Tembok identitas dirangkum: cukup 3 baris unik pertama, sisanya dibuang.
  3. Hasil gabung = identitas (max 3) + penting + biasa.

Jalankan dari E:\\Project Software\\Orion:
    python perbaiki_kompres.py

Aman: backup otomatis (.bak_gema_*), compile-check, idempoten
(dijalankan 2x tidak dobel-patch). Rollback: copy file .bak kembali
menjadi kompresi_konteks.py.
"""
import os
import shutil
import py_compile
import sys
from datetime import datetime

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "core", "otonom", "kesadaran", "kompresi_konteks.py")

PERBAIKAN = [
    # 1. "Aku Orion" keluar dari daftar PENTING
    ('''        "Aku Orion", "Rumah", "Emosi", "Tubuh",''',
     '''        # FIX GEMA 01/10: "Aku Orion" keluar dari PENTING (identitas max 3 baris, lihat atas).
        "Rumah", "Emosi", "Tubuh",'''),
    # 2. Rangkum tembok identitas tepat setelah split baris
    ('''    # Split per baris
    lines = konteks.split("\\n")''',
     '''    # Split per baris
    lines = konteks.split("\\n")

    # FIX GEMA 01/10: tembok identitas cukup 3 baris unik pertama.
    # Dulu puluhan baris "Aku Orion..." lolos dedup (beda teks dikit) lalu
    # dimuat di depan sebagai "penting" hingga memakan jatah max_char.
    import re as _re_gema
    _pola_ident = _re_gema.compile(r'aku\\s+orion', _re_gema.IGNORECASE)
    _ident, _sudah_ident, _sisa = [], set(), []
    for _b in lines:
        if _pola_ident.search(_b):
            _k = _b.strip().lower()
            if _k not in _sudah_ident and len(_ident) < 3:
                _sudah_ident.add(_k)
                _ident.append(_b)
            # selebihnya dibuang — identitas cukup disebut sekali
        else:
            _sisa.append(_b)
    lines = _sisa'''),
    # 3. Identitas (max 3) sekali di depan, lalu penting, lalu biasa
    ('''    hasil = penting_lines + biasa_lines''',
     '''    # FIX GEMA 01/10: identitas (max 3 baris) sekali di depan, lalu penting, lalu biasa
    hasil = _ident + penting_lines + biasa_lines'''),
]


def main():
    if not os.path.isfile(TARGET):
        print("BATAL: tidak ketemu: %s" % TARGET)
        return
    with open(TARGET, encoding="utf-8") as f:
        isi = f.read()
    if "FIX GEMA 01/10" in isi:
        print("Sudah dipatch sebelumnya — tidak ada yang diubah.")
        return
    for old, new in PERBAIKAN:
        c = isi.count(old)
        if c != 1:
            print("BATAL: pola tidak ketemu persis 1x (ketemu %d). File tidak diubah." % c)
            print("Pola: %s" % old[:70].replace("\n", "\\n"))
            return
        isi = isi.replace(old, new)
    bak = TARGET + ".bak_gema_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(TARGET, bak)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(isi)
    py_compile.compile(TARGET, doraise=True)
    print("OK — dipatch + compile lolos.")
    print("Backup: %s" % bak)
    print("Rollback: copy file .bak di atas kembali menjadi kompresi_konteks.py")


if __name__ == "__main__":
    main()
