#!/usr/bin/env python3
"""tambah_aktifkan.py -- Tambah aksi aktifkan_jendela ke kontrol_komputer.

Latar: ORION gagal "Aksi tidak dikenal: aktifkan" saat mau fokuskan jendela.
Aksi baru: aktifkan_jendela <judul>  (alias: aktifkan)

Target:
  E:\\Project Software\\Orion\\core\\otonom\\kontrol\\kontrol_utama.py
  E:\\Project Software\\Orion\\orion_tool_loop.py  (deskripsi registry)

Cara kerja: cocokkan judul jendela (parsial, case-insensitive) lalu fokuskan
via WScript.Shell.AppActivate (tanpa dependensi baru).

Safety: fokus jendela itu aksi ringan dan reversible; tidak perlu konfirmasi
tambahan (lihat_layar memang sudah bisa melihat layar kapan pun).

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

# 1a. wrapper _cmd_ setelah _cmd_buat_folder (HARUS sebelum dict PERINTAH,
#     karena PERINTAH mereferensikan wrapper saat modul di-load).
tambah_patch(
    KU,
    r"^def _cmd_buat_folder\(x\):\n    return buat_folder\(x\)$",
    '''def _cmd_buat_folder(x):
    return buat_folder(x)

def _cmd_aktifkan_jendela(x):
    return aktifkan_jendela(x)''',
    "def _cmd_aktifkan_jendela(",
)

# 1b. implementasi, append di akhir file (idempoten via cek string).
#     Catatan: fragmen PowerShell ditulis dengan quote Python yang selang-seling
#     (bagian ber-quote-dua pakai '...', bagian ber-quote-satu pakai "...")
#     supaya tidak ada backslash escaping di kode yang digenerate.
KU_FUNCS = '''

def aktifkan_jendela(judul: str) -> dict:
    """Fokuskan jendela Windows berdasarkan judul (parsial, case-insensitive)."""
    import subprocess
    judul = (judul or "").strip()
    if not judul:
        return {"sukses": False, "pesan": "Format: aktifkan_jendela <judul jendela>"}
    esc = judul.replace("'", "''")
    ps = "$j = '" + esc + "'; "
    ps += '$p = Get-Process | Where-Object { $_.MainWindowTitle -like "*$j*" } | Select-Object -First 1; '
    ps += 'if ($p) { $ok = (New-Object -ComObject WScript.Shell).AppActivate($p.Id); '
    ps += 'if ($ok) { "OK:" + $p.MainWindowTitle } else { "GAGAL_AKTIF:" + $p.MainWindowTitle } } '
    ps += 'else { "TIDAK_KETEMU:" + $j }'
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, text=True, timeout=15)
        out = (r.stdout or "").strip()
        if out.startswith("OK:"):
            return {"sukses": True, "pesan": "Jendela diaktifkan: " + out[3:]}
        if out.startswith("TIDAK_KETEMU:"):
            return {"sukses": False, "pesan": "Tidak ada jendela berjudul '" + judul + "'"}
        if out.startswith("GAGAL_AKTIF:"):
            return {"sukses": False,
                    "pesan": "Jendela ketemu tapi gagal difokuskan: " + out[11:]}
        err = (r.stderr or "").strip()
        return {"sukses": False, "pesan": "Gagal: " + (err or out or "tidak ada output")}
    except Exception as e:
        return {"sukses": False, "pesan": "Gagal: " + str(e)}
'''

tambah_patch(KU, r"\Z", KU_FUNCS, "def aktifkan_jendela(")

# 2. daftarkan di PERINTAH (anchor terbukti ada dari patch rename)
tambah_patch(
    KU,
    r'^    "buat_folder": _cmd_buat_folder,$',
    '''    "buat_folder": _cmd_buat_folder,
    "aktifkan_jendela": _cmd_aktifkan_jendela,''',
    '"aktifkan_jendela": _cmd_aktifkan_jendela,',
)

# 3. ringkasan_perintah untuk prompt LLM
tambah_patch(
    KU,
    r"^- buat_folder <path>  : Buat folder$",
    """- buat_folder <path>  : Buat folder
- aktifkan_jendela <judul> : Fokuskan jendela (cocok parsial)""",
    "- aktifkan_jendela <judul>",
)

# 4. alias pendek: aktifkan -> aktifkan_jendela (ditangani khusus)
tambah_patch(KU, None, None, '"aktifkan": "aktifkan_jendela",')

# 5. AKSI_MULTI (ditangani khusus)
tambah_patch(KU, None, None, '"aktifkan_jendela",')


# ---------------------------------------------------------------- orion_tool_loop.py
TL = BASE / "orion_tool_loop.py"
tambah_patch(
    TL,
    r"baca/tulis/rename/copy file",
    "baca/tulis/rename/copy file, fokuskan jendela",
    "fokuskan jendela",
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
    m = re.search(r"(?m)^(\s*)ALIAS = \{$", teks)
    if not m:
        return "GAGAL: ALIAS tidak ketemu"
    base_indent = m.group(1)
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^" + re.escape(base_indent) + r"\}", rest)
    if not m2:
        return "GAGAL: tutup ALIAS tidak ketemu"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^(\s+)"', rest[: m2.start()])
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
    print("=== tambah_aktifkan.py ===")
    targets = {str(p) for p, _, _, _ in PATCHES}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_aktif_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
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
    r = _patch_alias(KU, {"aktifkan": "aktifkan_jendela"})
    hasil.append((KU.name + ":ALIAS", r))
    print(f"[{KU.name}:ALIAS] {r}")

    r = _patch_list_tambah(KU, "AKSI_MULTI", ["aktifkan_jendela"])
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
