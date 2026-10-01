#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""intip_chat.py — READ-ONLY. Tampilkan kepala fungsi chat() dan pola import
InternalState di inisiatif_otonom (yang sudah wired). Tidak mengubah apa pun.
Jalankan di E:\\Project Software\\Orion:  python intip_chat.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    (r"orion_tool_loop.py", 640, 730),          # def chat(...
    (r"core\otonom\inisiatif_otonom.py", 1, 30),  # pola import
    (r"core\otonom\inisiatif_otonom.py", 108, 165),  # pakai state + catat_initiative
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
    print("\nSELESAI. Copy semua output, kirim ke Muse.")


if __name__ == "__main__":
    main()
