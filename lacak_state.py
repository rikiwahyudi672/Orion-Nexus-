#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lacak_state.py — READ-ONLY. Lacak pemakaian InternalState di production:
di mana state dimuat/diupdate, siapa manggil catat_initiative, dan di mana
fungsi chat utama berada. Tidak mengubah apa pun.
Jalankan di E:\\Project Software\\Orion:  python lacak_state.py
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = ("_arsip", "__pycache__", ".git", "node_modules", ".venv", "venv", "exe")
ME = os.path.basename(__file__)


def py_files():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        if any(s in dp for s in SKIP):
            continue
        for f in fn:
            if f.endswith(".py") and f != ME:
                out.append(os.path.join(dp, f))
    return sorted(out)


def cari(pola):
    rx = re.compile(pola)
    hasil = []
    for p in py_files():
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                lines = fh.read().split("\n")
        except OSError:
            continue
        for n, b in enumerate(lines, 1):
            if rx.search(b):
                hasil.append((p, n, b.strip()[:130]))
    return hasil


def lapor(judul, temuan, maks=30):
    print("\n===== %s (%d) =====" % (judul, len(temuan)))
    for p, n, b in temuan[:maks]:
        print("  %s:%d: %s" % (os.path.relpath(p, ROOT), n, b))
    if len(temuan) > maks:
        print("  ... +%d lagi" % (len(temuan) - maks))


def main():
    print("ROOT:", ROOT)
    lapor("import/pakai InternalState", cari(r"internal_state|InternalState"))
    lapor("panggil .update() [kandidat state.update]", cari(r"\.update\(\)"))
    lapor("panggil catat_initiative(", cari(r"catat_initiative\("))
    lapor("definisi fungsi chat", cari(r"def (tool_loop_chat|chat|chat_orion|kirim_chat)\("))
    lapor("InternalState.muat()", cari(r"InternalState\.muat\(\)"))
    print("\nSELESAI. Copy semua output, kirim ke Muse.")


if __name__ == "__main__":
    main()
