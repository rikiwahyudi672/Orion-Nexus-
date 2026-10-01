"""Debug GOD - auto debug."""
import ast, subprocess, sys
from pathlib import Path

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

def jalankan(file_path):
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    file_path = Path(file_path)
    # Phase 1: Reproduce
    try:
        r = subprocess.run([sys.executable, str(file_path)], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return {"sukses": True, "output": r.stdout[:200]}
        err = r.stderr
    except Exception as e:
        err = str(e)
    
    # Phase 2: Isolate
    content = file_path.read_text(encoding="utf-8")
    try:
        ast.parse(content)
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False
        line = e.lineno
    
    # Phase 3: Identify
    if "U+FEFF" in err or "non-printable" in err:
        penyebab = "BOM"
        content = content.lstrip("\ufeff")
        file_path.write_text(content, encoding="utf-8")
    elif not syntax_ok:
        penyebab = f"Syntax error line {line}"
    else:
        penyebab = "Runtime error"
    
    # Phase 4: Verify
    try:
        r = subprocess.run([sys.executable, str(file_path)], capture_output=True, text=True, timeout=30)
        ok = r.returncode == 0
    except: ok = False
    
    return {"sukses": ok, "penyebab": penyebab, "error": err[:200]}
