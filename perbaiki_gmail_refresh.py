#!/usr/bin/env python3
"""perbaiki_gmail_refresh.py -- Tambah auto-refresh token ke gmail_server.py.

Masalah: get_service() langsung pakai token.json tanpa cek expired.
Kalau access token mati tapi refresh token masih hidup, harusnya bisa refresh otomatis.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python perbaiki_gmail_refresh.py

Surgical, reversible, idempoten. Backup .bak_gmail_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "mcp_servers" / "gmail_server.py"

FUNGSI_BARU = '''def get_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file("config/token.json")
    # Auto-refresh kalau access token expired tapi refresh token masih ada
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("config/token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)'''


def main():
    print("=== perbaiki_gmail_refresh.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    teks = TARGET.read_text(encoding="utf-8")

    if "creds.refresh(Request())" in teks:
        print("[sudah] auto-refresh sudah ada. Tidak diapa-apain.")
        return

    # Cari fungsi get_service yang lama
    pola = re.compile(
        r"def get_service\(\):.*?return build\(\"gmail\", \"v1\", credentials=creds\)",
        re.DOTALL,
    )
    m = pola.search(teks)
    if not m:
        print("GAGAL: fungsi get_service tidak ketemu.")
        sys.exit(1)

    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_gmail_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    teks_baru = teks[: m.start()] + FUNGSI_BARU + teks[m.end():]
    TARGET.write_text(teks_baru, encoding="utf-8")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    print("[OK] auto-refresh token terpasang, compile OK.")
    print("     Kalau refresh token juga mati, hapus config/token.json")
    print("     lalu jalanin OAuth ulang pakai credentials.json.")


if __name__ == "__main__":
    main()
