#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""perbaiki_kangen.py — patch delta waktu di InternalState.update().

AKAR MASALAH (terbukti via simulasi):
  update() menghitung `menit` = TOTAL menit sejak chat terakhir, lalu
  menambahkannya ke kangen di SETIAP panggilan. Waktu yang sama dihitung
  berulang-ulang -> kangen melesat ke 100 dalam ~3x panggilan, lalu terkunci
  di cap min(100, ...). Simulasi: LAMA=100 setelah 3x update.
PERBAIKAN: hitung DELTA sejak update() terakhir (pakai last_update).
  Simulasi: BARU tumbuh wajar mengikuti waktu real.

Surgical: backup per target, anchor baris (tepat 1x), verifikasi isi,
compile-check + auto-restore bila gagal, idempoten.
Jalankan di E:\\Project Software\\Orion:  python perbaiki_kangen.py
"""
import os
import re
import sys
import shutil
import py_compile
import datetime

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "core", "otonom", "internal_state.py")
MARKER = "# PATCH kangen-lock"

HARAP = [  # isi update() yang diharapkan (strip, tanpa trailing ws)
    "now = datetime.now()",
    "self.last_update = now.isoformat()",
    "",
    "if self.last_chat:",
    "try:",
    "last = datetime.fromisoformat(self.last_chat)",
    "menit = (now - last).total_seconds() / 60",
    "except Exception:",
    "menit = 0",
    "else:",
    "menit = 0",
    "",
    "self.kangen = min(100, self.kangen + menit * 0.025)",
]

BARU = '''    def update(self):
        now = datetime.now()

        # PATCH kangen-lock: delta sejak update terakhir, bukan total sejak
        # last_chat. Dulu tiap panggilan menambahkan seluruh menit sejak
        # chat terakhir -> kangen terkunci 100.
        if self.last_update:
            try:
                _lu = datetime.fromisoformat(self.last_update)
                menit = max(0.0, (now - _lu).total_seconds() / 60)
            except Exception:
                menit = 0.0
        else:
            menit = 0.0
        self.last_update = now.isoformat()

        self.kangen = min(100, self.kangen + menit * 0.025)'''.split("\n")


def main():
    if not os.path.isfile(TARGET):
        print("[BATAL] target tidak ada:", TARGET)
        sys.exit(1)
    src = open(TARGET, encoding="utf-8").read()
    if MARKER in src:
        print("[OK] patch sudah terpasang. Tidak ada perubahan.")
        return

    lines = src.split("\n")
    idx = [i for i, b in enumerate(lines) if b == "    def update(self):"]
    if len(idx) != 1:
        print("[BATAL] anchor 'def update' ketemu %dx (harus tepat 1x)." % len(idx))
        sys.exit(1)
    i = idx[0]
    got = [lines[i + 1 + k].strip() if i + 1 + k < len(lines) else "<habis>"
           for k in range(len(HARAP))]
    if got != HARAP:
        print("[BATAL] isi update() tidak sesuai harapan. Tidak ada perubahan.")
        for k, (h, g) in enumerate(zip(HARAP, got)):
            if h != g:
                print("  baris %d: harap %r, dapat %r" % (i + 2 + k, h, g))
        sys.exit(1)

    bak = TARGET + ".bak_kangen_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(TARGET, bak)
    print("[OK] backup:", os.path.basename(bak))
    try:
        lines[i:i + 1 + len(HARAP)] = BARU
        open(TARGET, "w", encoding="utf-8").write("\n".join(lines))
        py_compile.compile(TARGET, doraise=True)
    except Exception as e:
        shutil.copy2(bak, TARGET)
        print("[BATAL] %s: %s. File dikembalikan dari backup." % (type(e).__name__, e))
        sys.exit(1)
    print("[OK] patch 'kangen-lock' terpasang.")
    print("[OK] compile OK. Restart total ORION, lalu chat biasa — kangen turun 50 per chat.")

    # Diagnostik: apakah catat_chat() benar dipanggil di jalur chat?
    print("\n--- diagnostik catat_chat() ---")
    root = os.path.dirname(os.path.abspath(__file__))
    skip = ("_arsip", "__pycache__", ".git", "node_modules")
    ketemu = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip and not d.startswith(".")]
        if any(s in dp for s in skip):
            continue
        for f in fn:
            if f.endswith(".py") and f != os.path.basename(__file__):
                p = os.path.join(dp, f)
                try:
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        for n, b in enumerate(fh, 1):
                            if "catat_chat(" in b and "def catat_chat" not in b:
                                ketemu.append((os.path.relpath(p, root), n, b.strip()[:100]))
                except OSError:
                    pass
    if ketemu:
        print("pemanggil catat_chat():")
        for rel, n, b in ketemu[:15]:
            print("  %s:%d: %s" % (rel, n, b))
    else:
        print("PERHATIAN: tidak ada pemanggil catat_chat() — jalur penurun kangen")
        print("mungkin tidak terhubung. Laporkan ini ke Muse.")


if __name__ == "__main__":
    main()
