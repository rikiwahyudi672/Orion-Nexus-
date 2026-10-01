#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagnosa_emosi2.py — scanner READ-ONLY: kenapa emosi 'kangen' kekunci 100/100.
Tidak mengubah file apa pun. Hanya membaca & melaporkan.
Jalankan di E:\\Project Software\\Orion:  python diagnosa_emosi2.py
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = ("_arsip", "__pycache__", ".git", "node_modules", ".venv", "venv", "exe")


def py_files():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        if any(s in dp for s in SKIP):
            continue
        for f in fn:
            if f.endswith(".py") and f != os.path.basename(__file__):
                out.append(os.path.join(dp, f))
    return sorted(out)


def cari(pola, flags=0):
    rx = re.compile(pola, flags)
    hasil = []
    for p in py_files():
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                for i, baris in enumerate(f, 1):
                    if rx.search(baris):
                        hasil.append((p, i, baris.rstrip("\n")))
        except OSError:
            pass
    return hasil


def lapor(judul, temuan, maks=40):
    print("\n===== %s (%d ketemu) =====" % (judul, len(temuan)))
    for path, baris, teks in temuan[:maks]:
        rel = os.path.relpath(path, ROOT)
        print("  %s:%d: %s" % (rel, baris, teks.strip()[:160]))
    if len(temuan) > maks:
        print("  ... +%d lagi" % (len(temuan) - maks))


def main():
    print("ROOT:", ROOT)
    files = py_files()
    print("file .py dipindai:", len(files))

    # 1. semua penyebutan kangen
    lapor("penyebutan 'kangen'", cari(r"kangen", re.IGNORECASE))
    # 2a. assignment langsung: kangen = ... / ["kangen"] = ...
    lapor("assignment ke kangen", cari(r"kangen.{0,12}="))
    # 2b. dict literal: "kangen": ...
    lapor("dict literal kangen", cari(r"""['"]kangen['"]\s*:"""))
    # 3. definisi state emosi di RAM
    lapor("definisi state emosi", cari(r"(emosi|emotion).{0,20}=", re.IGNORECASE), maks=25)
    # 4. kode decay / penurun emosi
    lapor("kode decay/penurun", cari(r"decay|turun|berkurang|dikurang|luruh|fade|pelan|0\.9", re.IGNORECASE), maks=25)
    # 5. penulis JSON emosi
    lapor("tulis JSON emosi", cari(r"emosi.{0,30}\.json|json\.dump", re.IGNORECASE), maks=25)

    print("\nSELESAI. Copy semua output di atas, kirim ke Muse.")


if __name__ == "__main__":
    main()
