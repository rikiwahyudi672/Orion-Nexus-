#!/usr/bin/env python3
"""perbaiki_cot_persona.py -- Bikin COT Jarvis pakai persona gaul, bukan formal.

Masalah:
1. Trigger perlu_cot() kelewat luas ("bikin","buat","create" ketrigger di obrolan santai)
2. Prompt COT "Kamu Jarvis. CHAIN-OF-THOUGHT." bikin output formal/kaku

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python perbaiki_cot_persona.py

Surgical, reversible, idempoten. Backup .bak_cot_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "tools" / "jarvis_brain_cot.py"

# Prompt COT baru dengan persona gaul
PROMPT_BARU = (
    '    prompt = (\n'
    '        "Kamu Jarvis, asisten gaul pake bahasa gue/lu, santai tapi pinter.\\n"\n'
    '        "Analisis perintah berikut step-by-step, tapi sampaikan dengan gaya lo yang natural, "\n'
    '        "jangan kaku kayak laporan formal.\\n"\n'
    '        "Perintah: " + perintah + "\\nKonteks: " + (konteks or "(none)") + "\\n"\n'
    '        "Output JSON:\\n"\n'
    '        "{\\"steps\\":[{\\"step\\":1,\\"reasoning\\":\\"...\\"}],"\n'
    '        "\\"kesimpulan\\":\\"...\\",\\"confidence\\":85,\\"saran\\":[\\"...\\"]}\\n"\n'
    '        "HANYA JSON:"\n'
    '    )  # COT_PERSONA\n'
)


def main():
    print("=== perbaiki_cot_persona.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    teks = TARGET.read_text(encoding="utf-8")

    if "COT_PERSONA" in teks:
        print("[sudah] patch COT persona sudah ada. Tidak diapa-apain.")
        return

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_cot_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    # 1. Hapus trigger generik dari list
    for kata in ['"bikin",', '"buat",', '"create",', '"bikin"', '"buat"', '"create"']:
        if kata in teks:
            teks = teks.replace(kata, "")
            print("  trigger %s dihapus" % kata.strip('",'))

    # Bersihkan koma ganda dan koma sebelum ]
    teks = re.sub(r",\s*,", ",", teks)
    teks = re.sub(r",\s*\n(\s*)\]", r"\n\1]", teks)

    # 2. Ganti prompt COT
    # Cari baris: prompt = "Kamu Jarvis. CHAIN-OF-THOUGHT...
    # sampai baris yang berakhir HANYA JSON:"
    pola = re.compile(
        r'^(\s*)prompt = "Kamu Jarvis\. CHAIN-OF-THOUGHT\..*?HANYA JSON:"\s*$',
        re.MULTILINE | re.DOTALL,
    )
    m = pola.search(teks)
    if m:
        indent = m.group(1)
        # Sesuaikan indentasi prompt baru
        pb = PROMPT_BARU.replace("    prompt", indent + "prompt")
        teks = teks[: m.start()] + pb.rstrip("\n") + teks[m.end():]
        print("  prompt COT diganti ke gaya gaul")
    else:
        # Fallback: cari baris prompt yang mengandung CHAIN-OF-THOUGHT
        garis = teks.splitlines(keepends=True)
        for i, b in enumerate(garis):
            if 'prompt = "Kamu Jarvis. CHAIN-OF-THOUGHT.' in b:
                indent = b[: len(b) - len(b.lstrip())]
                pb = PROMPT_BARU.replace("    prompt", indent + "prompt")
                garis[i] = pb
                teks = "".join(garis)
                print("  prompt COT diganti (fallback)")
                break
        else:
            print("  WARNING: prompt tidak ketemu")

    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] COT persona terpasang, compile OK.")


if __name__ == "__main__":
    main()
