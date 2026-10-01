#!/usr/bin/env python3
"""tambah_rename_copy.py -- Tambah aksi rename_file + copy_file ke kontrol_komputer.

Target:
  E:\\Project Software\\Orion\\core\\otonom\\kontrol\\file_control.py
  E:\\Project Software\\Orion\\core\\otonom\\kontrol\\kontrol_utama.py
  E:\\Project Software\\Orion\\core\\otonom\\kontrol\\safety_kontrol.py
  E:\\Project Software\\Orion\\orion_tool_loop.py  (deskripsi registry)

Aksi baru:
  rename_file <sumber>|<tujuan>   (alias: rename)
  copy_file   <sumber>|<tujuan>   (alias: copy)

Safety:
  - FILE_SENSITIF (.env dkk) tidak boleh di-rename/di-copy ke/dari mana pun.
  - rename: sumber .db DIBLOKIR (database live tidak boleh dipindah).
  - copy/rename: tujuan .db hanya boleh kalau namanya gaya backup (*backup*, *bak*).
  - tujuan sudah ada -> butuh konfirmasi (seperti tulis menimpa).

Idempoten, backup per file, compile-check, auto-restore bila gagal.
"""
import ast
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
KONTROL = BASE / "core" / "otonom" / "kontrol"

PATCHES = []  # (path, anchor_regex, sisipan, cek_idempoten)


def tambah_patch(path, anchor, sisipan, cek):
    PATCHES.append((Path(path), anchor, sisipan, cek))


# ---------------------------------------------------------------- file_control.py
FC = KONTROL / "file_control.py"

FC_FUNCS = '''

def rename_file(sumber: str, tujuan: str) -> dict:
    """Rename/pindah file. Sumber .db tidak boleh dipindah (database live)."""
    ok, pesan = _cek_path_aman(sumber)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    ok, pesan = _cek_path_aman(tujuan)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    try:
        s = Path(sumber)
        t = Path(tujuan)
        if not s.exists():
            return {"sukses": False, "pesan": f"File tidak ada: {sumber}"}
        if s.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            return {"sukses": False,
                    "pesan": "File database tidak boleh dipindah, pakai copy_file untuk backup"}
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(t))
        return {"sukses": True, "pesan": f"Rename OK: {s.name} -> {t.name}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Rename gagal: {e}"}


def copy_file(sumber: str, tujuan: str) -> dict:
    """Copy file. Tujuan .db hanya boleh untuk backup (*backup*/*bak*)."""
    ok, pesan = _cek_path_aman(sumber)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    ok, pesan = _cek_path_aman(tujuan)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    try:
        s = Path(sumber)
        t = Path(tujuan)
        if not s.exists():
            return {"sukses": False, "pesan": f"File tidak ada: {sumber}"}
        if t.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            _nl = t.name.lower()
            if "backup" not in _nl and "bak" not in _nl:
                return {"sukses": False,
                        "pesan": f"Penulisan database dilindungi: {t.name} (backup *_backup.db tetap boleh)"}
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(s), str(t))
        return {"sukses": True, "pesan": f"Copy OK: {s.name} -> {t.name}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Copy gagal: {e}"}
'''

# Append di akhir file (idempoten via cek string).
tambah_patch(FC, r"\Z", FC_FUNCS, "def rename_file(")


# ---------------------------------------------------------------- kontrol_utama.py
KU = KONTROL / "kontrol_utama.py"

# 1. import fungsi baru
tambah_patch(
    KU,
    r"^from file_control import baca_file, tulis_file, list_folder, buat_folder$",
    "from file_control import baca_file, tulis_file, list_folder, buat_folder, rename_file, copy_file",
    "rename_file, copy_file",
)

# 2. _cmd_ wrapper setelah _cmd_buat_folder
tambah_patch(
    KU,
    r"^def _cmd_buat_folder\(x\):\n    return buat_folder\(x\)$",
    '''def _cmd_buat_folder(x):
    return buat_folder(x)

def _cmd_rename_file(x):
    parts = x.split("|", 1)
    if len(parts) < 2:
        return {"sukses": False, "pesan": "Format: rename_file <sumber>|<tujuan>"}
    return rename_file(parts[0].strip(), parts[1].strip())

def _cmd_copy_file(x):
    parts = x.split("|", 1)
    if len(parts) < 2:
        return {"sukses": False, "pesan": "Format: copy_file <sumber>|<tujuan>"}
    return copy_file(parts[0].strip(), parts[1].strip())''',
    "def _cmd_rename_file(",
)

