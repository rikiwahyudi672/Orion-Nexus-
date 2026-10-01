#!/usr/bin/env python3
"""tambah_auto_channel.py -- Bot Discord respon semua pesan di channel khusus.

Masalah: di server Discord harus @mention atau pake /chat tiap kali. Ribet.
Solusi: tambah daftar AUTO_CHANNELS. Di channel itu bot respon semua pesan
        tanpa perlu mention.

Cara pakai (dari folder E:\\Project Software\\Nexus.ai):
    python tambah_auto_channel.py

Lalu edit config/discord.json, tambah:
    "auto_channels": [1234567890]   <- ID channel Discord lo

Surgical, reversible, idempoten. Backup .bak_dc_*.
"""

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
TARGET = BASE / "bot" / "discord_bot.py"
CONFIG = BASE / "config" / "discord.json"


def _patch_list_add(garis, anchor_re, sisip, tag):
    """Sisipkan baris setelah anchor (regex, MULTILINE per baris)."""
    anchor = re.compile(anchor_re)
    out = []
    n = 0
    for b in garis:
        out.append(b)
        if anchor.match(b):
            # cek sudah ada (idempoten)
            sudah = any(tag in x for x in out)
            if not sudah:
                indent = b[: len(b) - len(b.lstrip())]
                for s in sisip:
                    out.append(indent + s + "\n")
                n += 1
    return out, n


def main():
    print("=== tambah_auto_channel.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)
    tag = "AUTO_CHANNELS"

    # 1. Tambah konstanta setelah import/config load
    # Anchor: baris yang load discord.json atau DATA_DIR
    anchor_re = r"^.*discord\.json.*$"
    sisip = [
        "# === AUTO CHANNELS (tambah_auto_channel.py) ===",
        "def _load_auto_channels():",
        "    try:",
        "        cfg = json.load(open(str(CONFIG), encoding='utf-8'))",
        "        return set(cfg.get('auto_channels', []))",
        "    except Exception:",
        "        return set()",
        "AUTO_CHANNELS = _load_auto_channels()",
    ]
    # Cek idempoten dulu
    if any(tag in b or "_load_auto_channels" in b for b in garis):
        print("[sudah] patch auto-channel sudah terpasang.")
    else:
        # Cari anchor CONFIG atau discord.json
        idx = None
        for i, b in enumerate(garis):
            if "discord.json" in b and ("CONFIG" in b or "config" in b.lower()):
                idx = i
                break
        if idx is None:
            # fallback: setelah blok import
            for i, b in enumerate(garis):
                if b.strip().startswith("import ") or b.strip().startswith("from "):
                    idx = i
            # sisip setelah import terakhir
        if idx is not None:
            indent = ""
            baru = []
            for s in sisip:
                baru.append(indent + s + "\n")
            garis[idx + 1 : idx + 1] = baru
            print("[OK] konstanta AUTO_CHANNELS ditambahkan.")
        else:
            print("GAGAL: anchor tidak ketemu.")
            sys.exit(1)

    # 2. Ubah kondisi on_message: tambah cek auto channel
    # Anchor: if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
    anchor2 = r"^(\s*)if bot\.user\.mentioned_in\(message\) or isinstance\(message\.channel, discord\.DMChannel\):\s*$"
    out = []
    n2 = 0
    for b in garis:
        m = re.match(anchor2, b)
        if m and n2 == 0:
            indent = m.group(1)
            # cek idempoten
            if "AUTO_CHANNELS" not in b:
                b = "%sif bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel) or (hasattr(message.channel, 'id') and message.channel.id in AUTO_CHANNELS):\n" % indent
                n2 += 1
        out.append(b)
    garis = out
    if n2:
        print("[OK] on_message: tambah cek AUTO_CHANNELS.")
    else:
        print("[info] kondisi on_message sudah ada AUTO_CHANNELS atau anchor tidak ketemu.")

    # Backup & tulis
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET.with_suffix(".py.bak_dc_" + t)
    shutil.copy2(str(TARGET), str(bak))
    print("backup: %s" % bak.name)

    TARGET.write_text("".join(garis), encoding="utf-8")

    # Compile check
    import py_compile

    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("[OK] compile OK.")
    except Exception as e:
        print("GAGAL compile: %s. Restore backup." % e)
        shutil.copy2(str(bak), str(TARGET))
        sys.exit(1)

    # 3. Update config contoh
    if CONFIG.is_file():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
            if "auto_channels" not in cfg:
                cfg["auto_channels"] = []
                cbak = CONFIG.with_suffix(".json.bak_dc_" + t)
                shutil.copy2(str(CONFIG), str(cbak))
                CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
                print("[OK] config: tambah key 'auto_channels' (kosong, isi ID channel lo).")
            else:
                print("[info] config sudah punya 'auto_channels'.")
        except Exception as e:
            print("[warn] config gagal diupdate: %s" % e)

    print("")
    print("SELESAI. Cara pakai:")
    print("  1. Di Discord, klik kanan channel -> Copy Channel ID")
    print("     (aktifkan Developer Mode dulu di Settings > Advanced)")
    print("  2. Edit config/discord.json, isi:")
    print('     "auto_channels": [123456789012345678]')
    print("  3. Restart bot. Di channel itu, chat biasa langsung dibales.")


if __name__ == "__main__":
    main()
