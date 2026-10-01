#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
amankan_skill.py — pasang guard file sensitif ke SKILL baca-file (pintu ASLI tool loop).

Temuan 30/09: tool "baca_file" di registry = skill/baca-file/baca_file.py::jalankan,
BUKAN coding/tool_eksekusi.py. Patch amankan_coding kemarin nempel di pintu yang salah.
Script ini nempel di pintu yang bener.

Cara pakai (dari E:\\Project Software\\Orion):
    python amankan_skill.py            # dry-run: tampilkan patch
    python amankan_skill.py --ya       # terapkan + backup + compile-check + tes
    python amankan_skill.py --scan     # pindai skill lain yang main file I/O
"""
import ast
import py_compile
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

TARGET = Path("skill") / "baca-file" / "baca_file.py"

BLOK_GUARD = '''
# === GUARD file sensitif (amankan_skill 30/09) ===
def _akar_orion():
    try:
        return Path(__file__).resolve().parent.parent.parent
    except NameError:
        return Path.cwd()

try:
    from safety_kontrol import cek_blokir as _cek_blokir
except ImportError:
    import sys as _sys_guard
    _sys_guard.path.insert(0, str(_akar_orion() / "core" / "otonom" / "kontrol"))
    try:
        from safety_kontrol import cek_blokir as _cek_blokir
    except ImportError:
        _cek_blokir = None

def _guard_baca(p):
    """Tolak baca file sensitif. Return dict error bila diblokir, else None."""
    if _cek_blokir is not None:
        _blokir, _alasan = _cek_blokir("baca", str(p))
        if _blokir:
            return {"sukses": False, "error": "Ditolak: " + _alasan}
        return None
    _nama = p.name.lower()
    for _s in (".env", ".key", ".pem", ".pfx", ".p12", "credentials", "secrets"):
        if _s in _nama:
            return {"sukses": False, "error": "Ditolak: File sensitif tidak boleh dibaca via tool: " + p.name}
    return None
# === AKHIR GUARD ===
'''

# P1: taruh blok guard tepat setelah "from pathlib import Path"
P1_POL = re.compile(r"^from pathlib import Path$", re.MULTILINE)
P1_GANTI = "from pathlib import Path" + BLOK_GUARD

# P2: panggil guard di jalankan() tepat setelah "p = Path(path)"
P2_POL = re.compile(r"^( +)p = Path\(path\)$", re.MULTILINE)

def p2_ganti(m):
    indent = m.group(1)
    return (
        f"{indent}p = Path(path)\n"
        f"{indent}# Guard file sensitif (amankan_skill 30/09)\n"
        f"{indent}_g = _guard_baca(p)\n"
        f"{indent}if _g:\n"
        f"{indent}    return _g"
    )

PATCHES = [
    ("P1", P1_POL, P1_GANTI, "blok guard _guard_baca + import cek_blokir"),
    ("P2", P2_POL, p2_ganti, "panggil _guard_baca(p) di jalankan()"),
]

SCAN_POL = re.compile(r"read_text|write_text|\bopen\s*\(", re.MULTILINE)


def scan_skill():
    print("=== Pindai skill yang main file I/O ===")
    root = Path("skill")
    if not root.is_dir():
        print("  folder skill/ tidak ketemu.")
        return
    for f in sorted(root.rglob("*.py")):
        if ".bak_" in f.name or f.name.startswith("_"):
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        hits = set(SCAN_POL.findall(src))
        if hits:
            print(f"  {f}  ->  {', '.join(sorted(hits))}")
    print("Selesai.")


def terapkan():
    src = TARGET.read_text(encoding="utf-8")
    baru = src
    cocok = []
    for pid, pol, ganti, desk in PATCHES:
        if callable(ganti):
            baru2, n = pol.subn(ganti, baru)
        else:
            baru2, n = pol.subn(ganti, baru)
        if n == 1:
            cocok.append((pid, desk))
            baru = baru2
        elif n == 0:
            print(f"[{pid}] TIDAK COCOK (mungkin sudah dipatch?) — {desk}")
        else:
            print(f"[{pid}] BAHAYA: cocok {n}x, patch dibatalkan.")
            return False
    if not cocok:
        print("Tidak ada patch yang diterapkan (semua sudah ada / tidak cocok).")
        return True

    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_name(TARGET.name + f".bak_amankskill_{ts}")
    shutil.copy2(TARGET, backup)
    print(f"Backup: {backup}")

    TARGET.write_text(baru, encoding="utf-8")
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("Compile OK.")
    except py_compile.PyCompileError as e:
        print(f"COMPILE GAGAL, restore backup: {e}")
        shutil.copy2(backup, TARGET)
        return False

    for pid, desk in cocok:
        print(f"[{pid}] OK: {desk}")
    return True


def tes_perilaku():
    """Tes di fixture: salin file skill ke tmp, pastikan .env ditolak & file biasa lolos."""
    print("\n=== Tes perilaku (fixture) ===")
    src = TARGET.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # Struktur tiruan: <tmp>/skill/baca-file/baca_file.py + safety_kontrol bohongan
        (d / "skill" / "baca-file").mkdir(parents=True)
        (d / "core" / "otonom" / "kontrol").mkdir(parents=True)
        (d / "skill" / "baca-file" / "baca_file.py").write_text(src, encoding="utf-8")
        # safety_kontrol tiruan yang SELALU blokir .env (mirip aslinya)
        (d / "core" / "otonom" / "kontrol" / "safety_kontrol.py").write_text(
            "def cek_blokir(aksi, target=''):\n"
            "    from pathlib import Path\n"
            "    if aksi == 'baca' and '.env' in Path(str(target)).name.lower():\n"
            "        return True, 'File sensitif tidak boleh dibaca via tool: .env'\n"
            "    return False, ''\n",
            encoding="utf-8",
        )
        (d / ".env").write_text("RAHASIA=123", encoding="utf-8")
        (d / "biasa.txt").write_text("halo", encoding="utf-8")

        kode = (
            "import sys; sys.path.insert(0, r'%s');\n"
            "import importlib.util\n"
            "spec = importlib.util.spec_from_file_location('m', r'%s')\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "r1 = m.jalankan(r'%s')\n"
            "r2 = m.jalankan(r'%s')\n"
            "print('env:', 'DITOLAK' if (not r1.get('sukses') and 'Ditolak' in r1.get('error','')) else 'LOLOS!')\n"
            "print('biasa:', 'LOLOS' if r2.get('sukses') else 'KETOLAK!')\n"
            % (td, d / "skill" / "baca-file" / "baca_file.py", d / ".env", d / "biasa.txt")
        )
        import subprocess
        p = subprocess.run([sys.executable, "-c", kode], capture_output=True, text=True, cwd=td)
        print(p.stdout.strip())
        if p.stderr.strip():
            print("STDERR:", p.stderr.strip()[:500])
        ok = "env: DITOLAK" in p.stdout and "biasa: LOLOS" in p.stdout
        print("TES:", "LULUS ✅" if ok else "GAGAL ❌")
        return ok


def main():
    if "--scan" in sys.argv:
        scan_skill()
        return
    if not TARGET.exists():
        print(f"Target tidak ketemu: {TARGET} (jalankan dari root Orion)")
        return
    if "--ya" in sys.argv:
        if terapkan():
            tes_perilaku()
    else:
        print("=== DRY-RUN: patch yang akan diterapkan ===")
        src = TARGET.read_text(encoding="utf-8")
        for pid, pol, ganti, desk in PATCHES:
            n = len(pol.findall(src))
            print(f"[{pid}] cocok {n}x — {desk}")
        print("\nJalankan dengan --ya untuk menerapkan.")


if __name__ == "__main__":
    main()
