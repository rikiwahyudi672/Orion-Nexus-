#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""intip_emosi.py — READ-ONLY. Menampilkan potongan kode di sekitar baris-baris
kunci emosi 'kangen'. Tidak mengubah apa pun.
Jalankan di E:\\Project Software\\Orion:  python intip_emosi.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    (r"core\otonom\internal_state.py", 1, 145),   # seluruh state machine
    (r"core\otonom\hati_nurani.py", 440, 480),    # state.kangen = 90
    (r"core\otonom\kesadaran\fenomenal\kesadaran_fenomenal.py", 120, 165),  # rasakan kangen 85
]


def main():
    for rel, a, b in TARGETS:
        p = os.path.join(ROOT, rel)
        print("\n" + "=" * 70)
        print("FILE:", rel, "(baris %d-%d)" % (a, b))
        print("=" * 70)
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError as e:
            print("  [tidak bisa dibaca: %s]" % e)
            continue
        n = len(lines)
        a = max(1, a)
        b = min(n, b)
        for i in range(a, b + 1):
            print("%4d: %s" % (i, lines[i - 1].rstrip("\n")))
    print("\nSELESAI. Copy semua output di atas, kirim ke Muse.")


if __name__ == "__main__":
    main()
