#!/usr/bin/env python3
"""tambah_daftar_aksi.py -- Aksi daftar_aksi: ORION bisa ngintip registry-nya sendiri.

Latar: ORION tidak tahu nama aksinya sendiri (pernah nanya "apa nama aksinya"
untuk copy/rename/aktifkan). Dengan daftar_aksi dia bisa introspeksi:
  daftar_aksi         -> semua aksi + deskripsi + alias
  daftar_aksi <kata>  -> saring berdasarkan nama/deskripsi

Deskripsi diambil dari blok ringkasan di file ini sendiri (baris "- nama : ..."),
jadi selalu sinkron dengan yang dilihat LLM di prompt.

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

# 1a. wrapper _cmd_ setelah _cmd_jadwal_tugas (HARUS sebelum dict PERINTAH).
tambah_patch(
    KU,
    r"^def _cmd_jadwal_tugas\(x\):\n    return jadwal_tugas\(x\)$",
    '''def _cmd_jadwal_tugas(x):
    return jadwal_tugas(x)

def _cmd_daftar_aksi(x):
    return daftar_aksi(x)''',
    "def _cmd_daftar_aksi(",
)

# 1b. implementasi, append di akhir file (idempoten via cek string).
KU_FUNCS = '''

def daftar_aksi(arg: str) -> dict:
    """Tampilkan semua aksi yang ORION bisa pakai (baca registry sendiri)."""
    import re
    from pathlib import Path
    a = (arg or "").strip().lower()
    # kumpulkan deskripsi dari blok ringkasan di file ini sendiri
    desk = {}
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        for m in re.finditer(r"(?m)^- (\\S+)\\s+.*?:\\s*(.+)$", src):
            desk[m.group(1)] = m.group(2).strip()
    except Exception:
        pass
    # alias balik: aksi -> [alias...]
    balik = {}
    for k, v in ALIAS.items():
        balik.setdefault(v, []).append(k)
    baris = []
    for nama in sorted(PERINTAH):
        d = desk.get(nama, "")
        if a and a not in nama and a not in d.lower():
            continue
        al = balik.get(nama, [])
        s = "- %s" % nama
        if nama in AKSI_MULTI:
            s += " [multi]"
        if al:
            s += " (alias: %s)" % ", ".join(al)
        if d:
            s += " : %s" % d
        baris.append(s)
    if not baris:
        return {"sukses": False,
                "pesan": "Tidak ada aksi yang cocok dengan '%s'." % a}
    return {"sukses": True,
            "pesan": "Aksi yang aku bisa pakai (%d):\\n%s" % (len(baris), "\\n".join(baris))}
'''

tambah_patch(KU, r"\Z", KU_FUNCS, "def daftar_aksi(")

# 2. daftarkan di PERINTAH
tambah_patch(
    KU,
    r'^    "jadwal_tugas": _cmd_jadwal_tugas,$',
    '''    "jadwal_tugas": _cmd_jadwal_tugas,
    "daftar_aksi": _cmd_daftar_aksi,''',
    '"daftar_aksi": _cmd_daftar_aksi,',
)

# 3. ringkasan_perintah untuk prompt LLM
tambah_patch(
    KU,
    r"^- jadwal_tugas <sub> : Atur tugas terjadwal \(list/tambah/hapus/on/off\)$",
    """- jadwal_tugas <sub> : Atur tugas terjadwal (list/tambah/hapus/on/off)
- daftar_aksi [kata] : Lihat semua aksi yang tersedia (introspeksi diri)""",
    "- daftar_aksi [kata]",
)

# 4. alias pendek: daftar -> daftar_aksi (ditangani khusus)
tambah_patch(KU, None, None, '"daftar": "daftar_aksi",')

# 5. AKSI_MULTI (ditangani khusus)
tambah_patch(KU, None, None, '"daftar_aksi",')


# ---------------------------------------------------------------- orion_tool_loop.py
TL = BASE / "orion_tool_loop.py"
tambah_patch(
    TL,
    r"jadwal tugas",
    "jadwal tugas, daftar aksi",
    "daftar aksi",
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
    print("=== tambah_daftar_aksi.py ===")
    targets = {str(p) for p, _, _, _ in PATCHES}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_daftar_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
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
    r = _patch_alias(KU, {"daftar": "daftar_aksi"})
    hasil.append((KU.name + ":ALIAS", r))
    print(f"[{KU.name}:ALIAS] {r}")

    r = _patch_list_tambah(KU, "AKSI_MULTI", ["daftar_aksi"])
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