# 3. daftarkan di PERINTAH (bagian File)
tambah_patch(
    KU,
    r'^    "buat_folder": _cmd_buat_folder,$',
    '''    "buat_folder": _cmd_buat_folder,
    "rename_file": _cmd_rename_file,
    "copy_file": _cmd_copy_file,''',
    '"rename_file": _cmd_rename_file,',
)

# 4. ringkasan_perintah untuk prompt LLM
tambah_patch(
    KU,
    r"^- buat_folder <path>  : Buat folder$",
    """- buat_folder <path>  : Buat folder
- rename_file <sumber>|<tujuan> : Rename/pindah file
- copy_file <sumber>|<tujuan>   : Copy file""",
    "- rename_file <sumber>",
)

# 5. alias pendek: rename -> rename_file, copy -> copy_file
#    (ALIAS dict; anchor fleksibel, sisip sebelum kurung tutup dict)
tambah_patch(
    KU,
    r"(?m)^ALIAS = \{$",
    None,  # ditangani khusus di bawah
    '"rename": "rename_file",',
)

# 5b. AKSI_MULTI: daftarkan aksi multi-kata baru (konsisten dgn list_folder dll)
tambah_patch(
    KU,
    r"(?m)^    AKSI_MULTI = \[$",
    None,  # ditangani khusus di bawah
    '"rename_file",',
)


# ---------------------------------------------------------------- safety_kontrol.py
SK = KONTROL / "safety_kontrol.py"

# 6. cek_blokir: tangani rename_file/copy_file
tambah_patch(
    SK,
    r'^    if a not in \("baca", "tulis"\):$',
    '''    if a not in ("baca", "tulis", "rename_file", "copy_file"):''',
    '"rename_file", "copy_file"',
)

tambah_patch(
    SK,
    r'(?m)^    return False, ""\n$',
    None,  # placeholder, diganti logika khusus di bawah
    "_cek_sisi_rename",
)


# ---------------------------------------------------------------- orion_tool_loop.py
TL = BASE / "orion_tool_loop.py"
tambah_patch(
    TL,
    r"baca/tulis file, list folder",
    "baca/tulis/rename/copy file, list folder",
    "baca/tulis/rename/copy file",
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


def _patch_alias(p: Path) -> str:
    """Sisip rename/copy ke dict ALIAS sebelum kurung tutupnya (tahan indent)."""
    teks = _baca(p)
    if '"rename": "rename_file"' in teks:
        return "sudah"
    m = re.search(r"(?m)^(\s*)ALIAS = \{$", teks)
    if not m:
        return "GAGAL: ALIAS tidak ketemu"
    base_indent = m.group(1)
    # cari kurung tutup dict ALIAS (baris hanya berisi '}' di indent yang sama)
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^" + re.escape(base_indent) + r"\}", rest)
    if not m2:
        return "GAGAL: tutup ALIAS tidak ketemu"
    pos = m.end() + m2.start()
    # indentasi dari baris isi pertama
    m3 = re.search(r"(?m)^(\s+)\"", rest[: m2.start()])
    indent = m3.group(1) if m3 else base_indent + "    "
    sisip = f'{indent}"rename": "rename_file",\n{indent}"copy": "copy_file",\n'
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def _patch_list_tambah(p: Path, nama_list: str, entries: list) -> str:
    """Tambah entries ke list module-level (mis. AKSI_MULTI) sebelum ']' penutup."""
    teks = _baca(p)
    m = re.search(r"(?m)^\s*" + re.escape(nama_list) + r"\s*=\s*\[$", teks)
    if not m:
        return f"GAGAL: {nama_list} tidak ketemu"
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^\s*\]", rest)
    if not m2:
        return f"GAGAL: tutup {nama_list} tidak ketemu"
    block = rest[: m2.start()]
    if all(f'"{e}"' in block or f"'{e}'" in block for e in entries):
        return "sudah"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^(\s+)"', rest[: m2.start()])
    indent = m3.group(1) if m3 else "    "
    sisip = "".join(f"{indent}\"{e}\",\n" for e in entries)
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def _patch_blokir_rename(p: Path) -> str:
    """Tambah blok rename/copy di cek_blokir sebelum 'return False, \"\"' akhir fungsi."""
    teks = _baca(p)
    if "_cek_sisi_rename" in teks:
        return "sudah"
    anchor = '''    if a == "tulis" and any(s in nama for s in FILE_SENSITIF):
        return True, f"File sensitif tidak boleh ditulis via tool: {p.name}"
    return False, ""'''
    if anchor not in teks:
        return "GAGAL: anchor blokir tidak ketemu"
    blok = '''    if a == "tulis" and any(s in nama for s in FILE_SENSITIF):
        return True, f"File sensitif tidak boleh ditulis via tool: {p.name}"
    if a in ("rename_file", "copy_file"):
        return _cek_sisi_rename(target, a)
    return False, ""'''
    baru = teks.replace(anchor, blok + "\n\n" + _cek_sisi_rename_src(), 1)
    _tulis(p, baru)
    return "ok"


