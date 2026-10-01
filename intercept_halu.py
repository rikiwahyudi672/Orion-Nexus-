#!/usr/bin/env python3
"""intercept_halu.py -- Hard block: jangan kasih ke LLM kalo nanya aktivitas worker."""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "agents" / "jarvis.py"
TAG = "INTERCEPT_HALU"

JAWABAN = (
    "Gue nggak tau mereka lagi ngapain sekarang bos, nggak ada live tracking. "
    "Kalo mau tau, suruh mereka lapor atau cek langsung."
)


def main():
    print("=== intercept_halu.py ===")
    if not TARGET.is_file():
        print("GAGAL.")
        sys.exit(1)
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] terpasang.")
        return

    # Anchor: def jarvis_node(state):
    pola = r"(def jarvis_node\(state\):\n)"
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    indent = "    "
    blok = (
        m.group(1)
        + "%s# [%s] hard block halu aktivitas worker\n" % (indent, TAG)
        + "%s_perintah_lower = (state.get('perintah') or '').lower()\n" % indent
        + "%s_pola_aktivitas = r'lagi\\s+(apa|ngapain|pada\\s+ngapain)'\n" % indent
        + "%s_pola_pekerja = r'pekerja|para\\s+pekerja|tim|anak\\s+buah|syifaa|tony|arya|juan|zulia|insan|raka'\n" % indent
        + "%sif re.search(_pola_aktivitas, _perintah_lower) and re.search(_pola_pekerja, _perintah_lower):\n" % indent
        + "%s    state['konten'] = \"%s\"\n" % (indent, JAWABAN)
        + "%s    state['output'] = \"%s\"\n" % (indent, JAWABAN)
        + "%s    return state\n" % indent
        + "\n"
    )
    teks = teks.replace(m.group(1), blok, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".py.bak_intercept_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang.")


if __name__ == "__main__":
    main()
