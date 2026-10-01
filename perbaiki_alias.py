#!/usr/bin/env python3
"""perbaiki_alias.py -- Perbaiki NameError: ALIAS/AKSI_MULTI is not defined.

Akar masalah (ditemukan 2026-10-01 00:53 dari diagnosis live):
di kontrol_utama.py yang asli, ALIAS (baris 187) dan AKSI_MULTI (baris 150)
adalah variabel LOKAL di dalam fungsi jalankan_perintah(), BUKAN global modul.
Script tambah_jadwal_tugas.py / tambah_daftar_aksi.py ngasumsikan keduanya
global (karena fixture tesnya naro di level modul), sehingga:

  1. jadwal_tugas -> `ALIAS.get(nama, nama)` -> NameError (ditabrak ORION)
  2. daftar_aksi  -> `ALIAS.items()` / `AKSI_MULTI` -> NameError laten
  3. cron_orion._jalan_tugas -> `ku.ALIAS.get(...)` -> AttributeError saat
     tugas beneran dieksekusi cron

Perbaikan (surgical, tanpa mengubah arsitektur dispatcher):
- tambah helper _peta_alias() / _daftar_multi() yang mem-parse dict/list
  tersebut dari source file ini sendiri (defensif: gagal -> {} / []).
- jadwal_tugas, daftar_aksi, dan _jalan_tugas memakai helper itu.
- sekalian perbaiki parser tambah: format baru <jam>||<perintah>||<pesan>
  agar perintah yang mengandung | (mis. copy_file a|b) tidak terpotong.
  Format lama satu-| tetap didukung (fallback).

Idempoten, backup per file, compile-check, auto-restore bila gagal.
"""
import os
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(os.environ.get("ORION_BASE", "E:/Project Software/Orion"))
KONTROL = BASE / "core" / "otonom" / "kontrol"
KU = KONTROL / "kontrol_utama.py"


def _cari_target(nama_file):
    if (BASE / nama_file).is_file():
        return BASE / nama_file
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules")]
        if nama_file in filenames:
            return Path(dirpath) / nama_file
    return None


CR = _cari_target("cron_orion.py")
if CR is None:
    print("GAGAL: cron_orion.py tidak ketemu di", BASE)
    sys.exit(1)

BLOK = []  # (path, lama, baru, cek) -- plain string replace, harus 1x
SATU = []  # (path, anchor_regex, sisipan, cek)


def blok(path, lama, baru, cek):
    BLOK.append((Path(path), lama, baru, cek))


def satu(path, anchor, sisipan, cek):
    SATU.append((Path(path), anchor, sisipan, cek))


# ---------------------------------------------------------------- helpers
KU_HELPERS = r'''

def _peta_alias() -> dict:
    """Baca dict ALIAS dari source file ini.

    ALIAS didefinisikan lokal di dalam jalankan_perintah(), bukan global
    modul, sehingga fungsi lain tidak bisa mengaksesnya langsung.
    Parse defensif: gagal -> {}.
    """
    import re
    from pathlib import Path
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        m = re.search(r'(?m)^([ \t]*)ALIAS = \{$', src)
        if not m:
            return {}
        indent = m.group(1)
        rest = src[m.end():]
        m2 = re.search(r'(?m)^' + re.escape(indent) + r'\}', rest)
        block = rest[: m2.start()] if m2 else rest
        return dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', block))
    except Exception:
        return {}


def _daftar_multi() -> list:
    """Baca list AKSI_MULTI (lokal di jalankan_perintah) dari source file."""
    import re
    from pathlib import Path
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        m = re.search(r'(?m)^([ \t]*)AKSI_MULTI = \[$', src)
        if not m:
            return []
        indent = m.group(1)
        rest = src[m.end():]
        m2 = re.search(r'(?m)^' + re.escape(indent) + r'\]', rest)
        block = rest[: m2.start()] if m2 else rest
        return re.findall(r'"([^"]+)"', block)
    except Exception:
        return []
'''

satu(KU, r"\Z", KU_HELPERS, "def _peta_alias(")

# ---------------------------------------------------------------- jadwal_tugas: parser || + alias via helper
blok(
    KU,
    '''        isi = a[len("tambah"):].strip()
        parts = [p.strip() for p in isi.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            return {"sukses": False, "pesan":
                    "Format: jadwal_tugas tambah <jam HH:MM>|<perintah>|<pesan opsional>"}
        jam, perintah = parts[0], parts[1]
        pesan = parts[2] if len(parts) > 2 else ""''',
    '''        isi = a[len("tambah"):].strip()
        if "||" in isi:
            # format || : <jam>||<perintah>||<pesan> (perintah boleh mengandung |)
            fparts = [p.strip() for p in isi.split("||")]
            jam = fparts[0] if len(fparts) > 0 else ""
            perintah = fparts[1] if len(fparts) > 1 else ""
            pesan = fparts[2] if len(fparts) > 2 else ""
        else:
            parts = [p.strip() for p in isi.split("|")]
            jam = parts[0] if len(parts) > 0 else ""
            perintah = parts[1] if len(parts) > 1 else ""
            pesan = parts[2] if len(parts) > 2 else ""
        if not jam or not perintah:
            return {"sukses": False, "pesan":
                    "Format: jadwal_tugas tambah <jam HH:MM>||<perintah>||<pesan opsional>"}''',
    '"||" in isi',
)

