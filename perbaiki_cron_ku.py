"""perbaiki_cron_ku.py -- Perbaiki _cari_kontrol_utama di cron_orion.py.

Latar (log support/logs/cron.log 01:35:08): "kontrol_utama.py tidak ketemu".
Cron jalan, tugas ketemu, tapi _jalan_tugas gagal import kontrol_utama.

Akar: _cari_kontrol_utama mengandalkan BASE untuk kandidat path, padahal
di proses cron BASE mengarah ke folder support/ (lokasi cron_orion.py),
bukan root Orion. kontrol_utama.py adanya di core/otonom/kontrol/.

Perbaikan: jangkar pencarian dari lokasi file cron itu sendiri
(parent.parent = root Orion). BASE hanya jadi fallback tambahan.
Surgical: 1 fungsi diganti, backup, compile-check, idempoten.
"""
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")


def cari_cron():
    p = BASE / "support" / "cron_orion.py"
    if p.is_file():
        return p
    for dirpath, dirnames, filenames in __import__("os").walk(BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules")]
        if "cron_orion.py" in filenames:
            return Path(dirpath) / "cron_orion.py"
    return None


FUNGSI_BARU = '''def _cari_kontrol_utama():
    """Import kontrol_utama.py (dicache). Return modul atau None."""
    # JANGKAR: root Orion dari lokasi cron (perbaiki_cron_ku)
    global _KU_CACHE
    if _KU_CACHE is not None:
        return _KU_CACHE
    import importlib.util
    import os
    import sys
    from pathlib import Path
    cron_dir = Path(__file__).resolve().parent
    # Root Orion = 1 level di atas folder cron (support/). Jangan andalkan
    # BASE karena di proses cron BASE bisa mengarah ke folder support.
    root = cron_dir.parent
    kandidat = [
        root / "core" / "otonom" / "kontrol" / "kontrol_utama.py",
        cron_dir / "kontrol_utama.py",
    ]
    try:
        kandidat.append(Path(BASE) / "core" / "otonom" / "kontrol" / "kontrol_utama.py")
    except NameError:
        pass
    target = None
    for k in kandidat:
        try:
            if k.is_file():
                target = k
                break
        except Exception:
            continue
    if target is None:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", "_arsip", "node_modules")]
            if "kontrol_utama.py" in filenames:
                target = Path(dirpath) / "kontrol_utama.py"
                break
    if target is None:
        _log("kontrol_utama.py tidak ketemu")
        return None
    try:
        sys.path.insert(0, str(target.parent))
        spec = importlib.util.spec_from_file_location("kontrol_utama", str(target))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _KU_CACHE = mod
        return mod
    except Exception as e:
        _log(f"gagal import kontrol_utama: {e}")
        return None
'''


def main():
    cr = cari_cron()
    if cr is None:
        print("GAGAL: cron_orion.py tidak ketemu di", BASE)
        return 1
    print("target:", cr)
    teks = cr.read_text(encoding="utf-8")

    if "# JANGKAR: root Orion dari lokasi cron (perbaiki_cron_ku)" in teks:
        print("SUDAH TERPASANG (idempoten), tidak ada yang diubah.")
        return 0

    bak = cr.with_suffix(".py.bak_cronku_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(cr, bak)
    print("backup:", bak.name)

    pola = re.compile(r"def _cari_kontrol_utama\(\):.*?(?=\ndef _toast_cron\()",
                      re.DOTALL)
    if not pola.search(teks):
        print("GAGAL: fungsi _cari_kontrol_utama tidak ketemu, dibatalkan.")
        return 1
    baru = pola.sub(lambda m: FUNGSI_BARU, teks, count=1)
    cr.write_text(baru, encoding="utf-8")

    try:
        py_compile.compile(str(cr), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, cr)
        print("GAGAL compile, restore dari backup:", e)
        return 1

    print("OK: _cari_kontrol_utama diperbaiki, compile OK.")
    print("Langkah: double-click ORION-HIDUP.bat (restart jantung), lalu tes jadwal lagi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
