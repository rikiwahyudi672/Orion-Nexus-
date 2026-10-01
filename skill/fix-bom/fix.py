"""fix.py - Hapus BOM dari semua file .py."""
import sys
from pathlib import Path


def fix_bom(folder: str = ".") -> dict:
    """Hapus BOM dari semua file .py."""
    base = Path(folder)
    
    if not base.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    files = list(base.rglob("*.py"))
    fixed = []
    failed = []
    
    for f in files:
        try:
            with open(f, "rb") as fp:
                data = fp.read()
            
            if data.startswith(b'\xef\xbb\xbf'):
                data = data[3:]
                with open(f, "wb") as fp:
                    fp.write(data)
                fixed.append(str(f.relative_to(base)))
        except Exception as e:
            failed.append((str(f.relative_to(base)), str(e)))
    
    return {
        "sukses": True,
        "total": len(files),
        "fixed": fixed,
        "failed": failed,
    }


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    hasil = fix_bom(folder)
    
    print("=" * 60)
    print("  FIX BOM")
    print("=" * 60)
    if hasil["sukses"]:
        print(f"Total    : {hasil['total']} file")
        print(f"Fixed    : {len(hasil['fixed'])} file")
        for f in hasil["fixed"][:20]:
            print(f"  [OK] {f}")
        if len(hasil["fixed"]) > 20:
            print(f"  ... dan {len(hasil['fixed']) - 20} lainnya")
        if hasil["failed"]:
            print(f"Failed   : {len(hasil['failed'])}")
            for f, e in hasil["failed"]:
                print(f"  [FAIL] {f}: {e}")
    else:
        print(f"Error: {hasil.get('error')}")
    print("=" * 60)


# === Fungsi utama untuk tool loop ===
# === GUARD-OTOMATIS file sensitif (amankan_skill 30/09) ===
def _cegah_sensitif(_nilai):
    """Tolak akses file sensitif. Terima dict/str/Path/list/tuple. Return dict error / None."""
    import os as _os
    import re as _re
    from pathlib import Path as _P
    _sensitif = (".env", ".key", ".pem", ".pfx", ".p12", "credentials", "secrets")

    def _mirip_path(_s):
        _s = str(_s)
        if _os.path.exists(_s):
            return True
        if _re.match(r"^[a-zA-Z]:[\\/]", _s):
            return True
        if _s.startswith(("\\\\", "/", "./", "../", "~/")):
            return True
        if ("\\" in _s or "/" in _s) and " " not in _s.strip():
            return True
        if " " not in _s and "." in _s and 0 < len(_s) < 260:
            return True
        return False

    def _cek(_v):
        if isinstance(_v, (str, _P)):
            if _mirip_path(_v) and any(_s in _P(str(_v)).name.lower() for _s in _sensitif):
                return str(_v)
            return None
        if isinstance(_v, dict):
            for _x in _v.values():
                _r = _cek(_x)
                if _r:
                    return _r
            return None
        if isinstance(_v, (list, tuple, set)):
            for _x in _v:
                _r = _cek(_x)
                if _r:
                    return _r
            return None
        return None

    _kena = _cek(_nilai)
    if _kena:
        return {"sukses": False, "error": "Ditolak: File sensitif tidak boleh diakses via tool: " + _kena}
    return None
# === AKHIR GUARD-OTOMATIS ===

def jalankan(folder: str = ".") -> dict:
    """Hapus BOM dari semua file .py."""
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    return fix_bom(folder)
