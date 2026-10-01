"""audit.py - Audit folder Python."""
import ast
import sys
from pathlib import Path


def audit_folder(folder: str) -> dict:
    """Audit folder: scan, cek syntax, BOM, TODO."""
    base = Path(folder)
    
    if not base.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    # Exclude folder
    EXCLUDE = ["_archive", "_backup", "backup", "__pycache__", ".git", "_tmp", "_temp", "_arsip"]
    py_files = []
    for py in base.rglob("*.py"):
        rel = str(py.relative_to(base))
        if any(ex in rel for ex in EXCLUDE):
            continue
        py_files.append(py)
    syntax_errors = []
    bom_files = []
    todo_items = []
    
    for py in py_files:
        try:
            with open(py, "rb") as f:
                data = f.read()
            
            # Cek BOM
            if data.startswith(b'\xef\xbb\xbf'):
                bom_files.append(str(py.relative_to(base)))
                continue
            
            # Cek syntax
            try:
                content = data.decode("utf-8", errors="ignore")
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append({
                    "file": str(py.relative_to(base)),
                    "error": str(e),
                    "line": e.lineno
                })
                continue
            
            # Cek TODO/FIXME
            for i, line in enumerate(content.split("\n"), 1):
                for kw in ["TODO", "FIXME"]:
                    if kw in line and "#" in line:
                        todo_items.append({
                            "file": str(py.relative_to(base)),
                            "line": i,
                            "text": line.strip()[:80]
                        })
                        break
        except Exception:
            pass
    
    return {
        "sukses": True,
        "folder": str(base),
        "total_py": len(py_files),
        "syntax_errors": syntax_errors,
        "bom_files": bom_files,
        "todo_items": todo_items,
    }


def format_audit(hasil: dict) -> str:
    """Format hasil audit."""
    if not hasil.get("sukses"):
        return f"Error: {hasil.get('error')}"
    
    lines = []
    lines.append("=" * 60)
    lines.append("  AUDIT FOLDER")
    lines.append("=" * 60)
    lines.append(f"Folder       : {hasil['folder']}")
    lines.append(f"Total .py    : {hasil['total_py']}")
    lines.append("")
    lines.append(f"BOM files    : {len(hasil['bom_files'])}")
    for f in hasil['bom_files'][:10]:
        lines.append(f"  [BOM] {f}")
    lines.append("")
    lines.append(f"Syntax error : {len(hasil['syntax_errors'])}")
    for e in hasil['syntax_errors'][:10]:
        lines.append(f"  [ERROR] {e['file']}:{e.get('line', '?')}")
    lines.append("")
    lines.append(f"TODO/FIXME   : {len(hasil['todo_items'])}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    hasil = audit_folder(folder)
    print(format_audit(hasil))


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
    """Audit folder."""
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    return audit_folder(folder)
