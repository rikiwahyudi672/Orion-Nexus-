"""Skill coding-assistant - wrapper untuk coding/coding_assistant.py."""
import sys
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent.parent
if str(_BASE) not in sys.path:
    sys.path.insert(0, str(_BASE))
if str(_BASE / "coding") not in sys.path:
    sys.path.insert(0, str(_BASE / "coding"))

try:
    import coding_assistant as _ca
except ImportError:
    from coding import coding_assistant as _ca


def jalankan(argumen=""):
    """Jalankan coding assistant.

    Format argumen:
      - "tulis:<path>:<kode>"  -> tulis file kode
      - "baca:<path>"          -> baca file kode
      - "run:<path>"           -> jalankan file python
      - "<goal bebas>"         -> coding_loop: tulis + jalankan + fix otomatis
    """
    arg = (argumen or "").strip()
    if not arg:
        return {"sukses": False, "pesan": "Kasih goal atau perintah. Contoh: 'buatin fungsi faktorial'"}
    try:
        if arg.startswith("tulis:"):
            _, path, kode = arg.split(":", 2)
            return _ca.tulis_kode(path.strip(), kode)
        if arg.startswith("baca:"):
            return {"sukses": True, "isi": _ca.baca_kode(arg[5:].strip())}
        if arg.startswith("run:") or arg.startswith("jalankan:"):
            path = arg.split(":", 1)[1].strip()
            return _ca.jalankan_kode(path)
        # default: anggap goal -> coding loop otomatis
        return _ca.coding_loop(arg)
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def info():
    return {"nama": "coding-assistant",
            "deskripsi": "Tulis, baca, jalankan, dan perbaiki kode Python otomatis."}
