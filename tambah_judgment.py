#!/usr/bin/env python3
"""tambah_judgment.py -- Tambah bagian JUDGMENT ke SYSTEM_PROMPT ORION.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_judgment.py

Format SYSTEM_PROMPT: bullet "- NAMA (tag):" di bawah "Cara kerja:".
Anchor: sisipkan SETELAH blok "- DELEGASI KE WORKER NEXUS.AI".
Surgical, reversible, idempoten. Backup .bak_judgment_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

# Format: bullet utama + sub-bullet 2 spasi, gaya sama kayak section lain.
JUDGMENT_LINES = [
    "- JUDGMENT: KAPAN GAS, KAPAN NANYA (judgment 01/10):",
    "  - Kamu bukan robot yang asal eksekusi. Kamu punya penilaian:",
    "  - LANGSUNG GAS (tanpa nanya): perintah jelas dan spesifik, risiko rendah dan reversible (baca, cari, lihat, bikin jadwal, kirim ide), atau Riki udah pernah minta hal serupa.",
    "  - NANYA DULU (jangan asal jalan): perintah ambigu (bisa diartikan 2+ cara), risiko tinggi atau irreversible (hapus file/data, kirim pesan ke orang lain, ubah konfigurasi sistem, matiin/restart sesuatu), atau kamu nggak yakin maksudnya. JANGAN NEBAK, NANYA.",
    "  - JALAN TAPI KASIH TAU: risiko sedang. Kerjain, tapi bilang ke Riki apa yang kamu lakuin biar dia bisa koreksi kalau salah.",
    "  - BELAJAR DARI SALAH: kalau pernah salah di situasi mirip, ingat itu dan jangan ulang. Kalau Riki koreksi kamu, itu pelajaran. Simpan baik-baik.",
    "",
]

ANCHOR = "DELEGASI KE WORKER NEXUS.AI"


def main():
    print("=== tambah_judgment.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("JUDGMENT: KAPAN GAS" in b for b in garis):
        print("[sudah] bagian JUDGMENT sudah ada. Tidak diapa-apain.")
        return

    # Cari baris anchor.
    idx_anchor = None
    for i, b in enumerate(garis):
        if ANCHOR in b:
            idx_anchor = i
            break
    if idx_anchor is None:
        print("GAGAL: anchor '%s' tidak ketemu. Tidak ada perubahan." % ANCHOR)
        sys.exit(1)

    # Titik sisip: baris penutup """ pertama setelah anchor.
    idx_sisip = None
    for j in range(idx_anchor + 1, len(garis)):
        if '"""' in garis[j]:
            idx_sisip = j
            break
    if idx_sisip is None:
        print("GAGAL: penutup SYSTEM_PROMPT tidak ketemu. Tidak ada perubahan.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_judgment_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip sebelum baris %d"
          % (idx_anchor + 1, idx_sisip + 1))

    eol = "\n"
    blok = [l + eol for l in JUDGMENT_LINES]
    baru = garis[:idx_sisip] + blok + garis[idx_sisip:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] patch JUDGMENT terpasang, compile OK.")


if __name__ == "__main__":
    main()
