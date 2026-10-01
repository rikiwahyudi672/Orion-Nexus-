#!/usr/bin/env python3
"""fix_delegate2.py -- Simpler anchor."""

import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "tools" / "jarvis_intent.py"


def main():
    print("=== fix_delegate2.py ===")
    teks = TARGET.read_text(encoding="utf-8")
    if "FIX_DELEGATE2" in teks:
        print("[sudah] terpasang.")
        return

    lama = """    for agen in AGEN_NAMES:
        m = re.search(rf'^{agen}[,\\s:]+(.+)', p)
        if m:
            task = m.group(1).strip()
            return {"intent": "delegate", "params": {"agent": agen, "task": task}}"""

    baru = """    for agen in AGEN_NAMES:
        # [FIX_DELEGATE2] Pola 1: 'arya, ...' langsung
        m = re.search(rf'^{agen}[,\\s:]+(.+)', p)
        if m:
            task = m.group(1).strip()
            return {"intent": "delegate", "params": {"agent": agen, "task": task}}
        # Pola 2: 'suruh/minta/tolong/panggil <agen> ...'
        m2 = re.search(rf'(?:suruh|minta|tolong|panggil)\\s+{agen}[,\\s:]+(.+)', p)
        if m2:
            task = m2.group(1).strip()
            return {"intent": "delegate", "params": {"agent": agen, "task": task}}"""

    if lama not in teks:
        print("GAGAL: anchor tidak ketemu.")
        sys.exit(1)

    teks = teks.replace(lama, baru, 1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".py.bak_d2_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")
    TARGET.write_text(teks, encoding="utf-8")

    import py_compile
    py_compile.compile(str(TARGET), doraise=True)
    print("[OK] terpasang.")


if __name__ == "__main__":
    main()
