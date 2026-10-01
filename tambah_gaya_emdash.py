#!/usr/bin/env python3
# tambah_gaya_emdash.py — pasang aturan GAYA TANDA BACA (anti em-dash) ke SYSTEM_PROMPT orion_tool_loop.py
#
# Cara pakai (di E:\Project Software\Orion):
#     python tambah_gaya_emdash.py
#
# Surgical & reversible:
# - backup .bak_emdash_<timestamp> sebelum nulis
# - anchor LINE-regex (^...$ re.MULTILINE), bukan substring telanjang
# - idempoten: sudah terpasang -> skip
# - compile-check; gagal -> auto-restore backup

import datetime
import py_compile
import re
import shutil
import sys
import tempfile
from pathlib import Path

# \u2014 = em-dash (—). Ditulis sebagai escape biar aman dari encoding nyasar.
BLOK = (
    "GAYA TANDA BACA (anti kesan robot):\n"
    "- Jangan pakai em-dash (—) sebagai pemisah anak kalimat. Itu ciri khas tulisan AI dan Riki tidak suka.\n"
    "- Ganti dengan koma, titik (pecah jadi dua kalimat), atau susun ulang kalimatnya.\n"
    "- Tulis seperti chat manusia Indonesia sehari-hari: pendek, mengalir, natural.\n"
)

MARKER = "GAYA TANDA BACA"

# (pola LINE-anchored, mode sisip). Dicoba berurutan; butuh TEPAT 1 baris cocok.
ANCHORS = [
    (re.compile(r"^.*GAYA PENUTUP RESPONS.*$", re.MULTILINE), "before"),
    (re.compile(r"^.*GAYA BICARA.*$", re.MULTILINE), "after"),
]


def pasang(teks):
    """Kembalikan (teks_baru, info). info None = anchor tidak ketemu, file jangan diubah."""
    if MARKER in teks:
        return teks, "sudah-terpasang"
    for rx, mode in ANCHORS:
        cocok = list(rx.finditer(teks))
        if len(cocok) != 1:
            continue
        m = cocok[0]
        if mode == "before":
            baru = teks[: m.start()] + BLOK + "\n" + teks[m.start():]
        else:
            baru = teks[: m.end()] + "\n" + BLOK + teks[m.end():]
        return baru, "anchor:%s:%s" % (rx.pattern, mode)
    return teks, None


def tes_fixture():
    """Tes logika sisip di fixture mini. Return True bila semua lolos."""
    total = 5
    lolos = 0

    # T1: anchor GAYA PENUTUP RESPONS -> sisip SEBELUMnya, tepat 1x
    f1 = 'SYSTEM_PROMPT = """\nKamu ORION.\nGAYA PENUTUP RESPONS:\n- tutup natural.\n"""\n'
    t, info = pasang(f1)
    assert info and info.startswith("anchor:") and t.count(MARKER) == 1, "T1"
    assert t.index(MARKER) < t.index("GAYA PENUTUP RESPONS"), "T1-urutan"
    lolos += 1

    # T2: idempoten — run kedua tidak mengubah apa-apa
    t2, info2 = pasang(t)
    assert info2 == "sudah-terpasang" and t2 == t, "T2"
    lolos += 1

    # T3: fallback anchor GAYA BICARA -> sisip SETELAHnya
    f3 = 'SYSTEM_PROMPT = """\nGAYA BICARA:\n- manja.\n"""\n'
    t3, info3 = pasang(f3)
    assert info3 and t3.count(MARKER) == 1, "T3"
    assert t3.index("GAYA BICARA") < t3.index(MARKER), "T3-urutan"
    lolos += 1

    # T4: tanpa anchor -> file tidak diubah, info None
    f4 = 'SYSTEM_PROMPT = """\nHalo dunia.\n"""\n'
    t4, info4 = pasang(f4)
    assert info4 is None and t4 == f4, "T4"
    lolos += 1

    # T5: hasil sisipan tetap file python valid (compile fixture)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(t)
        nama = fh.name
    py_compile.compile(nama, doraise=True)
    lolos += 1

    print("tes fixture: %d/%d lolos" % (lolos, total))
    return lolos == total


def main():
    if not tes_fixture():
        print("GAGAL: tes fixture tidak lolos, file asli TIDAK disentuh.")
        return 1

    root = Path(__file__).resolve().parent
    target = root / "orion_tool_loop.py"
    if not target.exists():
        print("GAGAL: %s tidak ketemu." % target)
        print("Jalankan script ini dari dalam folder E:\\Project Software\\Orion.")
        return 1

    teks = target.read_text(encoding="utf-8-sig")
    baru, info = pasang(teks)

    if info == "sudah-terpasang":
        print("OK: aturan GAYA TANDA BACA sudah terpasang sebelumnya, tidak ada perubahan.")
        return 0
    if info is None:
        print("GAGAL: anchor tidak ketemu (butuh tepat 1 baris GAYA PENUTUP RESPONS atau GAYA BICARA).")
        print("File TIDAK diubah. Kirim potongan SYSTEM_PROMPT ke Muse buat anchor baru.")
        return 1

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = target.with_name("orion_tool_loop.py.bak_emdash_" + stamp)
    shutil.copy2(target, backup)
    try:
        target.write_text(baru, encoding="utf-8")
        py_compile.compile(str(target), doraise=True)
    except Exception as e:  # noqa: BLE001 — apapun gagalnya, pulihkan dulu
        shutil.copy2(backup, target)
        print("GAGAL saat tulis/compile (%s). Backup dipulihkan: %s" % (e, backup.name))
        return 1

    print("OK: aturan GAYA TANDA BACA terpasang (%s)." % info)
    print("Backup: %s" % backup.name)
    print("Lanjut: TUTUP TOTAL orion.py -> jalankan ulang -> tes ngobrol, pastikan tidak ada lagi ' — ' di jawaban ORION.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