satu(
    KU,
    r"^        nama_asli = ALIAS\.get\(nama, nama\)$",
    "        nama_asli = _peta_alias().get(nama, nama)",
    "_peta_alias().get(nama, nama)",
)

blok(
    KU,
    '"Format: jadwal_tugas list | tambah <jam>|<perintah> | hapus <id> | on|off <id>"',
    '"Format: jadwal_tugas list | tambah <jam>||<perintah>||<pesan> | hapus <id> | on|off <id>"',
    "tambah <jam>||<perintah>",
)

# ---------------------------------------------------------------- daftar_aksi: alias + multi via helper
blok(
    KU,
    '''    # alias balik: aksi -> [alias...]
    balik = {}
    for k, v in ALIAS.items():
        balik.setdefault(v, []).append(k)
    baris = []''',
    '''    # alias balik: aksi -> [alias...] (ALIAS dibaca dari source, bukan global)
    balik = {}
    for k, v in _peta_alias().items():
        balik.setdefault(v, []).append(k)
    multi = _daftar_multi()
    baris = []''',
    "_peta_alias().items()",
)

satu(
    KU,
    r"^        if nama in AKSI_MULTI:$",
    "        if nama in multi:",
    "if nama in multi:",
)

# ---------------------------------------------------------------- cron_orion: dispatch via helper
satu(
    CR,
    r"^        nama = ku\.ALIAS\.get\(nama, nama\)$",
    "        nama = ku._peta_alias().get(nama, nama)",
    "ku._peta_alias().get(nama, nama)",
)


# ================================================================ engine
def _baca(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _tulis(p: Path, teks: str):
    p.write_text(teks, encoding="utf-8")


def _compile_ok(p: Path) -> bool:
    try:
        py_compile.compile(str(p), doraise=True)
        return True
    except Exception as e:
        print(f"COMPILE GAGAL {p.name}: {e}")
        return False


def _terapkan_satu(p: Path, anchor: str, sisipan: str, cek: str) -> str:
    teks = _baca(p)
    if cek in teks:
        return "sudah"
    if anchor == r"\Z":
        _tulis(p, teks + sisipan)
        return "ok(append)"
    m = re.search(anchor, teks, re.MULTILINE)
    if not m:
        return "GAGAL: anchor tidak ketemu"
    if len(re.findall(anchor, teks, re.MULTILINE)) != 1:
        return "GAGAL: anchor tidak unik"
    _tulis(p, teks[: m.start()] + sisipan + teks[m.end():])
    return "ok"


def _terapkan_blok(p: Path, lama: str, baru: str, cek: str) -> str:
    teks = _baca(p)
    if cek in teks:
        return "sudah"
    n = teks.count(lama)
    if n != 1:
        return f"GAGAL: blok ketemu {n}x (harus 1x)"
    _tulis(p, teks.replace(lama, baru, 1))
    return "ok(blok)"


def main():
    print("=== perbaiki_alias.py ===")
    targets = {str(p) for p, _, _, _ in BLOK} | {str(p) for p, _, _, _ in SATU}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_alias_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        shutil.copy2(p, bak)
        backups[t] = bak
        print(f"backup: {bak.name}")

    hasil = []
    for p, lama, baru, cek in BLOK:
        r = _terapkan_blok(p, lama, baru, cek)
        hasil.append((p.name, r))
        print(f"[{p.name}] {r}")
    for p, anchor, sisipan, cek in SATU:
        r = _terapkan_satu(p, anchor, sisipan, cek)
        hasil.append((p.name, r))
        print(f"[{p.name}] {r}")

    gagal = [h for h in hasil if h[1].startswith("GAGAL")]
    if gagal:
        print("ADA YANG GAGAL, restore backup...")
        for t, bak in backups.items():
            shutil.copy2(bak, t)
        print("restore selesai.")
        sys.exit(1)

    for t in targets:
        if not _compile_ok(Path(t)):
            print("COMPILE GAGAL, restore backup...")
            for tt, bak in backups.items():
                shutil.copy2(bak, tt)
            sys.exit(1)

    print(f"[OK] {len(hasil)} patch diproses, semua compile OK.")


if __name__ == "__main__":
    main()
