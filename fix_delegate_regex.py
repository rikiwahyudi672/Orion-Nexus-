#!/usr/bin/env python3
"""fix_delegate_regex.py -- Delegasi bisa via 'suruh/minta/tolong <agen>'."""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "tools" / "jarvis_intent.py"
TAG = "FIX_DELEGATE_REGEX"


def main():
    print("=== fix_delegate_regex.py ===")
    teks = TARGET.read_text(encoding="utf-8")
    if TAG in teks:
        print("[sudah] terpasang.")
        return

    # Anchor: blok DELEGASI KE AGEN
    pola = (
        r"([ \t]*)# [─-]+ DELEGASI KE AGEN [─-]+\n"
        r"\1[ \t]*AGEN_NAMES = \[.*?\]\n"
        r"\1[ \t]*for agen in AGEN_NAMES:\n"
        r"\1[ \t]*m = re\.search\(rf'\^.*?\), p\)\n"
        r"\1[ \t]*if m:\n"
        r"\1[ \t]*task = m\.group\(1\)\.strip\(\)\n"
        r"\1[ \t]*return \{\"intent\": \"delegate\", \"params\": \{\"agent\": agen, \"task\": task\}\}\n"
    )
    m = re.search(pola, teks, re.DOTALL)
    if not m:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    lama = m.group(0)

    baru = (
        "%s# [%s] DELEGASI KE AGEN (support 'suruh/minta/tolong <agen>')\n" % (indent, TAG)
        + "%sAGEN_NAMES = [\"syifaa\", \"sifa\", \"tony\", \"toni\", \"arya\", \"arie\", \"juan\",\n" % indent
        + "%s              \"zulia\", \"zul\", \"insan\", \"raka\"]\n" % indent
        + "%sfor agen in AGEN_NAMES:\n" % indent
        + "%s    # Pola 1: 'arya, ...' (langsung)\n" % indent
        + "%s    m = re.search(rf'^{agen}[,\\s:]+(.+)', p)\n" % indent
        + "%s    if m:\n" % indent
        + "%s        task = m.group(1).strip()\n" % indent
        + "%s        return {\"intent\": \"delegate\", \"params\": {\"agent\": agen, \"task\": task}}\n" % indent
        + "%s    # Pola 2: 'suruh/minta/tolong/panggil <agen> ...'\n" % indent
        + "%s    m2 = re.search(rf'(?:suruh|minta|tolong|panggil|kasih\\s+tugas\\s+ke)\\s+{agen}[,\\s:]+(.+)', p)\n" % indent
        + "%s    if m2:\n" % indent
        + "%s        task = m2.group(1).strip()\n" % indent
        + "%s        return {\"intent\": \"delegate\", \"params\": {\"agent\": agen, \"task\": task}}\n" % indent
    )

    teks = teks.replace(lama, baru, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".py.bak_delegate_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang.")


if __name__ == "__main__":
    main()
