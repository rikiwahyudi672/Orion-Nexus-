#!/usr/bin/env python3
"""roundtable.py -- Eksperimen: 8 agent Nexus.ai ngobrol bareng.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python roundtable.py "topik diskusi" [jumlah_ronde]

Contoh:
    python roundtable.py "gimana cara bikin konten viral?" 2

Alur:
- Ronde 1: tiap agent kasih pendapat awal soal topik
- Ronde 2+: tiap agent komentarin pendapat agent lain
- Hasil: print percakapan lengkap

Catatan: ini EKSPERIMEN, bukan sistem produksi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nexus_kerja import nexus_kerja

AGENTS = ["jarvis", "arya", "tony", "juan", "zulia", "insan", "raka", "syifaa"]

# Bagi peran debat: separuh pro, separuh kontra
PERAN = {
    "jarvis": "netral (moderator, rangkum pro-kontra)",
    "arya": "PRO (dukung topik, kasih argumen kreatif)",
    "tony": "KONTRA (kritik topik, cari kelemahannya)",
    "juan": "PRO (dukung dengan data sinyal/tren)",
    "zulia": "KONTRA (kritik dengan data statistik)",
    "insan": "netral (dokumentasikan argumen kedua sisi)",
    "raka": "PRO (dukung dengan pendekatan emosional)",
    "syifaa": "KONTRA (kritik tegas, to-the-point)",
}


def tanya(agent, prompt):
    """Tanya satu agent, balikin jawabannya (dipotong biar nggak kepanjangan)."""
    try:
        hasil = nexus_kerja(agent, prompt)
        # Potong kalau kepanjangan
        if len(hasil) > 500:
            hasil = hasil[:500] + "..."
        return hasil
    except Exception as e:
        return "[error: %s]" % e


def main():
    if len(sys.argv) < 2:
        print("Pakai: python roundtable.py \"<topik>\" [ronde]")
        sys.exit(1)

    topik = sys.argv[1]
    ronde = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    print("=" * 60)
    print("ROUNDTABLE: %s" % topik)
    print("Peserta: %s" % ", ".join(AGENTS))
    print("Ronde: %d" % ronde)
    print("=" * 60)

    # Ronde 1: pendapat awal sesuai peran
    print("\n--- RONDE 1: Pendapat awal (sesuai peran) ---\n")
    print("Peran:")
    for a in AGENTS:
        print("  %s: %s" % (a.upper(), PERAN[a]))
    print()
    pendapat = {}
    for a in AGENTS:
        print("[%s mikir...]" % a)
        p = tanya(a, "Topik diskusi: %s. Peran lo: %s. Kasih pendapat singkat (2-3 kalimat) sesuai peran lo." % (topik, PERAN[a]))
        pendapat[a] = p
        print("**%s**: %s\n" % (a.upper(), p))

    # Ronde 2+: debat sesuai peran
    for r in range(2, ronde + 1):
        print("\n--- RONDE %d: Debat pro vs kontra ---\n" % r)
        # Kumpulin semua pendapat jadi konteks
        konteks = "\n".join(
            "%s bilang: %s" % (a.upper(), pendapat[a][:200])
            for a in AGENTS
        )
        for a in AGENTS:
            print("[%s mikir...]" % a)
            prompt = (
                "Debat soal: %s\n"
                "Peran lo: %s\n\n"
                "Argumen peserta lain:\n%s\n\n"
                "Sampaikan argumen lo (2-3 kalimat) SESUAI PERAN. "
                "Kalau lo PRO, serang argumen KONTRA. "
                "Kalau lo KONTRA, hancurkan argumen PRO. "
                "Kalau netral, rangkum kedua sisi dengan adil."
                % (topik, PERAN[a], konteks)
            )
            p = tanya(a, prompt)
            pendapat[a] = p  # update dengan komentar terbaru
            print("**%s**: %s\n" % (a.upper(), p))

    print("=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
