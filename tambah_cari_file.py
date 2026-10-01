#!/usr/bin/env python3
"""tambah_cari_file.py -- Tambah aksi cari_file rekursif ke kontrol_komputer.

Latar: ORION 2x gagal menemukan file (mis. mata_orion.py) karena list_folder
tidak bisa mencari rekursif ke subfolder.
Aksi baru: cari_file <pola>  (alias: cari)
           cari_file <pola>|<folder>  untuk membatasi ke subfolder.

Cara kerja: os.walk dari root ORION, cocokkan nama file parsial dan
case-insensitive (mendukung wildcard * dan ?), hasil dibatasi 50.

Safety: hanya membaca daftar nama file (tidak membuka isi), hasil dibatasi
50 baris supaya tidak membanjiri konteks; tidak perlu konfirmasi.

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

PATCHES = []  # (path, anchor_regex, sisipan, cek_idempoten)


def tambah_patch(path, anchor, sisipan, cek):
    PATCHES.append((Path(path), anchor, sisipan, cek))


# ---------------------------------------------------------------- kontrol_utama.py
KU = KONTROL / "kontrol_utama.py"

# 1a. wrapper _cmd_ setelah _cmd_aktifkan_jendela (HARUS sebelum dict PERINTAH,
#     karena PERINTAH mereferensikan wrapper saat modul di-load).
tambah_patch(
    KU,
    r"^def _cmd_aktifkan_jendela\(x\):\n    return aktifkan_jendela\(x\)$",
    '''def _cmd_aktifkan_jendela(x):
    return aktifkan_jendela(x)

def _cmd_cari_file(x):
    return cari_file(x)''',
    "def _cmd_cari_file(",
)

# 1b. implementasi, append di akhir file (idempoten via cek string).
KU_FUNCS = '''

def cari_file(pola: str) -> dict:
    """Cari file rekursif dari root ORION (nama parsial, case-insensitive)."""
    import fnmatch
    import os
    from pathlib import Path
    arg = (pola or "").strip()
    if "|" in arg:
        nama_pola, folder = [s.strip() for s in arg.split("|", 1)]
    else:
        nama_pola, folder = arg, ""
    if not nama_pola:
        return {"sukses": False,
                "pesan": "Format: cari_file <pola> atau cari_file <pola>|<folder>"}
    root = Path(__file__).resolve().parents[3]
    if folder:
        base = Path(folder) if Path(folder).is_absolute() else root / folder
    else:
        base = root
    if not base.is_dir():
        return {"sukses": False, "pesan": "Folder tidak ada: " + folder}
    kunci = nama_pola.lower()
    pakai_wildcard = ("*" in kunci) or ("?" in kunci)
    hasil = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in filenames:
            if pakai_wildcard:
                cocok = fnmatch.fnmatch(fn.lower(), kunci)
            else:
                cocok = kunci in fn.lower()
            if cocok:
                p = Path(dirpath, fn)
                try:
                    hasil.append(str(p.relative_to(root)))
                except ValueError:
                    hasil.append(str(p))
                if len(hasil) >= 50:
                    break
        if len(hasil) >= 50:
            break
    if not hasil:
        return {"sukses": False,
                "pesan": "Tidak ketemu file cocok '" + nama_pola + "'"}
    catatan = "" if len(hasil) < 50 else "\\n...(dibatasi 50 hasil)"
    return {"sukses": True,
            "pesan": "Ketemu %d file:\\n%s%s" % (len(hasil), "\\n".join(hasil), catatan)}
'''

tambah_patch(KU, r"\Z", KU_FUNCS, "def cari_file(")

# 2. daftarkan di PERINTAH
tambah_patch(
    KU,
    r'^    "aktifkan_jendela": _cmd_aktifkan_jendela,$',
    '''    "aktifkan_jendela": _cmd_aktifkan_jendela,
    "cari_file": _cmd_cari_file,''',
    '"cari_file": _cmd_cari_file,',
)

# 3. ringkasan_perintah untuk prompt LLM
tambah_patch(
    KU,
    r"^- aktifkan_jendela <judul> : Fokuskan jendela \(cocok parsial\)$",
    """- aktifkan_jendela <judul> : Fokuskan jendela (cocok parsial)
