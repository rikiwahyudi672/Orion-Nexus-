#!/usr/bin/env python3
"""auth_gmail_ulang.py -- OAuth ulang Gmail dari nol.

Hapus token.json yang mati, buka browser buat login Google,
simpan token baru.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python auth_gmail_ulang.py

Butuh: config/credentials.json (OAuth client dari Google Cloud Console)
Hasil: config/token.json baru
"""

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CRED = BASE / "config" / "credentials.json"
TOKEN = BASE / "config" / "token.json"

# Scope sesuai kebutuhan Jarvis: baca, kirim, balas
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def main():
    print("=== auth_gmail_ulang.py ===")

    if not CRED.is_file():
        print("GAGAL: %s tidak ketemu." % CRED)
        print("Download OAuth client JSON dari Google Cloud Console")
        print("-> APIs & Services -> Credentials -> buat OAuth 2.0 Client ID")
        print("-> simpan sebagai config/credentials.json")
        sys.exit(1)

    # Backup token lama kalau ada
    if TOKEN.is_file():
        bak = TOKEN.with_suffix(".json.bak_mati")
        TOKEN.rename(bak)
        print("Token lama dipindah ke: %s" % bak.name)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("GAGAL: google-auth-oauthlib belum install.")
        print("Jalankan: pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    print("Buka browser buat login Google...")
    print("Kalau browser tidak terbuka otomatis, buka URL yang muncul manual.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(str(CRED), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN, "w") as f:
        f.write(creds.to_json())

    print()
    print("[OK] Token baru tersimpan di: %s" % TOKEN)
    print("Tes: python -c \"from mcp_servers.gmail_server import baca_email; print(baca_email())\"")


if __name__ == "__main__":
    main()
