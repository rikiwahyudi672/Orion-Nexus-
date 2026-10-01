#!/usr/bin/env python3
"""rapikan_tahap4.py -- Bersih-bersih file LAIN di root ORION (tahap 4).

Cara pakai (dari folder E:\\Project Software\\Orion):
    python rapikan_tahap4.py        -> LAPORAN saja
    python rapikan_tahap4.py --ya   -> arsipkan yang AMAN ke _arsip/tahap4/

Aturan:
- File INTI tidak pernah disentuh (ditambah orion_hidup.py + orion_supervisor.py).
- Untuk tiap file LAIN *.py: cek apakah diacu (import/nama) oleh file INTI,
  file .bat, atau cron. Kalau tidak diacu di mana-mana -> AMAN.
- Yang AMAN dipindah ke _arsip/tahap4/ + manifest. TIDAK ada hapus permanen.
- Yang PERLU CEK cuma dilaporin, tidak disentuh.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INTI = {
    "orion.py",
    "orion_hidup.py",
    "orion_supervisor.py",
    "orion_tool_loop.py",
    "orion_webchat.py",
    "lihat_layar.py",
    "nexus_kerja.py",
    ".env",
}

# Pola yang sudah ditangani tahap 3 (jangan dobel).
POLA_TAHAP3 = (
    "tambah_", "perbaiki_", "pasang_", "daftar_", "diagnosa_",
    "cek_", "pindai_", "amankan_", "colok_", "boleh_",
    "balikin_", "bersihkan_", "rapikan_",
)


def kandidat_lain():
    hasil = []
    for p in sorted(ROOT.iterdir()):
        if not p.is_file() or p.name.startswith("."):
            continue
        nama = p.name.lower()
        if nama in INTI or p.suffix.lower() == ".bat":
            continue
        if ".bak_" in nama:
            continue
        if p.suffix.lower() == ".py" and nama.startswith(POLA_TAHAP3):
            continue
        if nama == Path(__file__).name.lower():
            continue
        hasil.append(p)
    return hasil


def teks_acuan():
    """Kumpulkan teks dari file yang mungkin mengacu ke file lain."""
    teks = []
    for p in ROOT.iterdir():
        if not p.is_file():
            continue
        # File inti + bat + json config.
        if p.name.lower() in INTI or p.suffix.lower() in (".bat", ".json"):
            try:
                teks.append(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    # Juga cron_orion.py di support/.
    cron = ROOT / "support" / "cron_orion.py"
    if cron.is_file():
        try:
            teks.append(cron.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    return "\n".join(teks)


def diacu(p: Path, acuan: str) -> bool:
    stem = p.stem  # nama tanpa .py
    # Pola: import stem | from stem | "stem" | 'stem' | stem.py
    pola = re.compile(
        r"(import\s+%s\b)|(from\s+%s\b)|(['\"]%s['\"])|(%s\.py\b)"
        % (re.escape(stem), re.escape(stem), re.escape(stem), re.escape(stem))
    )
    return bool(pola.search(acuan))


def main():
    lain = kandidat_lain()
    acuan = teks_acuan()
    aman, perlu_cek = [], []
    for p in lain:
        (perlu_cek if diacu(p, acuan) else aman).append(p)

    print("=== TAHAP 4: %d file LAIN ===" % len(lain))
    print("\n[AMAN diarsip] %d file (tidak diacu di mana-mana):" % len(aman))
    for p in aman:
        print("    %s" % p.name)
    print("\n[PERLU CEK] %d file (diacu, jangan sentuh dulu):" % len(perlu_cek))
    for p in perlu_cek:
        print("    %s" % p.name)

    if "--ya" not in sys.argv:
        print("\nMode laporan saja. Tambah --ya kalau setuju yang AMAN diarsipkan.")
        return
    if not aman:
        print("\nTidak ada yang aman diarsipkan. Beres.")
        return
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    tujuan = ROOT / "_arsip" / "tahap4"
    tujuan.mkdir(parents=True, exist_ok=True)
    manifest = []
    for p in aman:
        target = tujuan / p.name
        i = 1
        while target.exists():
            target = tujuan / ("%s_%d%s" % (p.stem, i, p.suffix))
            i += 1
        shutil.move(str(p), str(target))
        manifest.append("%s -> %s" % (p.name, target.name))
        print("arsip: %s" % p.name)
    (tujuan / ("manifest_%s.txt" % t)).write_text(
        "\n".join(manifest), encoding="utf-8")
    print("\n[OK] %d file diarsipkan ke _arsip\\tahap4\\. Reversible." % len(manifest))


if __name__ == "__main__":
    main()
