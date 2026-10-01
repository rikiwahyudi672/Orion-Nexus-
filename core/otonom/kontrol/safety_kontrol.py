"""safety_kontrol.py - Safety untuk kontrol komputer Orion (JARVIS style)."""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
LOG_FILE = BASE / "core" / "otonom" / "kontrol" / "log_kontrol.json"

AKSI_BAHAYA = [
    "shutdown", "restart", "sleep",
    "hapus", "delete", "format",
    "tutup", "kill", "taskkill",
    "hotkey",  # amankan_kontrol 30/09
]

FOLDER_TERLARANG = [
    "C:/Windows",
    "C:/Program Files",
    "C:/Program Files (x86)",
]

APP_TERLARANG = [
    "regedit.exe",
    "diskpart.exe",
    "format.exe",
]


def butuh_konfirmasi(aksi: str, target: str = "") -> tuple:
    aksi_lower = aksi.lower()
    target_lower = target.lower()
    
    for bahaya in AKSI_BAHAYA:
        if bahaya in aksi_lower:
            return True, f"Aksi '{bahaya}' butuh konfirmasi"
    
    for folder in FOLDER_TERLARANG:
        if target_lower.startswith(folder.lower()):
            return True, f"Folder terlarang: {folder}"
    
    for app in APP_TERLARANG:
        if app in target_lower:
            return True, f"Aplikasi terlarang: {app}"
    
    # tulis menimpa file existing -> konfirmasi (amankan_kontrol 30/09)
    if aksi_lower == "tulis":
        _pp = _path_bersih(target)
        try:
            if _pp.exists() and _pp.is_file():
                return True, f"File sudah ada, tulis akan menimpa: {_pp.name}"
        except Exception:
            pass

    # rename/copy menimpa file existing -> konfirmasi (tambah_rename_copy 30/09)
    if aksi_lower in ("rename_file", "copy_file"):
        _belah = target.split("|", 1)
        if len(_belah) == 2:
            _pp = _path_bersih(_belah[1].strip())
            try:
                if _pp.exists():
                    return True, f"File sudah ada, {aksi_lower} akan menimpa: {_pp.name}"
            except Exception:
                pass

    return False, "Aman"


def catat_aksi(aksi: str, target: str, sukses: bool, butuh_konfirmasi: bool = False):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if LOG_FILE.exists():
        try:
            log = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            log = []
    else:
        log = []
    
    log.append({
        "waktu": datetime.now().isoformat(),
        "aksi": aksi,
        "target": target,
        "sukses": sukses,
        "konfirmasi": butuh_konfirmasi,
        "waktu": datetime.now().isoformat(),  # amankan_kontrol 30/09
    })
    
    if len(log) > 1000:
        log = log[-1000:]
    
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def cek_aksi_terakhir(jumlah: int = 10) -> list:
    if not LOG_FILE.exists():
        return []
    try:
        log = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        return log[-jumlah:]
    except Exception:
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST SAFETY KONTROL")
    print("=" * 60)
    
    print("\n=== Test butuh konfirmasi ===")
    for aksi, target in [
        ("buka", "notepad.exe"),
        ("hapus", "E:/test.txt"),
        ("shutdown", ""),
        ("buka", "regedit.exe"),
    ]:
        butuh, alasan = butuh_konfirmasi(aksi, target)
        status = "KONFIRMASI" if butuh else "AMAN"
        print(f"  [{status}] {aksi} {target}: {alasan}")


# === Tambahan amankan_kontrol 30/09 ===
FILE_SENSITIF = [".env", ".key", ".pem", ".pfx", ".p12", "id_rsa",
                 "credentials", "secret"]


def _path_bersih(target: str) -> Path:
    """Ambil path file dari target (tulis memakai format path|isi)."""
    p = target.split("|")[0].strip().strip('"').strip("'")
    try:
        return Path(p).expanduser().resolve()
    except Exception:
        return Path(p)


def cek_blokir(aksi: str, target: str = "") -> tuple:
    """(True, alasan) jika aksi harus DITOLAK mentah-mentah."""
    a = aksi.lower()
    if a not in ("baca", "tulis", "rename_file", "copy_file"):
        return False, ""
    p = _path_bersih(target)
    nama = p.name.lower()
    sfx = p.suffix.lower()
    if a == "baca" and any(s in nama for s in FILE_SENSITIF):
        return True, f"File sensitif tidak boleh dibaca via tool: {p.name}"
    if a == "tulis" and sfx in (".db", ".sqlite", ".sqlite3"):
        return True, f"File database dilindungi: {p.name}"
    if a == "tulis" and any(s in nama for s in FILE_SENSITIF):
        return True, f"File sensitif tidak boleh ditulis via tool: {p.name}"
    if a in ("rename_file", "copy_file"):
        return _cek_sisi_rename(target, a)
    return False, ""

def _cek_sisi_rename(target: str, aksi: str) -> tuple:
    """Aturan blokir rename/copy: sensitif selalu dilarang; .db dijaga."""
    _belah = target.split("|", 1)
    _sumber = _belah[0].strip() if len(_belah) > 0 else ""
    _tujuan = _belah[1].strip() if len(_belah) > 1 else ""
    for _sisi in (_sumber, _tujuan):
        if not _sisi:
            continue
        _pb = _path_bersih(_sisi)
        _nama = _pb.name.lower()
        if any(s in _nama for s in FILE_SENSITIF):
            return True, f"File sensitif tidak boleh di-{aksi}: {_pb.name}"
    if _tujuan:
        _pt = _path_bersih(_tujuan)
        if _pt.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            _nl = _pt.name.lower()
            if "backup" not in _nl and "bak" not in _nl:
                return True, f"Penulisan database dilindungi: {_pt.name}"
    if aksi == "rename_file" and _sumber:
        _ps = _path_bersih(_sumber)
        if _ps.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            return True, "File database tidak boleh dipindah, pakai copy_file untuk backup"
    return False, ""

