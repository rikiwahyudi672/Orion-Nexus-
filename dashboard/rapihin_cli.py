#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rapihin_cli.py -- Restyle CLI dashboard ORION jadi profesional & minimal.

Mengganti: banner ASCII raksasa -> wordmark ramping, info header ber-emoji ->
teks dim rapi, menu 1 baris -> grid 3 kolom, prompt "Lo >" -> "riki ›",
"🤔 Orion mikir..." -> "orion mengetik…", "🤖 ..." -> "orion › ...".

Kepribadian ORION TIDAK diubah -- cuma bingkai CLI-nya.

Cara pakai (dari E:\\Project Software\\Orion\\dashboard):
    python rapihin_cli.py           -> patch dashboard_orion.py
    python rapihin_cli.py --kering  -> simulasi saja

Aman: backup .bak_rapihincli_<timestamp>, idempoten, compile-check,
auto-restore kalau compile gagal.
"""

import argparse
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET = Path("dashboard_orion.py")
MARK = "rapihin_cli"


def blok(nama_def, lookahead_def, isi_baru):
    """Pola ganti satu blok fungsi (line-anchored)."""
    pat = r"^def " + nama_def + r"\(.*?\):.*?(?=^def " + lookahead_def + r")"
    return (pat, isi_baru, re.MULTILINE | re.DOTALL)


LOGO_BARU = '''def logo_animasi():
    """Wordmark ORION ramping. (rapihin_cli 30/09)"""
    try:
        _ver = version_orion.__version__ if version_orion else "2.7"
    except Exception:
        _ver = "2.7"
    print(c("  ORION", C.CYAN + C.BOLD)
          + c(f"   ·   personal ai assistant   ·   v{_ver}   ·   unified edition", C.GRAY))


'''

HEADER_BARU = '''def header():
    """Header ramping tanpa ASCII raksasa. (rapihin_cli 30/09)"""
    os.system("cls" if os.name == "nt" else "clear")
    w = lebar_terminal()
    jam = datetime.now().strftime("%H:%M")
    tgl = datetime.now().strftime("%d/%m/%Y")

    print()
    logo_animasi()
    print(c(f"  {CFG_OWNER}  ·  {tgl} {jam}", C.GRAY))
    info_mood_loyalty()
    if sapaan_orion:
        print()
        try:
            print(c(f"  {sapaan_dashboard.sapaan()}", C.GRAY))
        except Exception:
            pass

    # Garis pemisah
    print(c("  " + "─" * (min(w - 4, 64)), C.GRAY))


'''

MOOD_BARU = '''def info_mood_loyalty():
    """Tampilkan mood + loyalty + trust di header, satu baris kompak. (rapihin_cli 30/09)"""
    _parts = []
    try:
        import emotion_orion
        emo = emotion_orion.get_emotion()
        _parts.append(f"mood {emo['primary']} ({emo['primary_intensity']}/10)")
    except Exception:
        pass
    try:
        import loyalty_orion
        loy = loyalty_orion.get_loyalty()
        _parts.append(f"loyalty {loy['skor']}/100")
    except Exception:
        pass
    try:
        import emotion_orion
        rel = emotion_orion.get_relationship()
        _parts.append(f"trust {rel['trust']}/100 · intimacy {rel['intimacy']}/100")
    except Exception:
        pass
    if _parts:
        print(c("  " + "  ·  ".join(_parts), C.GRAY))


'''

MENU_BARU = '''def menu_cepat():
    """Menu grid 3 kolom. (rapihin_cli 30/09)"""
    _menu = [
        ("1", "sistem"), ("2", "cari"), ("3", "memori"),
        ("4", "notif"), ("v", "voice"), ("i", "inisiatif"),
        ("c", "chat"), ("a", "aktivitas"), ("m", "model"),
        ("k", "cron"), ("0", "keluar"),
    ]
    print()
    for _i in range(0, len(_menu), 3):
        _sel = []
        for _k, _n in _menu[_i:_i + 3]:
            _w = C.RED if _k == "0" else C.GREEN
            _sel.append(c(f"[{_k}]", _w) + f" {_n:<10}")
        print("  " + "  ".join(_sel))
    print()


'''


def daftar_patch():
    P = []
    P.append(blok("logo_animasi", "mood_emoji", LOGO_BARU))
    P.append(blok("info_mood_loyalty", "header", MOOD_BARU))
    P.append(blok("header", "status_bar", HEADER_BARU))
    P.append(blok("menu_cepat", "input_prompt", MENU_BARU))
    # status bar: emoji -> teks dim
    P.append((
        r"^        print\(c\(f\"  \U0001F5A5\U0000FE0F  CPU \{cpu\}%  \u00b7  \U0001F9E0 RAM \{ram\}%  \u00b7  \U0001F4BE E: \{disk\}%\", C\.GRAY\)\)$",
        '        print(c(f"  cpu {cpu}%  ·  mem {ram}%  ·  disk e: {disk}%", C.GRAY))  # rapihin_cli',
        re.MULTILINE,
    ))
    # prompt umum
    P.append((
        r"^        return input\(c\(\"  > \", C\.PROMPT\)\)\.strip\(\)$",
        '        return input(c("  › ", C.PROMPT)).strip()  # rapihin_cli',
        re.MULTILINE,
    ))
    # header chat
    P.append((
        r"^    print\(c\(\"  \u2500\u2500 CHAT AI \u2500\u2500\", C\.CYAN\)\)$",
        '    print(c("  ── chat ──", C.CYAN))  # rapihin_cli',
        re.MULTILINE,
    ))
    # baris provider + bantuan -> satu baris
    P.append((
        r"^    print\(c\(f\"  Provider: \{', '\.join\(f'\{k\}=\{v\}' for k,v in prov\.items\(\)\)\)\}\", C\.GRAY\)\)$\n"
        r"^    print\(c\(\"  Ketik 'exit' buat keluar, 'clear' buat reset history\.\", C\.GRAY\)\)$",
        '    print(c(f"  {\' · \'.join(f\'{k} {v}\' for k,v in prov.items())}  ·  exit=keluar  ·  clear=reset history", C.GRAY))  # rapihin_cli',
        re.MULTILINE,
    ))
    # prompt chat "Lo >" -> "riki ›"
    P.append((
        r"^            user = input\(c\(\"  Lo > \", C\.PROMPT\)\)\.strip\(\)$",
        '            user = input(c("  riki › ", C.PROMPT)).strip()  # rapihin_cli',
        re.MULTILINE,
    ))
    # prefix jawaban orion (semua kemunculan, indentasi dipertahankan)
    P.append((
        r"(?m)^([ ]+)print\(c\(f\"  \U0001F916 \{jawab\}\", C\.(WHITE|YELLOW)\)\)$",
        None,  # handler khusus di bawah
        re.MULTILINE,
    ))
    # indikator mikir (semua kemunculan, indentasi dipertahankan)
    P.append((
        r"(?m)^([ ]+)print\(c\(\"  \U0001F914 Orion mikir\.\.\.\", C\.GRAY\)\)$",
        None,  # handler khusus di bawah
        re.MULTILINE,
    ))
    # pesan perpisahan: buang emoji
    P.append((
        r"^            print\(c\(\"\\n  Sampai jumpa, Riki! \U0001F44B\\n\", C\.CYAN\)\)$",
        r'            print(c("\\n  Sampai jumpa, Riki!\\n", C.CYAN))  # rapihin_cli',
        re.MULTILINE,
    ))
    return P


def terapkan(src):
    total = 0
    for pat, ganti, flags in daftar_patch():
        if MARK in pat:
            continue
        if ganti is None:
            # handler khusus: preservasi indentasi
            if "1F916" in pat:  # 🤖 -> orion ›
                def _r(m):
                    ind, warna = m.group(1), m.group(2)
                    return (f'{ind}print(c("  orion › ", C.GREEN) '
                            f'+ c(jawab, C.{warna}))  # rapihin_cli')
            else:  # 🤔 -> mengetik…
                def _r(m):
                    ind = m.group(1)
                    return f'{ind}print(c("  orion mengetik…", C.GRAY))  # rapihin_cli'
            src, n = re.subn(pat, _r, src, flags=flags)
        else:
            src, n = re.subn(pat, ganti, src, flags=flags)
        total += n
    return src, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kering", action="store_true")
    a = ap.parse_args()

    if not TARGET.exists():
        print(f"!! {TARGET} tidak ketemu. Jalankan dari folder dashboard/.")
        sys.exit(1)
    src = TARGET.read_text(encoding="utf-8")

    if MARK in src:
        print("OK: patch rapihin_cli sudah terpasang (idempoten, lewati).")
        return

    baru, n = terapkan(src)
    print(f"Patch cocok: {n} titik.")
    if n == 0:
        print("!! Tidak ada pola yang cocok -- file mungkin beda versi. Batal.")
        sys.exit(1)
    if a.kering:
        print("Mode --kering: tidak ada yang diubah.")
        return

    bak = TARGET.with_name(
        f"{TARGET.stem}.bak_rapihincli_{datetime.now():%Y%m%d_%H%M%S}{TARGET.suffix}")
    shutil.copy2(TARGET, bak)
    print(f"Backup: {bak.name}")
    TARGET.write_text(baru, encoding="utf-8")
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("Compile OK.")
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, TARGET)
        print(f"!! Compile gagal, restore dari backup.\n{e}")
        sys.exit(1)
    print("Selesai. Restart dashboard buat lihat tampilan baru.")


if __name__ == "__main__":
    main()
