#!/usr/bin/env python3
"""rapikan_root.py -- Bersih-bersih root folder ORION, bertahap & aman.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python rapikan_root.py            -> cuma LAPORAN, tidak mindahin apa-apa
    python rapikan_root.py --ya       -> pindahkan kandidat arsip ke _arsip/tahap3/

Aturan:
- File INTI (orion.py, orion_tool_loop.py, orion_webchat.py, lihat_layar.py,
  nexus_kerja.py, .env, *.bat) TIDAK PERNAH disentuh.
- Yang dipindah cuma: file .bak_* lama + script sekali-pakai yang kerjaannya
  sudah selesai (tambah_*, perbaiki_*, pasang_*, dst).
- Tidak ada hapus permanen: semua masuk _arsip/tahap3/ + ada manifest.
- File yang tidak dikenal (LAIN) cuma dilaporin, tidak disentuh.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Nama file inti: jangan pernah disentuh (dibanding case-insensitive).
INTI = {
    "orion.py",
    "orion_tool_loop.py",
    "orion_webchat.py",
    "lihat_layar.py",
    "nexus_kerja.py",
    ".env",
}

# Awalan nama script sekali-pakai yang kerjaannya sudah selesai.
POLA_SEKALI_PAKAI = (
    "tambah_",
    "perbaiki_",
    "pasang_",
    "daftar_",
    "diagnosa_",
    "cek_",
    "pindai_",
    "amankan_",
    "colok_",
    "boleh_",
    "balikin_",
    "bersihkan_",
    "rapikan_",
)


# File sekali-pakai yang BELUM boleh diarsip (kerjaannya belum kelar):
# - tambah_cek_riwayat.py : INGATAN langkah 2, belum dijalankan Riki
# - tambah_gaya_emdash.py : gaya em-dash, belum dijalankan Riki
# - colok_memori_loop.py  : memori v2, belum dijalankan Riki
# - amankan_skill (1).py  : sisa kerjaan --scan audit skill I/O
KECUALI = {
    "tambah_cek_riwayat.py",
    "tambah_gaya_emdash.py",
    "colok_memori_loop.py",
    "amankan_skill (1).py",
}


def kategori(p: Path) -> str:
    nama = p.name.lower()
    if nama in KECUALI:
        return "LAIN"  # dilaporin, tidak diarsipkan
    if nama in INTI or p.suffix.lower() == ".bat":
        return "INTI"
    if ".bak_" in nama:
        return "CADANGAN"
    if p.suffix.lower() == ".py" and nama.startswith(POLA_SEKALI_PAKAI):
        # Jangan arsipkan diri sendiri kalau lagi jalan.
        if nama == Path(__file__).name.lower():
            return "LAIN"
        return "SEKALI_PAKAI"
    if p.suffix.lower() == ".log":
        return "LOG"
    return "LAIN"


def pindai():
    hasil = {"INTI": [], "CADANGAN": [], "SEKALI_PAKAI": [], "LOG": [], "LAIN": []}
    for p in sorted(ROOT.iterdir()):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        hasil[kategori(p)].append(p)
    return hasil


def laporan(hasil):
    print("=== ISI ROOT: %s ===" % ROOT)
    total = sum(len(v) for v in hasil.values())
    print("Total file di root: %d\n" % total)
    for kat in ("INTI", "CADANGAN", "SEKALI_PAKAI", "LOG", "LAIN"):
        daftar = hasil[kat]
        print("[%s] %d file" % (kat, len(daftar)))
        for p in daftar[:30]:
            print("    %s" % p.name)
        if len(daftar) > 30:
            print("    ... +%d lagi" % (len(daftar) - 30))
    print()
    pindah = hasil["CADANGAN"] + hasil["SEKALI_PAKAI"]
    print("Kandidat arsip (--ya): %d file" % len(pindah))
    print("Tidak disentuh (INTI+LOG+LAIN): %d file"
          % (len(hasil["INTI"]) + len(hasil["LOG"]) + len(hasil["LAIN"])))


def arsipkan(hasil):
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    tujuan = ROOT / "_arsip" / "tahap3"
    tujuan.mkdir(parents=True, exist_ok=True)
    pindah = hasil["CADANGAN"] + hasil["SEKALI_PAKAI"]
    if not pindah:
        print("Tidak ada kandidat arsip. Beres.")
        return
    manifest = []
    for p in pindah:
        target = tujuan / p.name
        # Hindari tabrakan nama.
        i = 1
        while target.exists():
            target = tujuan / ("%s_%d%s" % (p.stem, i, p.suffix))
            i += 1
        shutil.move(str(p), str(target))
        manifest.append("%s -> %s" % (p.name, target.name))
        print("arsip: %s" % p.name)
    (tujuan / ("manifest_%s.txt" % t)).write_text(
        "\n".join(manifest), encoding="utf-8"
    )
    print("\n[OK] %d file diarsipkan ke _arsip\\tahap3\\ (manifest_%s.txt)."
          % (len(manifest), t))
    print("Tidak ada yang dihapus permanen; copy balik manual kalau perlu.")


def main():
    hasil = pindai()
    laporan(hasil)
    if "--ya" in sys.argv:
        print()
        arsipkan(hasil)
    else:
        print("\nMode laporan saja. Tambah --ya kalau setuju diarsipkan.")


if __name__ == "__main__":
    main()
