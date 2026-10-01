"""baca_file.py - Baca isi file."""
from pathlib import Path
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


MAX_UKURAN = 2000


def jalankan(path):
    # Baca isi file - batasi 2000 char
    try:
        p = Path(path)
        # Guard file sensitif (amankan_skill 30/09)
        _g = _guard_baca(p)
        if _g:
            return _g
        if not p.exists():
            return {"sukses": False, "error": "File tidak ada: " + str(path)}

        if p.is_dir():
            return {"sukses": True, "tipe": "folder", "isi": [f.name for f in p.iterdir()][:50]}

        content = p.read_text(encoding="utf-8", errors="ignore")
        total = len(content)

        if total > MAX_UKURAN:
            content = content[:MAX_UKURAN]
            terpotong = True
        else:
            terpotong = False

        return {
            "sukses": True,
            "path": str(p),
            "ukuran_asli": total,
            "ukuran_dibaca": len(content),
            "terpotong": terpotong,
            "isi": content,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}
