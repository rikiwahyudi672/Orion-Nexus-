#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sambung_catat_chat.py — sambungkan InternalState.catat_chat() ke chat().

AKAR MASALAH: catat_chat() (kangen -50, kepo -40, bosan -30, last_chat=now)
tidak pernah dipanggil di jalur production — cuma di blok TEST. Akibatnya
kangen tidak pernah turun saat Riki chat.
PERBAIKAN: panggil muat()->catat_chat()->simpan() di awal chat()
orion_tool_loop.py. Dibungkus try/except agar emosi tidak pernah
merusak chat.

Surgical: backup per target, anchor baris (tepat 1x), verifikasi isi,
compile-check + auto-restore bila gagal, idempoten.
Jalankan di E:\\Project Software\\Orion:  python sambung_catat_chat.py
"""
import os
import sys
import shutil
import py_compile
import datetime

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "orion_tool_loop.py")
MARKER = "# PATCH catat-chat"

DEF_LINE = "def chat(pesan, riwayat=None, registry=None, max_putaran=MAX_PUTARAN,"
HARAP = [  # 3 baris setelah DEF_LINE (strip)
    "llm_fn=None, verbose=False):",
    '"""Satu pesan user -> jawaban akhir (dengan tool loop)."""',
    "registry = registry or bangun_registry()",
]

BLOK = '''    # PATCH catat-chat: hubungkan emosi ke tiap pesan user
    # (kangen -50, kepo -40, bosan -30, last_chat=now). try/except agar
    # pelacakan emosi tidak pernah merusak chat.
    try:
        import sys as _sys_catat
        from pathlib import Path as _Path_catat
        _oton = _Path_catat("E:/Project Software/Orion") / "core" / "otonom"
        if str(_oton) not in _sys_catat.path:
            _sys_catat.path.insert(0, str(_oton))
        from internal_state import InternalState as _InternalState
        _st_catat = _InternalState.muat()
        _st_catat.catat_chat()
        _st_catat.simpan()
    except Exception:
        pass'''.split("\n")


def main():
    if not os.path.isfile(TARGET):
        print("[BATAL] target tidak ada:", TARGET)
        sys.exit(1)
    src = open(TARGET, encoding="utf-8").read()
    if MARKER in src:
        print("[OK] patch sudah terpasang. Tidak ada perubahan.")
        return

    lines = src.split("\n")
    idx = [i for i, b in enumerate(lines) if b == DEF_LINE]
    if len(idx) != 1:
        print("[BATAL] anchor 'def chat' ketemu %dx (harus tepat 1x)." % len(idx))
        sys.exit(1)
    i = idx[0]
    got = [lines[i + 1 + k].strip() if i + 1 + k < len(lines) else "<habis>"
           for k in range(len(HARAP))]
    if got != HARAP:
        print("[BATAL] kepala chat() tidak sesuai harapan. Tidak ada perubahan.")
        for k, (h, g) in enumerate(zip(HARAP, got)):
            if h != g:
                print("  baris %d: harap %r, dapat %r" % (i + 2 + k, h, g))
        sys.exit(1)

    bak = TARGET + ".bak_catat_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(TARGET, bak)
    print("[OK] backup:", os.path.basename(bak))
    try:
        # Sisipkan BLOK setelah docstring (i+3), sebelum 'registry = ...'
        lines[i + 3:i + 3] = BLOK
        open(TARGET, "w", encoding="utf-8").write("\n".join(lines))
        py_compile.compile(TARGET, doraise=True)
    except Exception as e:
        shutil.copy2(bak, TARGET)
        print("[BATAL] %s: %s. File dikembalikan dari backup." % (type(e).__name__, e))
        sys.exit(1)
    print("[OK] patch 'catat-chat' terpasang.")
    print("[OK] compile OK. Restart total ORION — tiap chat Riki kini menurunkan kangen 50.")


if __name__ == "__main__":
    main()
