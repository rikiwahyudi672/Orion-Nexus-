"""Archify GOD - auto diagram."""
import ast, re
from pathlib import Path

def scan(folder):
    folder = Path(folder)
    modules, imports = {}, {}
    for py in folder.rglob("*.py"):
        if "_arsip" in str(py) or "__pycache__" in str(py): continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
            mod = str(py.relative_to(folder).with_suffix("")).replace("\\", ".")
            modules[mod] = {"size": py.stat().st_size, "func": 0}
            for n in ast.walk(tree):
                if isinstance(n, ast.FunctionDef): modules[mod]["func"] += 1
                if isinstance(n, ast.Import):
                    for x in n.names: imports.setdefault(mod, []).append(x.name.split(".")[0])
                if isinstance(n, ast.ImportFrom) and n.module:
                    imports.setdefault(mod, []).append(n.module.split(".")[0])
        except: pass
    return modules, imports

def diagram(modules, imports):
    lines = ["```mermaid", "graph TD"]
    for m in modules:
        top = m.split(".")[0]
        lines.append(f'  {top}["{top}"]')
    for m, imps in imports.items():
        src = m.split(".")[0]
        for i in imps:
            dst = i.split(".")[0]
            if src != dst: lines.append(f"  {src} --> {dst}")
    lines.append("```")
    return "\n".join(lines)

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

def jalankan(folder="."):
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    folder = Path(folder).resolve()
    modules, imports = scan(folder)
    result = diagram(modules, imports)
    out = folder / "ARCHITECTURE.md"
    out.write_text(f"# Architecture\n\n**Modules:** {len(modules)}\n\n{result}", encoding="utf-8")
    return {"sukses": True, "modules": len(modules), "file": str(out)}
