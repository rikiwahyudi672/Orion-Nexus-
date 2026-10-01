#!/usr/bin/env python3
"""fix_intercept_re.py -- Tambah import re yang kurang."""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "agents" / "jarvis.py"


def main():
    print("=== fix_intercept_re.py ===")
    teks = TARGET.read_text(encoding="utf-8")
    if "import re as _re_intercept" in teks:
        print("[sudah] terpasang.")
        return

    # Tambah import setelah blok INTERCEPT_HALU
    pola = r"([ \t]*)# \[INTERCEPT_HALU\] hard block halu aktivitas worker\n"
    m = re.search(pola, teks)
    if not m:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    indent = m.group(1)
    lama = m.group(0)
    baru = lama + "%simport re as _re_intercept\n" % indent
    teks = teks.replace(lama, baru, 1)

    # Ganti re.search jadi _re_intercept.search
    teks = teks.replace(
        "if re.search(_pola_aktivitas, _perintah_lower) and re.search(_pola_pekerja, _perintah_lower):",
        "if _re_intercept.search(_pola_aktivitas, _perintah_lower) and _re_intercept.search(_pola_pekerja, _perintah_lower):"
    )

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".py.bak_re_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang.")


if __name__ == "__main__":
    main()
