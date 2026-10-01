"""fix.py - Fix syntax error massal (em dash, en dash, BOM)."""
import ast
import sys
from pathlib import Path


def fix_syntax(folder: str = ".") -> dict:
    """Fix syntax error: em dash, en dash, BOM."""
    base = Path(folder)
    
    if not base.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    py_files = list(base.rglob("*.py"))
    fixed = []
    still_error = []
    
    for py in py_files:
        try:
            with open(py, "rb") as f:
                data = f.read()
            
            changed = False
            
            # Fix BOM
            if data.startswith(b'\xef\xbb\xbf'):
                data = data[3:]
                changed = True
            
            # Fix em dash (U+2014)
            if b'\xe2\x80\x94' in data:
                data = data.replace(b'\xe2\x80\x94', b'-')
                changed = True
            
            # Fix en dash (U+2013)
            if b'\xe2\x80\x93' in data:
                data = data.replace(b'\xe2\x80\x93', b'-')
                changed = True
            
            if changed:
                with open(py, "wb") as f:
                    f.write(data)
                fixed.append(str(py.relative_to(base)))
            
            # Cek syntax setelah fix
            try:
                ast.parse(data.decode("utf-8", errors="ignore"))
            except SyntaxError as e:
                still_error.append({
                    "file": str(py.relative_to(base)),
                    "error": str(e),
                    "line": e.lineno,
                })
        except Exception:
            pass
    
    return {
        "sukses": True,
        "total": len(py_files),
        "fixed": fixed,
        "still_error": still_error,
    }


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    hasil = fix_syntax(folder)
    
    print("=" * 60)
    print("  FIX SYNTAX")
    print("=" * 60)
    if hasil["sukses"]:
        print(f"Total        : {hasil['total']} file")
        print(f"Fixed        : {len(hasil['fixed'])} file")
        for f in hasil["fixed"][:20]:
            print(f"  [OK] {f}")
        print(f"Still error  : {len(hasil['still_error'])}")
        for e in hasil["still_error"][:10]:
            print(f"  [ERROR] {e['file']}:{e.get('line', '?')}")
            print(f"    {e['error'][:80]}")
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
    """Fix syntax error massal."""
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    return fix_syntax(folder)
