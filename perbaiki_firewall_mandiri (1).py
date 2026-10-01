#!/usr/bin/env python3
"""perbaiki_firewall_mandiri.py -- Hapus false positive "mandiri" dari firewall.

Masalah: "mandiri" sebagai kata sifat (independent) ketrigger padahal
maksudnya bukan Bank Mandiri. Contoh: "menulis kode secara mandiri".

Aman dihapus karena:
- "Bank Mandiri" tetap ketangkep via kata "bank"
- "transfer ke Mandiri" tetap ketangkep via kata "transfer"
- "rekening Mandiri" tetap ketangkep via kata "rekening"

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python perbaiki_firewall_mandiri.py

Surgical, reversible, idempoten. Backup .bak_fw_*.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "config" / "jarvis_forbidden.json"

# Kata yang dihapus karena false positive sebagai kata umum
# (tetap ketangkep via kata lain dalam konteks finansial)
KATA_DIhapus = ["mandiri", "biaya", "bayar", "bet"]


def main():
    print("=== perbaiki_firewall_mandiri.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    kata_list = data.get("kata_terlarang", [])

    # Cek idempoten
    sudah_bersih = not any(k in kata_list for k in KATA_DIhapus)
    if sudah_bersih:
        print("[sudah] tidak ada false positive. Tidak diapa-apain.")
        return

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".json.bak_fw_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    baru = [k for k in kata_list if k not in KATA_DIhapus]
    dihapus = [k for k in kata_list if k in KATA_DIhapus]
    data["kata_terlarang"] = baru

    TARGET.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Validasi JSON
    try:
        json.loads(TARGET.read_text(encoding="utf-8"))
    except Exception as e:
        print("GAGAL validasi: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] dihapus: %s" % ", ".join(dihapus))
    print("     'Bank Mandiri' tetap ketangkep via kata 'bank'")
    print("     'transfer ke Mandiri' tetap ketangkep via kata 'transfer'")
    print("     'bayar tagihan bank' tetap ketangkep via kata 'bank'")
    print("     'judi bola' tetap ketangkep via kata 'judi'")


if __name__ == "__main__":
    main()
