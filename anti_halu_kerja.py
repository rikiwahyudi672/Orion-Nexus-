#!/usr/bin/env python3
"""anti_halu_kerja.py -- Jarvis jangan ngarang aktivitas worker.

Aturan: kalo ditanya "lagi apa" / aktivitas real-time worker,
        jawab jujur nggak tau, jangan inventarisasi ngarang.
Target: config/personality.json (tambah aturan anti-halu spesifik).
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "config" / "personality.json"

ATURAN = (
    "JANGAN PERNAH mengarang aktivitas real-time para worker (Syifaa, Tony, Arya, Juan, Zulia, Insan, Raka). "
    "Kalo ditanya 'lagi apa', 'lagi ngapain', atau aktivitas mereka saat ini, jawab jujur: "
    "'Gue nggak tau mereka lagi ngapain sekarang bos, nggak ada live tracking. Kalo mau tau, suruh mereka lapor atau cek langsung.' "
    "Jangan inventarisasi seperti 'lagi ngedit video', 'lagi ngumpulin data', dll. Itu halu."
)


def main():
    print("=== anti_halu_kerja.py ===")
    if not TARGET.is_file():
        print("GAGAL: personality.json tidak ketemu.")
        sys.exit(1)

    data = json.loads(TARGET.read_text(encoding="utf-8"))

    # Cari key yang cocok untuk aturan
    # Coba beberapa kemungkinan struktur
    added = False
    for key in ["rules", "aturan", "anti_halu", "constraints", "larangan"]:
        if key in data and isinstance(data[key], list):
            if ATURAN not in data[key]:
                data[key].append(ATURAN)
                added = True
                print(f"Ditambah ke key '{key}'.")
            else:
                print(f"[sudah] sudah ada di '{key}'.")
                return
            break

    if not added:
        # Buat key baru
        if "anti_halu_spesifik" not in data:
            data["anti_halu_spesifik"] = []
        if ATURAN not in data["anti_halu_spesifik"]:
            data["anti_halu_spesifik"].append(ATURAN)
            added = True
            print("Ditambah ke key 'anti_halu_spesifik'.")
        else:
            print("[sudah] sudah ada.")
            return

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(f".json.bak_halu_{t}")
    shutil.copy2(str(TARGET), str(bak))
    print(f"backup: {bak.name}")

    TARGET.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[OK] aturan anti-halu terpasang.")


if __name__ == "__main__":
    main()
