#!/usr/bin/env python3
"""tambah_kelola_agent.py -- Tambah bagian KELOLA AGENT CERDAS ke SYSTEM_PROMPT.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_kelola_agent.py

Sisip SETELAH blok DISKUSI (sebelum penutup string).
Surgical, reversible, idempoten. Backup .bak_agent_*.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "orion_tool_loop.py"

AGENT_LINES = [
    "- KELOLA AGENT CERDAS (nexus 01/10):",
    "  - Kamu membawahi 8 agent Nexus.ai: Arya, Insan, Juan, Raka, Syifaa, Tony, Zulia (worker), dan Jarvis (orchestrator).",
    "  - Kenali spesialisasi masing-masing dari pengalaman. Tugas kreatif ke yang kreatif, tugas teknis ke yang teknis. Jangan asal lempar ke siapa aja.",
    "  - Untuk tugas kompleks: pecah jadi sub-tugas, delegasikan ke beberapa agent yang pas via nexus_kerja, lalu gabungkan hasilnya jadi satu jawaban utuh.",
    "  - KASIH ARAHAN YANG JELAS: jangan cuma lempar 'bikinin X'. Kasih konteks, syarat, dan format yang dimau. Brief yang jelas menghasilkan output yang bagus.",
    "  - KALAU OUTPUT MASIH MENTAH: jangan langsung terima. Kasih feedback spesifik dan suruh revisi. Atau suruh agent lain review dan sempurnakan. Mereka bisa saling diskusi dan bangun di atas kerja masing-masing sampai hasilnya matang.",
    "  - Jarvis itu orchestrator. Kalau tugas butuh koordinasi multi-agent atau kamu nggak yakin routingnya, libatkan dia. Jangan bypass.",
    "  - Pelajari dari hasil: kalau agent A bagus buat X, inget itu dan pakai lagi lain kali. Makin lama routingmu makin tajam.",
    "",
]

ANCHOR = "DISKUSI: JADI TEMAN MIKIR"


def main():
    print("=== tambah_kelola_agent.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    if any("KELOLA AGENT CERDAS" in b for b in garis):
        print("[sudah] bagian KELOLA AGENT sudah ada. Tidak diapa-apain.")
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
    bak = TARGET.with_suffix(".py.bak_agent_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)
    print("[OK] anchor baris %d, sisip sebelum baris %d"
          % (idx_anchor + 1, idx_sisip + 1))

    eol = "\n"
    blok = [l + eol for l in AGENT_LINES]
    baru = garis[:idx_sisip] + blok + garis[idx_sisip:]
    TARGET.write_text("".join(baru), encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] patch KELOLA AGENT terpasang, compile OK.")


if __name__ == "__main__":
    main()
