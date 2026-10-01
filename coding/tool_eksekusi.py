import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
tool_eksekusi.py - Tool eksekusi untuk ORION.
Bikin ORION bisa tulis file, baca file, jalankan terminal.
"""
import os
import io
import subprocess
import time
from pathlib import Path

BASE = Path(__file__).parent


# === WHITELIST TERMINAL ===
# WHITELIST EXPANDED
# TERMINAL_EXPANDED
WHITELIST_CMD = [
    # Visual Studio 2022
    "devenv.exe", "devenv ", "devenv.com",
    # VSCode
    "code ", "code.exe", "code.cmd",
    # Notepad
    "notepad ", "notepad.exe",
    # Terminal
    "cmd.exe", "cmd ", "powershell", "pwsh",
    "wt.exe", "wt ", "wt",
    # Buka aplikasi
    "explorer.exe", "explorer ", "start ",
    "start chrome", "start notepad", "start code", "start devenv",
    # Utility
    "where.exe", "where ", "tasklist", "systeminfo", "ipconfig",
    "ping ", "tree ", "taskkill /im", "taskkill /pid",
    # File ops
    "dir", "ls", "cd", "pwd", "type", "cat", "tree",
    "echo", "where", "which", "mkdir ", "md ", "copy ", "cp ",
    "move ", "mv ", "ren ", "touch ", "del ",
    # Python
    "python ", "python3 ", "py ", "pip install ", "pip list", "pip show",
    "pytest ",
    # Git
    "git status", "git log", "git diff", "git branch",
    "git add ", "git commit ", "git init", "git clone ", "git pull", "git fetch",
    # OLD

    "devenv.exe", "devenv ", "start devenv",
    "code ", "code.exe",
    # VSCode & Editor
    "code ", "code.exe", "notepad ", "notepad.exe",
    # Windows Terminal & Shell
    "wt.exe", "wt ", "cmd.exe", "cmd ", "powershell", "pwsh",
    "start ",
    # Buka aplikasi
    "explorer.exe", "explorer ", "start chrome", "start notepad",
    "start code",
    # Utility
    "where.exe", "where ", "tasklist", "taskkill /im", "taskkill /pid",
    "systeminfo", "ipconfig", "ping ",
    # Python & PIP
    "python ", "python3 ", "py ", "pip install ", "pip list", "pip show",
    "pytest ",
    # File ops
    "dir", "ls", "cd", "pwd", "type", "cat", "tree",
    "echo", "where", "which", "mkdir ", "md ", "copy ", "cp ",
    "move ", "mv ", "ren ", "touch ", "del ",
    # Git
    "git status", "git log", "git diff", "git branch",
    "git add ", "git commit ", "git init", "git clone ", "git pull", "git fetch",
    # OLD

    # Python
    "python ", "python3 ", "py ",
    "pip list", "pip show", "pip install ", "pip freeze",
    "pytest ", "python -m ",
    # File & folder
    "dir", "ls", "cd", "pwd", "type", "cat", "tree",
    "echo", "where", "which",
    "mkdir ", "md ", "copy ", "cp ", "move ", "mv ",
    "ren ", "touch ",
    # Git
    "git status", "git log", "git diff", "git branch",
    "git add ", "git commit ", "git init", "git clone ",
    # Editor
    "code ", "notepad ",
]

BLACKLIST_CMD = [
    "rm -rf", "rm -r", "rmdir /s",
    "del /f", "del /q", "del /s",
    "format ", "shutdown", "restart",
    "net user", "reg delete", "reg add",
    "taskkill /f", "kill -9",
    "pip uninstall",
    "git push", "git reset --hard",
]


# === Guard file sensitif (amankan_kontrol 30/09) ===
try:
    from safety_kontrol import cek_blokir
except ImportError:  # fallback: cari modulnya manual
    import sys as _sys_guard
    _sys_guard.path.insert(0, str(Path("E:/Project Software/Orion") / "core" / "otonom" / "kontrol"))
    try:
        from safety_kontrol import cek_blokir
    except ImportError:
        def cek_blokir(aksi, target=""):
            return False, ""


def _guard_file(aksi, p):
    """Kembalikan dict error bila file diblokir, atau None bila aman."""
    _b, _a = cek_blokir(aksi, str(p))
    if _b:
        return {"sukses": False, "error": f"Ditolak: {_a}"}
    return None


def tulis_file(path: str, isi: str) -> dict:
    """Tulis file ke disk."""
    try:
        # Resolve path
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p

        # Guard file sensitif (amankan_kontrol 30/09)
        _g = _guard_file("tulis", p)
        if _g:
            return _g

        # Bikin folder kalau belum ada
        p.parent.mkdir(parents=True, exist_ok=True)

        # Tulis file
        p.write_text(isi, encoding="utf-8")

        return {
            "sukses": True,
            "path": str(p),
            "ukuran": len(isi),
            "pesan": f"File ditulis: {p}",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def baca_file(path: str) -> dict:
    """Baca file dari disk."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p

        # Guard file sensitif (amankan_kontrol 30/09)
        _g = _guard_file("baca", p)
        if _g:
            return _g

        if not p.exists():
            return {"sukses": False, "error": f"File tidak ditemukan: {p}"}

        isi = p.read_text(encoding="utf-8", errors="ignore")
        return {
            "sukses": True,
            "path": str(p),
            "isi": isi[:5000],  # batasi 5000 char
            "panjang": len(isi),
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def cek_aman(perintah: str) -> tuple:
    """Cek apakah perintah aman dijalankan."""
    p = perintah.lower().strip()

    if not p:
        return False, "Perintah kosong"

    for bad in BLACKLIST_CMD:
        if bad in p:
            return False, f"Perintah terlarang: '{bad}'"

    for good in WHITELIST_CMD:
        if p.startswith(good):
            return True, "OK"

    return False, f"Perintah tidak di whitelist"


def jalankan_terminal(perintah: str, timeout: int = 30) -> dict:
    """Jalankan perintah terminal (aman)."""
    aman, alasan = cek_aman(perintah)
    if not aman:
        return {"sukses": False, "error": alasan}

    try:
        start = time.time()
        result = subprocess.run(
            perintah,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BASE),
            encoding="utf-8",
            errors="ignore",
        )
        durasi = time.time() - start
        output = (result.stdout + result.stderr)[:3000]

        return {
            "sukses": True,
            "output": output,
            "exit_code": result.returncode,
            "durasi": round(durasi, 2),
        }
    except subprocess.TimeoutExpired:
        return {"sukses": False, "error": f"Timeout {timeout} detik"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


# ============================================================
# TOOL BARU: list_file, buat_folder, copy_file, hapus_file
# ============================================================

def list_file(folder: str = ".") -> dict:
    """Lihat isi folder."""
    try:
        p = Path(folder)
        if not p.is_absolute():
            p = BASE / p
        if not p.exists():
            return {"sukses": False, "error": f"Folder tidak ditemukan: {p}"}
        if not p.is_dir():
            return {"sukses": False, "error": f"Bukan folder: {p}"}

        items = []
        for item in p.iterdir():
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            tipe = "folder" if item.is_dir() else "file"
            ukuran = item.stat().st_size if item.is_file() else 0
            items.append({
                "nama": item.name,
                "tipe": tipe,
                "ukuran": ukuran,
            })

        items.sort(key=lambda x: (x["tipe"], x["nama"]))
        return {
            "sukses": True,
            "folder": str(p),
            "jumlah": len(items),
            "items": items[:50],  # batasi 50
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buat_folder(path: str) -> dict:
    """Bikin folder baru."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p
        p.mkdir(parents=True, exist_ok=True)
        return {"sukses": True, "path": str(p), "pesan": f"Folder dibuat: {p}"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def copy_file(sumber: str, tujuan: str) -> dict:
    """Copy file dari sumber ke tujuan."""
    try:
        src = Path(sumber)
        dst = Path(tujuan)
        if not src.is_absolute():
            src = BASE / src
        if not dst.is_absolute():
            dst = BASE / dst

        if not src.exists():
            return {"sukses": False, "error": f"Sumber tidak ada: {src}"}

        # Bikin folder tujuan kalau belum ada
        dst.parent.mkdir(parents=True, exist_ok=True)

        import shutil
        if src.is_file():
            shutil.copy2(src, dst)
            return {
                "sukses": True,
                "sumber": str(src),
                "tujuan": str(dst),
                "pesan": f"File di-copy: {src.name} -> {dst}",
            }
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return {
                "sukses": True,
                "sumber": str(src),
                "tujuan": str(dst),
                "pesan": f"Folder di-copy: {src.name} -> {dst}",
            }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def hapus_file(path: str) -> dict:
    """
    Hapus file - TAPI pindah ke _trash/ dulu (bisa di-restore).
    """
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p

        if not p.exists():
            return {"sukses": False, "error": f"File tidak ditemukan: {p}"}

        # Bikin folder _trash
        trash_dir = BASE / "_trash"
        trash_dir.mkdir(exist_ok=True)

        # Bikin nama unik dengan timestamp
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        target = trash_dir / f"{timestamp}_{p.name}"

        # Pindah ke _trash
        import shutil
        if p.is_file():
            shutil.move(str(p), str(target))
        else:
            shutil.move(str(p), str(target))

        return {
            "sukses": True,
            "path_asli": str(p),
            "path_trash": str(target),
            "pesan": f"File dipindah ke _trash: {p.name}",
            "catatan": "Bisa di-restore dari folder _trash",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def restore_file(nama_trash: str) -> dict:
    """Restore file dari _trash."""
    try:
        trash_dir = BASE / "_trash"
        if not trash_dir.exists():
            return {"sukses": False, "error": "_trash tidak ada"}

        target = trash_dir / nama_trash
        if not target.exists():
            return {"sukses": False, "error": f"Tidak ada di _trash: {nama_trash}"}

        # Hapus timestamp dari nama
        import re
        nama_asli = re.sub(r"^\d{8}_\d{6}_", "", nama_trash)
        tujuan = BASE / nama_asli

        import shutil
        shutil.move(str(target), str(tujuan))

        return {
            "sukses": True,
            "path": str(tujuan),
            "pesan": f"File di-restore: {nama_asli}",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def scan_folder(folder: str = None, output: str = None, max_depth: int = 3) -> dict:
    """Scan folder + simpan struktur ke file txt."""
    from pathlib import Path
    from datetime import datetime
    import json

    if folder is None:
        folder = r"E:\Project Software\Orion"
    if output is None:
        # Simpan di folder luar
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = rf"E:\Project Software\test orion 2\scan_{ts}.txt"

    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}

    exclude = ["__pycache__", ".git", "node_modules", ".venv", ".idea", ".vscode"]
    items = []
    total_file = 0
    total_size = 0

    def walk(path, depth=0):
        nonlocal total_file, total_size
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except (PermissionError, OSError):
            return
        for item in entries:
            if item.name in exclude:
                continue
            rel = item.relative_to(root)
            if item.is_dir():
                items.append({"type": "dir", "path": str(rel), "depth": depth})
                walk(item, depth + 1)
            else:
                try:
                    size = item.stat().st_size
                except OSError:
                    size = 0
                items.append({"type": "file", "path": str(rel), "size": size, "depth": depth})
                total_file += 1
                total_size += size

    walk(root)

    # Format teks
    lines = []
    lines.append("=" * 60)
    lines.append("ORION FOLDER SCAN")
    lines.append("=" * 60)
    lines.append(f"Root       : {root}")
    lines.append(f"Waktu      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total file : {total_file}")
    lines.append(f"Total size : {total_size:,} B")
    lines.append("=" * 60)
    lines.append("")
    for item in items:
        indent = "  " * item["depth"]
        if item["type"] == "dir":
            lines.append(f"{indent}[DIR] {Path(item['path']).name}/")
        else:
            lines.append(f"{indent}  {Path(item['path']).name}  ({item['size']} B)")

    teks = "\n".join(lines)

    # Tulis output
    out = Path(output)
    if not out.is_absolute():
        out = Path(r"E:\Project Software") / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(teks, encoding="utf-8")

    return {
        "sukses": True,
        "file": str(out),
        "total_file": total_file,
        "total_size": total_size,
    }



def kenalan_folder(folder: str) -> dict:
    """Kenalan dengan folder - pahami struktur proyek."""
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    scan = scan_folder(folder=str(root))
    total_file = scan.get("total_file", 0)
    file_penting = ["README.md", "main.py", "app.py", "index.py", "requirements.txt"]
    isi_file = {}
    for nama in file_penting:
        p = root / nama
        if p.exists():
            try:
                isi_file[nama] = p.read_text(encoding="utf-8", errors="ignore")[:1500]
            except Exception:
                pass
    try:
        from model_router import panggil_model
        prompt = "Analisis folder proyek ini. Path: " + folder + "\nTotal file: " + str(total_file) + "\n\n" + "\n".join("=== " + k + " ===\n" + v for k, v in list(isi_file.items())[:5]) + "\n\nRingkas proyek ini 5-8 baris: nama, fungsi, tech stack, struktur. Bahasa Indonesia santai."
        r = panggil_model(messages=[{"role": "user", "content": prompt}], tugas="analisis", max_tokens=500)
        ringkasan = r.get("konten", "(gagal)")
    except Exception as e:
        ringkasan = "Error: " + str(e)
    return {"sukses": True, "folder": str(folder), "total_file": total_file, "ringkasan": ringkasan}


def analisis_folder(folder: str, max_file: int = 5) -> dict:
    """Analisis folder - cari bug."""
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    py_files = list(root.rglob("*.py"))
    if not py_files:
        return {"sukses": False, "error": "Tidak ada .py"}
    hasil = []
    diproses = 0
    for py_file in py_files[:max_file]:
        try:
            kode = py_file.read_text(encoding="utf-8", errors="ignore")
            if len(kode.strip()) < 50:
                continue
            if len(kode) > 4000:
                kode = kode[:4000]
            from model_router import panggil_model
            prompt = "Analisis kode Python ini. Cari BUG: error handling, path salah, API key hardcoded, loop infinite, typo. FILE: " + py_file.name + "\n" + kode + "\n\nKalau AMAN bilang AMAN. Kalau ada bug, lapor baris + cara fix. Max 5 baris."
            r = panggil_model(messages=[{"role": "user", "content": prompt}], tugas="coding", max_tokens=400)
            analisis = r.get("konten", "")
            if "AMAN" not in analisis.upper():
                hasil.append({"file": str(py_file.relative_to(root)), "analisis": analisis})
            diproses += 1
        except Exception:
            pass
    return {"sukses": True, "folder": str(folder), "total_py": len(py_files), "diproses": diproses, "bug_ditemukan": len(hasil), "hasil": hasil}


def fix_bug(file_path: str) -> dict:
    """Fix bug di 1 file."""
    from pathlib import Path
    import shutil
    from datetime import datetime
    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}
    try:
        kode_asli = p.read_text(encoding="utf-8")
    except Exception as e:
        return {"sukses": False, "error": str(e)}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.parent / (p.name + ".bak_" + ts)
    try:
        shutil.copy(p, backup)
    except Exception as e:
        return {"sukses": False, "error": "Backup gagal: " + str(e)}
    try:
        from model_router import panggil_model
        prompt = "Fix bug di kode Python ini. Output HANYA kode Python fixed, tanpa penjelasan.\n\n" + kode_asli[:4000]
        r = panggil_model(messages=[{"role": "user", "content": prompt}], tugas="coding", max_tokens=3000)
        kode_baru = r.get("konten", "")
        import re
        kode_baru = re.sub(r"^```python\s*\n", "", kode_baru)
        kode_baru = re.sub(r"^```\s*\n", "", kode_baru)
        kode_baru = re.sub(r"\n```\s*$", "", kode_baru).strip()
        if not kode_baru or len(kode_baru) < 20:
            return {"sukses": False, "error": "LLM gagal"}
        p.write_text(kode_baru, encoding="utf-8")
        import subprocess
        result = subprocess.run(["python", "-m", "py_compile", str(p)], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            shutil.copy(backup, p)
            return {"sukses": False, "error": "Syntax error, rollback"}
        return {"sukses": True, "file": str(p), "backup": str(backup)}
    except Exception as e:
        try:
            shutil.copy(backup, p)
        except Exception:
            pass
        return {"sukses": False, "error": str(e)}




def analisis_file(file_path: str) -> dict:
    """Analisis 1 file Python - cari bug."""
    from pathlib import Path
    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}
    try:
        kode = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return {"sukses": False, "error": str(e)}
    if len(kode.strip()) < 20:
        return {"sukses": True, "hasil": "File kosong"}
    kode_potong = kode[:5000]
    try:
        from model_router import panggil_model
        prompt = "Analisis kode Python ini. Cari BUG/ERROR.\n\nFILE: " + p.name + "\n\n" + kode_potong + "\n\nCari: syntax error, import salah, path Windows salah, API key hardcoded, error handling bolong, loop infinite, fungsi hilang. Kalau AMAN bilang AMAN. Kalau ada bug, lapor baris + fix. Max 10 baris."
        r = panggil_model(messages=[{"role": "user", "content": prompt}], tugas="coding", max_tokens=800)
        return {"sukses": True, "file": str(p), "analisis": r.get("konten", "")}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def fix_file(file_path: str, instruksi: str = "") -> dict:
    """Fix bug di 1 file - pakai LLM."""
    from pathlib import Path
    import shutil
    from datetime import datetime
    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}
    try:
        kode_asli = p.read_text(encoding="utf-8")
    except Exception as e:
        return {"sukses": False, "error": str(e)}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.parent / (p.name + ".bak_" + ts)
    try:
        shutil.copy(p, backup)
    except Exception as e:
        return {"sukses": False, "error": "Backup gagal: " + str(e)}
    try:
        from model_router import panggil_model
        ins = instruksi if instruksi else "Cari dan fix semua bug."
        prompt = "Fix bug di kode Python ini. FILE: " + p.name + "\n\nINSTRUKSI: " + ins + "\n\nKODE:\n" + kode_asli[:6000] + "\n\nATURAN: Output HANYA kode Python fixed, tanpa penjelasan, tanpa markdown, tanpa ```python.\n\nKODE FIXED:"
        r = panggil_model(messages=[{"role": "user", "content": prompt}], tugas="coding", max_tokens=8000)
        kode_baru = r.get("konten", "")
        import re
        kode_baru = re.sub(r"^```python\s*\n", "", kode_baru)
        kode_baru = re.sub(r"^```\s*\n", "", kode_baru)
        kode_baru = re.sub(r"\n```\s*$", "", kode_baru)
        kode_baru = kode_baru.strip()
        if not kode_baru or len(kode_baru) < 20:
            return {"sukses": False, "error": "LLM tidak generate kode"}
        p.write_text(kode_baru, encoding="utf-8")
        import subprocess
        result = subprocess.run(["python", "-m", "py_compile", str(p)], capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            shutil.copy(backup, p)
            return {"sukses": False, "error": "Syntax error, rollback", "backup": str(backup)}
        return {"sukses": True, "file": str(p), "backup": str(backup)}
    except Exception as e:
        try:
            shutil.copy(backup, p)
        except Exception:
            pass
        return {"sukses": False, "error": str(e)}


def scan_folder_full(folder: str, pattern: str = "*.py") -> dict:
    """Scan folder - return list file."""
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    files = list(root.rglob(pattern))
    return {"sukses": True, "folder": str(folder), "total": len(files), "files": [str(f.relative_to(root)) for f in files]}


def _cari_devenv():
    """Cari devenv.exe Visual Studio 2022."""
    from pathlib import Path
    paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\devenv.exe",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
    ]
    for p in paths:
        if Path(p).exists():
            return p
    return None


def _cari_vscode():
    """Cari code.exe VSCode."""
    from pathlib import Path
    import os
    paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "Code.exe",
        Path(r"C:\Program Files\Microsoft VS Code\Code.exe"),
        Path(r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"),
    ]
    for p in paths:
        if p.exists():
            return str(p)
    return None


def buka_vs2022(path: str = None) -> dict:
    """Buka Visual Studio 2022."""
    import subprocess
    devenv = _cari_devenv()
    if not devenv:
        return {"sukses": False, "error": "Visual Studio 2022 tidak ditemukan"}
    try:
        if path:
            subprocess.Popen([devenv, path], shell=False)
            return {"sukses": True, "pesan": f"VS 2022 buka: {path}", "app": "vs2022"}
        else:
            subprocess.Popen([devenv], shell=False)
            return {"sukses": True, "pesan": "VS 2022 dibuka", "app": "vs2022"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_vscode(path: str = None) -> dict:
    """Buka VSCode - fallback ke VS 2022."""
    import subprocess
    vscode = _cari_vscode()
    if vscode:
        try:
            if path:
                subprocess.Popen([vscode, path], shell=False)
            else:
                subprocess.Popen([vscode], shell=False)
            return {"sukses": True, "pesan": f"VSCode buka: {path or 'default'}", "app": "vscode"}
        except Exception as e:
            return {"sukses": False, "error": str(e)}
    # Fallback ke VS 2022
    print("[VSCode] Tidak ditemukan, pakai VS 2022")
    return buka_vs2022(path=path)


def buka_cmd(path: str = None) -> dict:
    """Buka Command Prompt."""
    import subprocess
    import os
    try:
        cwd = path or os.getcwd()
        subprocess.Popen(["cmd.exe", "/K", "cd", "/d", cwd], shell=False)
        return {"sukses": True, "pesan": f"CMD dibuka di {cwd}", "app": "cmd"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_powershell(path: str = None) -> dict:
    """Buka PowerShell."""
    import subprocess
    import os
    try:
        cwd = path or os.getcwd()
        subprocess.Popen(["powershell.exe", "-NoExit", "-Command", f"cd '{cwd}'"], shell=False)
        return {"sukses": True, "pesan": f"PowerShell dibuka di {cwd}", "app": "powershell"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_windows_terminal(path: str = None) -> dict:
    """Buka Windows Terminal."""
    import subprocess
    import os
    try:
        cwd = path or os.getcwd()
        subprocess.Popen(["wt.exe", "-d", cwd], shell=False)
        return {"sukses": True, "pesan": f"Windows Terminal dibuka di {cwd}", "app": "wt"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_notepad(path: str = None) -> dict:
    """Buka Notepad."""
    import subprocess
    try:
        if path:
            subprocess.Popen(["notepad.exe", path], shell=False)
        else:
            subprocess.Popen(["notepad.exe"], shell=False)
        return {"sukses": True, "pesan": f"Notepad buka: {path or 'baru'}", "app": "notepad"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_file(path: str) -> dict:
    """Buka file dengan app default."""
    import subprocess
    try:
        subprocess.Popen(["start", path], shell=True)
        return {"sukses": True, "pesan": f"Buka: {path}", "app": "default"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def buka_terminal(app: str, path: str = None) -> dict:
    """Router buka terminal/app."""
    app = app.lower().strip()
    if app in ("vs2022", "vs", "visual studio", "visual studio 2022"):
        return buka_vs2022(path)
    if app in ("vscode", "code", "vs code"):
        return buka_vscode(path)
    if app in ("cmd", "command prompt"):
        return buka_cmd(path)
    if app in ("powershell", "ps", "pwsh"):
        return buka_powershell(path)
    if app in ("wt", "windows terminal"):
        return buka_windows_terminal(path)
    if app == "notepad":
        return buka_notepad(path)
    return {"sukses": False, "error": f"App tidak dikenal: {app}"}


def baca_log(log_path: str, max_lines: int = 100) -> dict:
    """Baca log error terbaru."""
    from pathlib import Path
    p = Path(log_path)
    if not p.exists():
        return {"sukses": False, "error": f"Log tidak ada: {log_path}"}
    try:
        with io.open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        tail = lines[-max_lines:] if len(lines) > max_lines else lines
        return {"sukses": True, "file": str(p), "total": len(lines), "isi": "".join(tail)}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def analisis_error(traceback_str: str) -> dict:
    """Dari traceback - cari file + baris + saran fix."""
    import re
    # Cari pola File "...", line N
    matches = re.findall(r'File "([^"]+)", line (\d+)', traceback_str)
    if not matches:
        return {"sukses": False, "error": "Traceback tidak valid"}
    
    lokasi = [{"file": m[0], "line": int(m[1])} for m in matches]
    
    # Ambil error terakhir
    error_lines = [l for l in traceback_str.split("\n") if l.strip() and not l.strip().startswith("File") and not l.strip().startswith("at ")]
    error_msg = error_lines[-1] if error_lines else "?"
    
    # Cari file utama (dari project)
    file_utama = None
    for lok in lokasi:
        if "Nexus.ai" in lok["file"] or "Orion" in lok["file"]:
            file_utama = lok
            break
    
    if not file_utama:
        file_utama = lokasi[-1] if lokasi else None
    
    return {
        "sukses": True,
        "lokasi": lokasi,
        "file_utama": file_utama,
        "error": error_msg[:300],
        "total_frame": len(lokasi),
    }


def analisis_multi(files: list, max_file: int = 5) -> dict:
    """Analisis beberapa file sekaligus."""
    hasil = []
    for fp in files[:max_file]:
        r = analisis_file(fp)
        hasil.append({
            "file": fp,
            "sukses": r.get("sukses"),
            "analisis": r.get("analisis", "")[:500] if r.get("sukses") else r.get("error", ""),
        })
    return {"sukses": True, "total": len(hasil), "hasil": hasil}


def fix_multi(files: list, max_file: int = 5) -> dict:
    """Fix beberapa file sekaligus."""
    hasil = []
    for fp in files[:max_file]:
        r = fix_file(fp)
        hasil.append({
            "file": fp,
            "sukses": r.get("sukses"),
            "backup": r.get("backup"),
            "error": r.get("error"),
        })
    sukses_count = sum(1 for h in hasil if h.get("sukses"))
    return {"sukses": sukses_count > 0, "total": len(hasil), "sukses_count": sukses_count, "hasil": hasil}


def fix_sampai_jalan(file_path: str, test_cmd: str = None, max_loop: int = 5) -> dict:
    """Fix file sampai test jalan."""
    import subprocess
    from pathlib import Path
    
    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}
    
    if not test_cmd:
        test_cmd = f'python -m py_compile "{file_path}"'
    
    history = []
    for loop in range(1, max_loop + 1):
        print(f"[Loop {loop}/{max_loop}]")
        
        # Test dulu
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"sukses": True, "loop": loop, "history": history, "pesan": "Test berhasil"}
            error_output = (result.stdout + result.stderr)[:500]
        except Exception as e:
            error_output = str(e)
        
        print(f"  Test gagal: {error_output[:100]}")
        
        # Fix
        hasil_fix = fix_file(file_path, instruksi=f"Test error: {error_output[:300]}")
        history.append({"loop": loop, "error": error_output[:200], "fix_sukses": hasil_fix.get("sukses")})
        
        if not hasil_fix.get("sukses"):
            return {"sukses": False, "loop": loop, "history": history, "error": hasil_fix.get("error")}
    
    return {"sukses": False, "loop": max_loop, "history": history, "error": "Max loop reached"}


def cari_string(folder: str, pattern: str, max_file: int = 50, max_match: int = 100) -> dict:
    """Cari string di semua file dalam folder."""
    from pathlib import Path
    import re
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    hasil = []
    total_match = 0
    scanned = 0
    
    for fp in root.rglob("*"):
        if not fp.is_file():
            continue
        # Skip file besar & biner
        try:
            size = fp.stat().st_size
            if size > 5 * 1024 * 1024:  # > 5 MB
                continue
        except Exception:
            continue
        
        # Skip file biner
        if fp.suffix.lower() in (".pyc", ".pyo", ".exe", ".dll", ".zip", ".7z", ".rar",
                                  ".jpg", ".png", ".gif", ".mp4", ".mp3", ".ico", ".db"):
            continue
        
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        scanned += 1
        if scanned > max_file:
            break
        
        for i, line in enumerate(text.split("\n"), 1):
            if pattern.lower() in line.lower():
                hasil.append({
                    "file": str(fp.relative_to(root)),
                    "line": i,
                    "isi": line.strip()[:200],
                })
                total_match += 1
                if total_match >= max_match:
                    break
        if total_match >= max_match:
            break
    
    return {
        "sukses": True,
        "folder": str(folder),
        "pattern": pattern,
        "scanned": scanned,
        "total_match": total_match,
        "hasil": hasil,
    }


def analisis_dependency(folder: str, max_file: int = 20) -> dict:
    """Analisis import graph antar file."""
    from pathlib import Path
    import re
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": f"Folder tidak ada: {folder}"}
    
    py_files = list(root.rglob("*.py"))[:max_file]
    graph = {}
    masalah = []
    
    for fp in py_files:
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        rel = str(fp.relative_to(root))
        imports = []
        for m in re.finditer(r"^(?:from|import)\s+([\w\.]+)", text, re.MULTILINE):
            imports.append(m.group(1))
        
        graph[rel] = imports
        
        # Cek import yang tidak ada file-nya
        for imp in imports:
            imp_file = imp.replace(".", "/") + ".py"
            if not (root / imp_file).exists() and not (root / imp / "__init__.py").exists():
                # Cek local import
                if not imp.startswith(("os", "sys", "re", "json", "time", "io", "pathlib",
                                        "subprocess", "typing", "datetime", "collections",
                                        "threading", "asyncio", "shutil", "random", "math",
                                        "requests", "discord", "flask", "openai", "groq",
                                        "dotenv", "numpy", "pandas")):
                    masalah.append({"file": rel, "import": imp, "masalah": "File import tidak ketemu"})
    
    return {"sukses": True, "folder": str(folder), "total_file": len(graph), "graph": graph, "masalah": masalah[:20]}


def git_init(folder: str) -> dict:
    """Init git repo."""
    import subprocess
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    try:
        r = subprocess.run(["git", "init"], cwd=str(root), capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            # Bikin .gitignore
            gi = root / ".gitignore"
            if not gi.exists():
                gi.write_text("__pycache__/\n*.pyc\n*.log\n.env\n*.db\nbackups/\n_temp/\n", encoding="utf-8")
            return {"sukses": True, "pesan": "Git initialized"}
        return {"sukses": False, "error": r.stderr[:300]}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def git_commit(folder: str, message: str = "Auto-commit by Orion") -> dict:
    """Git add + commit."""
    import subprocess
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    try:
        subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, text=True, timeout=30)
        r = subprocess.run(["git", "commit", "-m", message], cwd=str(root), capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return {"sukses": True, "pesan": f"Commit: {message}"}
        elif "nothing to commit" in r.stdout.lower():
            return {"sukses": True, "pesan": "Tidak ada perubahan"}
        return {"sukses": False, "error": r.stderr[:300]}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def git_status(folder: str) -> dict:
    """Cek git status."""
    import subprocess
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    try:
        r = subprocess.run(["git", "status", "--short"], cwd=str(root), capture_output=True, text=True, timeout=30)
        return {"sukses": True, "output": r.stdout[:1500]}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def jalankan_test(folder: str, test_cmd: str = "python -m pytest -x") -> dict:
    """Jalankan test suite."""
    import subprocess
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    try:
        r = subprocess.run(test_cmd, cwd=str(root), capture_output=True, text=True, timeout=120, shell=True)
        output = (r.stdout + r.stderr)[:2000]
        return {"sukses": r.returncode == 0, "exit_code": r.returncode, "output": output}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def fix_folder(folder: str, max_file: int = 10, auto_fix: bool = True) -> dict:
    """Scan folder → analisis → fix 1-1."""
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    
    # 1. Analisis folder
    analisis = analisis_folder(folder, max_file=max_file)
    if not analisis.get("sukses"):
        return analisis
    
    hasil_fix = []
    total_bug = analisis.get("bug_ditemukan", 0)
    
    if auto_fix:
        # 2. Fix setiap file yang bug
        for item in analisis.get("hasil", [])[:max_file]:
            file_path = item.get("file", "")
            if not file_path:
                continue
            # Resolve full path
            full_path = str((root / file_path).resolve())
            # Fix file
            fix_hasil = fix_file(full_path)
            hasil_fix.append({
                "file": file_path,
                "fix_sukses": fix_hasil.get("sukses"),
                "backup": fix_hasil.get("backup"),
                "error": fix_hasil.get("error"),
            })
    
    sukses_count = sum(1 for h in hasil_fix if h.get("fix_sukses"))
    return {
        "sukses": True,
        "folder": str(folder),
        "total_bug": total_bug,
        "total_fix": len(hasil_fix),
        "sukses_fix": sukses_count,
        "hasil": hasil_fix,
    }


def trace_error(folder: str, cmd: str, max_fix: int = 3) -> dict:
    """Jalankan → tangkap error → fix → ulangi."""
    import subprocess
    from pathlib import Path
    root = Path(folder)
    if not root.exists():
        return {"sukses": False, "error": "Folder tidak ada"}
    
    history = []
    for i in range(1, max_fix + 1):
        print(f"[Trace {i}/{max_fix}] Jalankan: {cmd}")
        try:
            r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=60, shell=True)
            if r.returncode == 0:
                return {"sukses": True, "loop": i, "history": history, "output": (r.stdout + r.stderr)[:1000]}
            
            error_output = (r.stdout + r.stderr)[:1000]
            print(f"  Error: {error_output[:200]}")
            
            # Cari file dari error
            import re
            matches = re.findall(r'File "([^"]+)", line (\d+)', error_output)
            if not matches:
                return {"sukses": False, "loop": i, "error": "Error tidak ditemukan file", "output": error_output}
            
            target = matches[0][0]
            history.append({"loop": i, "error_file": target, "error": error_output[:300]})
            
            # Fix file
            fix_hasil = fix_file(target, instruksi=f"Error: {error_output[:300]}")
            if not fix_hasil.get("sukses"):
                return {"sukses": False, "loop": i, "error": fix_hasil.get("error"), "history": history}
        
        except Exception as e:
            return {"sukses": False, "error": str(e), "loop": i, "history": history}
    
    return {"sukses": False, "loop": max_fix, "error": "Max fix reached", "history": history}


def fix_baris(file_path: str, baris_ke: int, teks_lama: str, teks_baru: str) -> dict:
    """Ganti teks di baris tertentu - tanpa LLM."""
    from pathlib import Path
    import shutil
    from datetime import datetime

    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.parent / f"{p.name}.bak_{ts}"
    try:
        shutil.copy(p, backup)
    except Exception as e:
        return {"sukses": False, "error": f"Backup gagal: {e}"}

    try:
        lines = p.read_text(encoding="utf-8").split("\n")
    except Exception as e:
        return {"sukses": False, "error": str(e)}

    if not (0 < baris_ke <= len(lines)):
        return {"sukses": False, "error": f"Baris {baris_ke} di luar range (1-{len(lines)})"}

    old_line = lines[baris_ke - 1]
    if teks_lama not in old_line:
        return {"sukses": False, "error": f"Teks '{teks_lama}' tidak ada di baris {baris_ke}: {old_line.strip()}"}

    new_line = old_line.replace(teks_lama, teks_baru)
    lines[baris_ke - 1] = new_line
    p.write_text("\n".join(lines), encoding="utf-8")

    return {
        "sukses": True,
        "file": str(p),
        "baris": baris_ke,
        "lama": old_line.strip(),
        "baru": new_line.strip(),
        "backup": str(backup),
    }


def fix_fungsi(file_path, nama_fungsi, instruksi="perbaiki bug"):
    """Fix 1 fungsi spesifik - tanpa rewrite seluruh file."""
    from pathlib import Path
    import shutil
    import re
    from datetime import datetime

    p = Path(file_path)
    if not p.exists():
        return {"sukses": False, "error": "File tidak ada"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.parent / f"{p.name}.bak_{ts}"
    shutil.copy(p, backup)

    kode = p.read_text(encoding="utf-8")

    # Cari fungsi
    pattern = rf"(def {nama_fungsi}\(.*?(?=\ndef |\nclass |\Z))"
    match = re.search(pattern, kode, re.DOTALL)

    if not match:
        return {"sukses": False, "error": f"Fungsi '{nama_fungsi}' tidak ketemu"}

    fungsi_lama = match.group(1)

    # Kirim ke LLM
    try:
        from model_router import panggil_model
        prompt = f"""Fix fungsi Python ini.

INSTRUKSI: {instruksi}

FUNGSI LAMA:
{fungsi_lama[:3000]}

ATURAN:
- Output HANYA kode fungsi yang sudah diperbaiki
- JANGAN ada penjelasan, markdown, atau ```python
- JANGAN hapus fungsi lain
- Output fungsi lengkap (def + body)

FUNGSI BARU:"""

        r = panggil_model(
            messages=[{"role": "user", "content": prompt}],
            tugas="coding",
            max_tokens=2000,
        )
        fungsi_baru = r.get("konten", "")

        # Bersihkan markdown
        fungsi_baru = re.sub(r"^```python\s*\n", "", fungsi_baru)
        fungsi_baru = re.sub(r"^```\s*\n", "", fungsi_baru)
        fungsi_baru = re.sub(r"\n```\s*$", "", fungsi_baru)
        fungsi_baru = fungsi_baru.strip()

        if not fungsi_baru or len(fungsi_baru) < 20:
            return {"sukses": False, "error": "LLM gagal generate"}

        # Ganti fungsi
        kode_baru = kode.replace(fungsi_lama, fungsi_baru)
        p.write_text(kode_baru, encoding="utf-8")

        # Test syntax
        import subprocess
        result = subprocess.run(
            ["python", "-m", "py_compile", str(p)],
            capture_output=True, text=True, timeout=15,
        )

        if result.returncode != 0:
            shutil.copy(backup, p)
            return {"sukses": False, "error": "Syntax error, rollback", "backup": str(backup)}

        return {"sukses": True, "file": str(p), "fungsi": nama_fungsi, "backup": str(backup)}
    except Exception as e:
        try:
            shutil.copy(backup, p)
        except Exception:
            pass
        return {"sukses": False, "error": str(e)}


def cek_status() -> str:
    return f"Tool eksekusi: siap (cwd={BASE})"


__all__ = ["tulis_file", "baca_file", "jalankan_terminal", "list_file", "buat_folder", "copy_file", "hapus_file", "restore_file", "cek_status"]
