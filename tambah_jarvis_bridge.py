#!/usr/bin/env python3
"""tambah_jarvis_bridge.py -- Tambah Jarvis ke bridge nexus_kerja.py + retry.

1. Daftarkan "jarvis" -> ("agents.jarvis", "jarvis_node") di AGENTS.
2. Tambah retry 2x kalau agent error atau balikin konten kosong.

Cara pakai (dari folder E:\\Project Software\\Orion):
    python tambah_jarvis_bridge.py

Surgical, reversible, idempoten. Backup .bak_jbridge_*.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "nexus_kerja.py"

AGENT_LINE = '    "jarvis": ("agents.jarvis", "jarvis_node"),'


def main():
    print("=== tambah_jarvis_bridge.py ===")
    if not TARGET.is_file():
        print("GAGAL: %s tidak ketemu." % TARGET)
        sys.exit(1)

    garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    # --- Patch 1: tambah jarvis ke AGENTS ---
    if '"jarvis"' in "".join(garis):
        print("[sudah] jarvis sudah terdaftar di AGENTS.")
    else:
        idx = None
        for i, b in enumerate(garis):
            if '"syifaa": ("agents.syifaa", "syifaa_node")' in b:
                idx = i
                break
        if idx is None:
            print("GAGAL: anchor AGENTS tidak ketemu.")
            sys.exit(1)

        t = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = TARGET.with_suffix(".py.bak_jbridge_" + t)
        shutil.copy2(str(TARGET), str(bak))
        print("backup: %s" % bak.name)

        eol = "\n"
        garis = garis[:idx + 1] + [AGENT_LINE + eol] + garis[idx + 1:]
        TARGET.write_text("".join(garis), encoding="utf-8")
        print("[OK] jarvis ditambahkan ke AGENTS.")

        # baca ulang buat patch 2
        garis = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    # --- Patch 2: retry logic ---
    if "maksimal 2x percobaan" in "".join(garis):
        print("[sudah] retry logic sudah ada.")
    else:
        # Cari blok try di nexus_kerja, bungkus dengan retry
        # Anchor: baris "        hasil = func(state) or {}"
        idx_hasil = None
        for i, b in enumerate(garis):
            if "hasil = func(state) or {}" in b:
                idx_hasil = i
                break
        if idx_hasil is None:
            print("GAGAL: anchor retry tidak ketemu.")
            sys.exit(1)

        # Cari awal try (mundur dari idx_hasil)
        idx_try = None
        for i in range(idx_hasil, -1, -1):
            if re.match(r"^    try:$", garis[i].rstrip("\n")):
                idx_try = i
                break
        if idx_try is None:
            print("GAGAL: blok try tidak ketemu.")
            sys.exit(1)

        # Cari akhir except (maju dari idx_hasil sampai "finally:")
        idx_finally = None
        for i in range(idx_hasil, len(garis)):
            if re.match(r"^    finally:$", garis[i].rstrip("\n")):
                idx_finally = i
                break
        if idx_finally is None:
            print("GAGAL: blok finally tidak ketemu.")
            sys.exit(1)

        # Ambil indentasi dalam try (8 spasi)
        # Ganti isi try dengan versi retry
        eol = "\n"
        retry_blok = [
            "    try:" + eol,
            "        # maksimal 2x percobaan kalau error/kosong" + eol,
            "        _err_terakhir = None" + eol,
            "        for _coba in range(2):" + eol,
            "            try:" + eol,
            "                mod = importlib.import_module(mod_name)" + eol,
            "                func = getattr(mod, func_name)" + eol,
            '                state = {"perintah": perintah, "data_riset": data_riset, "riwayat": []}' + eol,
            "                hasil = func(state) or {}" + eol,
            "                _cek = (hasil.get(\"konten\") or hasil.get(\"output\")" + eol,
            '                        or hasil.get("data_riset") or "").strip()' + eol,
            "                if _cek:" + eol,
            "                    _err_terakhir = None" + eol,
            "                    break" + eol,
            "                _err_terakhir = \"kosong\"" + eol,
            "            except Exception as _e:" + eol,
            "                _err_terakhir = \"%s: %s\" % (type(_e).__name__, _e)" + eol,
            "        else:" + eol,
            "            hasil = {}" + eol,
            "        if _err_terakhir == \"kosong\":" + eol,
            "            hasil = {}" + eol,
            "        elif _err_terakhir:" + eol,
            '            return "Bridge error setelah 2x coba: %s" % _err_terakhir' + eol,
        ]

        # Cari baris except yang lama: "    except Exception as e:"
        # dan "        return ..." setelahnya, hapus keduanya
        idx_except = None
        for i in range(idx_hasil + 1, idx_finally):
            if re.match(r"^    except Exception as e:$", garis[i].rstrip("\n")):
                idx_except = i
                break

        if idx_except is None:
            print("GAGAL: except lama tidak ketemu.")
            sys.exit(1)

        # Susun ulang: [sebelum try] + retry_blok + [dari finally sampai akhir]
        baru = garis[:idx_try] + retry_blok + garis[idx_finally:]
        TARGET.write_text("".join(baru), encoding="utf-8")
        print("[OK] retry logic terpasang.")

    import py_compile
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as e:
        print("GAGAL compile: %s" % e)
        sys.exit(1)

    print("[OK] semua patch OK, compile OK.")


if __name__ == "__main__":
    main()
