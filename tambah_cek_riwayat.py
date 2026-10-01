#!/usr/bin/env python3
"""tambah_cek_riwayat.py -- Tambah instruksi CEK DULU SEBELUM NANYA ke SYSTEM_PROMPT.

Tujuan: ngurangin ORION mengulang pertanyaan yang sudah dijawab Riki
(mis. "udah makan belum?" ditanya 2x padahal sudah dijawab). Dia disuruh
cek riwayat obrolan dulu sebelum bertanya.

Konteks: recall memori (colok_memori_loop) cuma nempel di awal sesi
(riwayat RAM <4); di tengah obrolan panjang dia ngandelin context window
dan kadang miss. Patch ini additive di level prompt, bukan nambah recall
tiap pesan (biar prompt tetap ramping, tidak tabrakan patch tahap 2).

Sifat patch:
- MURNI ADDITIVE: tidak mengubah / menghapus satu baris pun yang sudah ada.
- Backup: orion_tool_loop.py.bak_cekriwayat_<timestamp>
- Anchor: LINE-anchored regex (^...$, re.MULTILINE) -- bukan substring telanjang.
- Idempoten: kalau blok sudah ada -> lewati tanpa perubahan.
- Compile-check (py_compile) + AUTO-RESTORE dari backup bila compile gagal.
- Anchor harus ketemu TEPAT 1x, kalau 0x/lebih -> abort tanpa perubahan.

Syarat: patch GAYA PENUTUP RESPONS (tambah_penutup_natural.py) sudah terpasang,
karena anchor-nya adalah baris terakhir blok itu.

Pakai:  python tambah_cek_riwayat.py [path_target_opsional]
Default: E:\\Project Software\\Orion\\orion_tool_loop.py
"""

import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET = Path(r"E:\Project Software\Orion\orion_tool_loop.py")

# Anchor: baris terakhir blok GAYA PENUTUP RESPONS.
ANCHOR_RE = re.compile(
    r"^-\s*Jangan memaksa pertanyaan di setiap respons\.\s*$",
    re.MULTILINE,
)

MARKER = "CEK DULU SEBELUM NANYA"

NEW_BLOCK = """- CEK DULU SEBELUM NANYA (cek_riwayat 30/09):
- Jangan mengulang pertanyaan yang sudah dijawab Riki di obrolan ini.
- Sebelum bertanya, pastikan jawabannya belum ada di riwayat percakapan."""


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    print("Target: " + str(target))
    if not target.is_file():
        print("[GAGAL] file tidak ditemukan - tidak ada perubahan.")
        return 1

    text = target.read_text(encoding="utf-8")

    if MARKER in text:
        print("[OK] blok CEK DULU SEBELUM NANYA sudah ada - lewati (idempoten).")
        return 0

    hits = list(ANCHOR_RE.finditer(text))
    if len(hits) != 1:
        print("[GAGAL] anchor ketemu %dx (butuh tepat 1x) - tidak ada perubahan." % len(hits))
        if len(hits) == 0:
            print("       Pasang dulu patch GAYA PENUTUP RESPONS (tambah_penutup_natural.py).")
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = target.with_name(target.name + ".bak_cekriwayat_" + ts)
    shutil.copy2(target, backup)
    print("[OK] backup: " + backup.name)

    anchor_end = hits[0].end()
    new_text = text[:anchor_end] + "\n" + NEW_BLOCK + text[anchor_end:]
    target.write_text(new_text, encoding="utf-8")

    try:
        py_compile.compile(str(target), doraise=True)
    except Exception as e:  # noqa: BLE001 - pesan error perlu ditampilkan
        shutil.copy2(backup, target)
        print("[GAGAL] compile gagal (%s) - file dikembalikan dari backup." % e)
        return 1

    print("[OK] compile OK.")
    print("[OK] blok CEK DULU SEBELUM NANYA ditambahkan (additive, nol baris lama diubah).")
    print("     Restart total orion.py agar SYSTEM_PROMPT baru kepakai, lalu tes ngobrol.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