def _cek_sisi_rename_src() -> str:
    return '''def _cek_sisi_rename(target: str, aksi: str) -> tuple:
    """Aturan blokir rename/copy: sensitif selalu dilarang; .db dijaga."""
    _belah = target.split("|", 1)
    _sumber = _belah[0].strip() if len(_belah) > 0 else ""
    _tujuan = _belah[1].strip() if len(_belah) > 1 else ""
    for _sisi in (_sumber, _tujuan):
        if not _sisi:
            continue
        _pb = _path_bersih(_sisi)
        _nama = _pb.name.lower()
        if any(s in _nama for s in FILE_SENSITIF):
            return True, f"File sensitif tidak boleh di-{aksi}: {_pb.name}"
    if _tujuan:
        _pt = _path_bersih(_tujuan)
        if _pt.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            _nl = _pt.name.lower()
            if "backup" not in _nl and "bak" not in _nl:
                return True, f"Penulisan database dilindungi: {_pt.name}"
    if aksi == "rename_file" and _sumber:
        _ps = _path_bersih(_sumber)
        if _ps.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            return True, "File database tidak boleh dipindah, pakai copy_file untuk backup"
    return False, ""
'''


def _patch_konfirmasi_rename(p: Path) -> str:
    teks = _baca(p)
    if "rename/copy menimpa file existing -> konfirmasi" in teks:
        return "sudah"
    anchor = '''    # tulis menimpa file existing -> konfirmasi (amankan_kontrol 30/09)
    if aksi_lower == "tulis":
        _pp = _path_bersih(target)
        try:
            if _pp.exists() and _pp.is_file():
                return True, f"File sudah ada, tulis akan menimpa: {_pp.name}"
        except Exception:
            pass

    return False, "Aman"'''
    if anchor not in teks:
        return "GAGAL: anchor konfirmasi tidak ketemu"
    baru_anchor = anchor.replace(
        '\n    return False, "Aman"',
        '''
    # rename/copy menimpa file existing -> konfirmasi (tambah_rename_copy 30/09)
    if aksi_lower in ("rename_file", "copy_file"):
        _belah = target.split("|", 1)
        if len(_belah) == 2:
            _pp = _path_bersih(_belah[1].strip())
            try:
                if _pp.exists():
                    return True, f"File sudah ada, {aksi_lower} akan menimpa: {_pp.name}"
            except Exception:
                pass

    return False, "Aman"''',
        1,
    )
    _tulis(p, teks.replace(anchor, baru_anchor, 1))
    return "ok"


def main():
    print("=== tambah_rename_copy.py ===")
    targets = {str(p) for p, _, _, _ in PATCHES}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_renamecopy_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
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
    for nama, fn, p in [
        ("ALIAS", _patch_alias, KU),
        ("blokir rename", _patch_blokir_rename, SK),
        ("konfirmasi rename", _patch_konfirmasi_rename, SK),
    ]:
        r = fn(p)
        hasil.append((p.name + ":" + nama, r))
        print(f"[{p.name}:{nama}] {r}")

    r = _patch_list_tambah(KU, "AKSI_MULTI", ["rename_file", "copy_file"])
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
