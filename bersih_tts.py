#!/usr/bin/env python3
"""bersih_tts.py -- Hapus file TTS lama yang menuhin disk.

Cari file audio hasil TTS (mp3/wav/ogg) yang lebih dari 1 hari,
tampilkan ukuran, hapus dengan konfirmasi.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python bersih_tts.py            # lihat dulu
    python bersih_tts.py --ya       # hapus beneran
"""

import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
CANDIDATE_DIRS = ["output", "output/tts", "output/voice", "data/tts", "temp", "tmp"]
EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".opus", ".webm"}
UMUR_HARI = 1


def cari():
    ketemu = []
    for d in CANDIDATE_DIRS:
        p = BASE / d
        if not p.is_dir():
            continue
        for f in p.rglob("*"):
            if f.is_file() and f.suffix.lower() in EXTS:
                umur = (time.time() - f.stat().st_mtime) / 86400
                if umur >= UMUR_HARI:
                    ketemu.append((f, f.stat().st_size, umur))
    # juga cari di root dengan pola tts_*
    for f in BASE.glob("tts_*"):
        if f.is_file() and f.suffix.lower() in EXTS:
            umur = (time.time() - f.stat().st_mtime) / 86400
            if umur >= UMUR_HARI:
                ketemu.append((f, f.stat().st_size, umur))
    return sorted(ketemu, key=lambda x: -x[1])


def main():
    files = cari()
    if not files:
        print("Bersih. Tidak ada file TTS lama.")
        return
    total = sum(s for _, s, _ in files)
    print(f"Ketemu {len(files)} file TTS lama (>={UMUR_HARI} hari):")
    for f, s, u in files[:20]:
        print(f"  {s/1024/1024:.1f} MB  {u:.0f}h  {f.relative_to(BASE)}")
    if len(files) > 20:
        print(f"  ... dan {len(files)-20} lagi")
    print(f"Total: {total/1024/1024:.1f} MB")

    if "--ya" not in sys.argv:
        print("\nJalankan dengan --ya untuk hapus.")
        return
    for f, _, _ in files:
        try:
            f.unlink()
        except Exception as e:
            print(f"Gagal {f.name}: {e}")
    print(f"[OK] {len(files)} file dihapus.")


if __name__ == "__main__":
    main()