- cari_file <pola> : Cari file rekursif (nama parsial)""",
    "- cari_file <pola>",
)

# 4. alias pendek: cari -> cari_file (ditangani khusus)
tambah_patch(KU, None, None, '"cari": "cari_file",')

# 5. AKSI_MULTI (ditangani khusus)
tambah_patch(KU, None, None, '"cari_file",')


# ---------------------------------------------------------------- orion_tool_loop.py
TL = BASE / "orion_tool_loop.py"
tambah_patch(
    TL,
    r"baca/tulis/rename/copy file, fokuskan jendela",
    "baca/tulis/rename/copy file, fokuskan jendela, cari file rekursif",
    "cari file rekursif",
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


def _terapkan(p: Path, anchor: str, sisipan: str, cek: str) -> str:
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
    baru = teks[: m.start()] + sisipan + teks[m.end():]
    _tulis(p, baru)
    return "ok"


def _patch_alias(p: Path, entries: dict) -> str:
    """Sisip entries ke dict ALIAS sebelum kurung tutupnya (tahan indent)."""
    teks = _baca(p)
    if all('"%s": "%s"' % (k, v) in teks for k, v in entries.items()):
        return "sudah"
    m = re.search(r"(?m)^([ \t]*)ALIAS = \{$", teks)
    if not m:
        return "GAGAL: ALIAS tidak ketemu"
    base_indent = m.group(1)
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^" + re.escape(base_indent) + r"\}", rest)
    if not m2:
        return "GAGAL: tutup ALIAS tidak ketemu"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^([ \t]+)"', rest[: m2.start()])
    indent = m3.group(1) if m3 else base_indent + "    "
    sisip = "".join('%s"%s": "%s",\n' % (indent, k, v) for k, v in entries.items())
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def _patch_list_tambah(p: Path, nama_list: str, entries: list) -> str:
    """Tambah entries ke list (mis. AKSI_MULTI) sebelum ']' penutup."""
    teks = _baca(p)
    m = re.search(r"(?m)^\s*" + re.escape(nama_list) + r"\s*=\s*\[$", teks)
    if not m:
        return f"GAGAL: {nama_list} tidak ketemu"
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^\s*\]", rest)
    if not m2:
        return f"GAGAL: tutup {nama_list} tidak ketemu"
    block = rest[: m2.start()]
    if all('"%s"' % e in block or "'%s'" % e in block for e in entries):
        return "sudah"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^(\s+)"', rest[: m2.start()])
    indent = m3.group(1) if m3 else "    "
    sisip = "".join('%s"%s",\n' % (indent, e) for e in entries)
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def main():
    print("=== tambah_cari_file.py ===")
    targets = {str(p) for p, _, _, _ in PATCHES}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_cari_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        shutil.copy2(p, bak)
        backups[t] = bak
        print(f"backup: {bak.name}")

    hasil = []
    for p, anchor, sisipan, cek in PATCHES:
        if anchor is None or sisipan is None:
            continue  # ditangani khusus
        r = _terapkan(p, anchor, sisipan, cek)
        hasil.append((p.name, r))
        print(f"[{p.name}] {r}")

    # patch khusus
    r = _patch_alias(KU, {"cari": "cari_file"})
    hasil.append((KU.name + ":ALIAS", r))
    print(f"[{KU.name}:ALIAS] {r}")

    r = _patch_list_tambah(KU, "AKSI_MULTI", ["cari_file"])
    hasil.append((KU.name + ":AKSI_MULTI", r))
    print(f"[{KU.name}:AKSI_MULTI] {r}")

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
