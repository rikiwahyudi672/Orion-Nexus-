"""update.py - Orion update diri sendiri (dengan pengawasan)."""
import ast
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
DRAFT = BASE / "_draft"
BACKUP = BASE / "_backup_update"
DRAFT.mkdir(exist_ok=True)
BACKUP.mkdir(exist_ok=True)


def bikin_draft(nama_file: str, kode: str) -> dict:
    """Bikin draft update - belum apply."""
    draft_file = DRAFT / f"{nama_file}.draft"
    with open(draft_file, "w", encoding="utf-8") as f:
        f.write(kode)
    
    return {
        "sukses": True,
        "draft": str(draft_file),
        "target": str(BASE / nama_file),
        "pesan": f"Draft siap: {draft_file}",
    }


def cek_draft(draft_file: str) -> dict:
    """Cek draft - apakah valid."""
    draft_path = Path(draft_file)
    if not draft_path.exists():
        return {"sukses": False, "error": "Draft tidak ada"}
    
    try:
        ast.parse(draft_path.read_text(encoding="utf-8"))
        return {"sukses": True, "valid": True}
    except SyntaxError as e:
        return {"sukses": False, "error": str(e), "line": e.lineno}


def apply_draft(draft_file: str, target_file: str) -> dict:
    """Apply draft - backup dulu, baru copy."""
    draft_path = Path(draft_file)
    target_path = Path(target_file)
    
    if not draft_path.exists():
        return {"sukses": False, "error": "Draft tidak ada"}
    
    # Backup target
    if target_path.exists():
        backup_name = f"{target_path.name}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = BACKUP / backup_name
        shutil.copy2(target_path, backup_path)
    else:
        backup_path = None
    
    # Copy draft ke target
    shutil.copy2(draft_path, target_path)
    
    return {
        "sukses": True,
        "target": str(target_path),
        "backup": str(backup_path) if backup_path else None,
    }


def rollback(backup_file: str, target_file: str) -> dict:
    """Rollback - kembalikan backup."""
    backup_path = Path(backup_file)
    target_path = Path(target_file)
    
    if not backup_path.exists():
        return {"sukses": False, "error": "Backup tidak ada"}
    
    shutil.copy2(backup_path, target_path)
    return {"sukses": True, "target": str(target_path)}


def test_target(target_file: str) -> dict:
    """Test target - cek syntax & import."""
    target_path = Path(target_file)
    
    if not target_path.exists():
        return {"sukses": False, "error": "Target tidak ada"}
    
    # Cek syntax
    try:
        ast.parse(target_path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return {"sukses": False, "error": f"Syntax: {e}"}
    
    # Cek import (kalau .py)
    if target_path.suffix == ".py":
        module_name = target_path.stem
        r = subprocess.run(
            ["python", "-c", f"import {module_name}"],
            capture_output=True, text=True, cwd=str(BASE)
        )
        if r.returncode != 0:
            return {"sukses": False, "error": f"Import: {r.stderr[:200]}"}
    
    return {"sukses": True}


if __name__ == "__main__":
    print("Update-diri siap!")
    print(f"BASE  : {BASE}")
    print(f"DRAFT : {DRAFT}")
    print(f"BACKUP: {BACKUP}")


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

def jalankan(aksi: str = "status", **kwargs) -> dict:
    """Update diri sendiri.

    Args:
        aksi: "status" / "help" / "bikin_draft" / "apply" / "rollback" / "evolusi"

    Returns:
        dict: hasil aksi
    """
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    # === HELP ===
    if aksi == "help":
        return {
            "sukses": True,
            "aksi_tersedia": [
                "status",
                "help",
                "bikin_draft",
                "cek_draft",
                "apply",
                "rollback",
                "test",
                "evolusi",
            ],
            "panduan": "Pakai aksi 'evolusi' dengan deskripsi untuk update diri otomatis",
            "contoh": {
                "bikin_draft": "jalankan('bikin_draft', nama_file='test.py', kode='print(1)')",
                "apply": "jalankan('apply', draft_file='_draft/test.py.draft', target_file='test.py')",
                "evolusi": "jalankan('evolusi', deskripsi='Fungsi hitung luas lingkaran')",
            },
        }

    # === STATUS ===
    if aksi == "status":
        return {
            "sukses": True,
            "pesan": "Update-diri siap",
            "fungsi": ["bikin_draft", "cek_draft", "apply_draft", "rollback", "test_target", "evolusi"],
        }

    # === BIKIN DRAFT ===
    if aksi == "bikin_draft":
        nama_file = kwargs.get("nama_file", "")
        kode = kwargs.get("kode", "")
        if not nama_file or not kode:
            return {"sukses": False, "error": "Butuh 'nama_file' dan 'kode'"}
        return bikin_draft(nama_file, kode)

    # === CEK DRAFT ===
    if aksi == "cek_draft":
        draft_file = kwargs.get("draft_file", "")
        if not draft_file:
            return {"sukses": False, "error": "Butuh 'draft_file'"}
        return cek_draft(draft_file)

    # === APPLY ===
    if aksi == "apply":
        draft_file = kwargs.get("draft_file", "")
        target_file = kwargs.get("target_file", "")
        if not draft_file or not target_file:
            return {"sukses": False, "error": "Butuh 'draft_file' dan 'target_file'"}
        return apply_draft(draft_file, target_file)

    # === ROLLBACK ===
    if aksi == "rollback":
        backup_file = kwargs.get("backup_file", "")
        target_file = kwargs.get("target_file", "")
        if not backup_file or not target_file:
            return {"sukses": False, "error": "Butuh 'backup_file' dan 'target_file'"}
        return rollback(backup_file, target_file)

    # === TEST ===
    if aksi == "test":
        target_file = kwargs.get("target_file", "")
        if not target_file:
            return {"sukses": False, "error": "Butuh 'target_file'"}
        return test_target(target_file)

    # === EVOLUSI ===
    if aksi == "evolusi":
        deskripsi = kwargs.get("deskripsi", "")
        if not deskripsi:
            return {"sukses": False, "error": "Butuh 'deskripsi' untuk evolusi"}

        try:
            import sys as _sys
            from pathlib import Path as _Path
            _base = _Path(__file__).parent.parent.parent
            _sys.path.insert(0, str(_base / "core" / "otonom" / "evolusi"))
            from evolusi_kode import tambah_antrian, proses_antrian

            tambah_antrian(deskripsi)
            hasil = proses_antrian()
            return hasil
        except Exception as e:
            return {"sukses": False, "error": f"Evolusi error: {e}"}

    # === UNKNOWN ===
    return {
        "sukses": False,
        "error": f"Aksi tidak dikenal: {aksi}",
        "aksi_tersedia": ["status", "help", "bikin_draft", "cek_draft", "apply", "rollback", "test", "evolusi"],
    }
