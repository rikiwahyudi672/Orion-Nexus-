"""file_control.py - Kontrol file Orion (JARVIS style)."""
import shutil
from pathlib import Path

FOLDER_DIIZINKAN = [
    Path("E:/Project Software/Orion"),
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
]

FOLDER_TERLARANG = [
    "C:/Windows",
    "C:/Program Files",
    "C:/Program Files (x86)",
]


def _cek_path_aman(path: str) -> tuple:
    p = Path(path).resolve()
    p_str = str(p).replace("\\", "/").lower()
    
    for folder in FOLDER_TERLARANG:
        if p_str.startswith(folder.lower()):
            return False, f"Folder terlarang: {folder}"
    
    return True, "Aman"


def baca_file(path: str, max_char: int = 5000) -> dict:
    try:
        p = Path(path)
        if not p.exists():
            return {"sukses": False, "pesan": f"File tidak ada: {path}"}
        isi = p.read_text(encoding="utf-8", errors="ignore")
        return {"sukses": True, "isi": isi[:max_char], "total": len(isi), "path": str(p)}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def tulis_file(path: str, isi: str) -> dict:
    aman, alasan = _cek_path_aman(path)
    if not aman:
        return {"sukses": False, "pesan": alasan}
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(isi, encoding="utf-8")
        return {"sukses": True, "pesan": f"File ditulis: {path}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def list_folder(path: str) -> dict:
    try:
        p = Path(path)
        if not p.exists():
            return {"sukses": False, "pesan": f"Folder tidak ada: {path}"}
        items = []
        for item in p.iterdir():
            items.append({
                "nama": item.name,
                "tipe": "folder" if item.is_dir() else "file",
                "ukuran": item.stat().st_size if item.is_file() else 0,
            })
        return {"sukses": True, "items": items, "total": len(items)}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def buat_folder(path: str) -> dict:
    aman, alasan = _cek_path_aman(path)
    if not aman:
        return {"sukses": False, "pesan": alasan}
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"sukses": True, "pesan": f"Folder dibuat: {path}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST FILE CONTROL")
    print("=" * 60)
    
    hasil = list_folder("E:/Project Software/Orion")
    if hasil["sukses"]:
        print(f"Total: {hasil['total']} item")
        for item in hasil["items"][:10]:
            print(f"  [{item['tipe']}] {item['nama']}")


def rename_file(sumber: str, tujuan: str) -> dict:
    """Rename/pindah file. Sumber .db tidak boleh dipindah (database live)."""
    ok, pesan = _cek_path_aman(sumber)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    ok, pesan = _cek_path_aman(tujuan)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    try:
        s = Path(sumber)
        t = Path(tujuan)
        if not s.exists():
            return {"sukses": False, "pesan": f"File tidak ada: {sumber}"}
        if s.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            return {"sukses": False,
                    "pesan": "File database tidak boleh dipindah, pakai copy_file untuk backup"}
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(t))
        return {"sukses": True, "pesan": f"Rename OK: {s.name} -> {t.name}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Rename gagal: {e}"}


def copy_file(sumber: str, tujuan: str) -> dict:
    """Copy file. Tujuan .db hanya boleh untuk backup (*backup*/*bak*)."""
    ok, pesan = _cek_path_aman(sumber)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    ok, pesan = _cek_path_aman(tujuan)
    if not ok:
        return {"sukses": False, "pesan": pesan}
    try:
        s = Path(sumber)
        t = Path(tujuan)
        if not s.exists():
            return {"sukses": False, "pesan": f"File tidak ada: {sumber}"}
        if t.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            _nl = t.name.lower()
            if "backup" not in _nl and "bak" not in _nl:
                return {"sukses": False,
                        "pesan": f"Penulisan database dilindungi: {t.name} (backup *_backup.db tetap boleh)"}
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(s), str(t))
        return {"sukses": True, "pesan": f"Copy OK: {s.name} -> {t.name}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Copy gagal: {e}"}
