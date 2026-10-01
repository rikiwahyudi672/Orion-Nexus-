import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
cron_orion.py - Cron sederhana untuk ORION.
Format jadwal: HH:MM
"""
import json
import threading
import time
from datetime import datetime
from pathlib import Path

# TOOL_HUB_IMPORT
try:
    import tool_hub
    TOOL_HUB_AVAILABLE = True
except ImportError:
    TOOL_HUB_AVAILABLE = False


# TOOL_EKSEKUSI_IMPORT
try:
    import tool_eksekusi as te
    TOOL_AVAILABLE = True
except ImportError:
    TOOL_AVAILABLE = False


BASE = Path(__file__).parent
TASKS_FILE = BASE / "cron_tasks.json"
LOG_FILE = BASE / "logs" / "cron.log"
LOG_FILE.parent.mkdir(exist_ok=True)

_thread = None
_stop = threading.Event()
_aktif = False
_last_run = {}  # catat task terakhir jalan


def _log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def load_tasks():
    """Baca task dari JSON. Kalau belum ada, bikin default."""
    if not TASKS_FILE.exists():
        default = {
            "tasks": [
                {"jam": "08:00", "pesan": "Selamat pagi bos. Hari ini siap kerja?"},
                {"jam": "09:30", "pesan": "Bos, jangan lupa minum air. Serius."},
                {"jam": "12:00", "pesan": "Waktunya makan siang, Riki. Jangan skip."},
                {"jam": "15:00", "pesan": "Bos, postur lo benerin. Bungkuk itu."},
                {"jam": "17:30", "pesan": "Riki, hari udah sore. Cek target hari ini udah kelar?"},
                {"jam": "20:00", "pesan": "Bos, udah waktunya santai. Jangan kerja terus."},
                {"jam": "22:00", "pesan": "Udah malem, Riki. Istirahat."},
                {"jam": "23:30", "pesan": "Bos, tidur. Besok masih ada kerjaan."},
            ]
        }
        TASKS_FILE.write_text(json.dumps(default, indent=2, ensure_ascii=False), encoding="utf-8")
        return default["tasks"]
    try:
        data = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        return data.get("tasks", [])
    except Exception as e:
        _log(f"Error baca tasks: {e}")
        return []


def save_tasks(tasks):
    """Simpan task ke JSON."""
    TASKS_FILE.write_text(
        json.dumps({"tasks": tasks}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# IMPORT_OTAK
try:
    from otak_orion import diskusi
except ImportError:
    diskusi = None


def _loop(tts_func=None):
    """Loop background: cek tiap 30 detik."""
    global _aktif
    while not _stop.is_set():
        try:
            now = datetime.now()
            jam_sekarang = now.strftime("%H:%M")
            tanggal_sekarang = now.strftime("%Y-%m-%d")
            tasks = load_tasks()

            for i, t in enumerate(tasks):
                jam_task = t.get("jam", "")
                pesan = t.get("pesan", "")
                aksi = t.get("aksi", "tts")
                # Skip kalau nggak ada jam, atau (tts tapi nggak ada pesan)
                if not jam_task:
                    continue
                if aksi == "tts" and not pesan:
                    continue
                if t.get("aktif") is False:
                    continue

                # Cek jam cocok (toleransi 1 menit)
                jam_cocok = False
                if jam_task == jam_sekarang:
                    jam_cocok = True
                else:
                    # Cek kalau task kelewatan (dalam 2 menit terakhir)
                    try:
                        from datetime import datetime as _dt, timedelta
                        jam_task_dt = _dt.strptime(f"{tanggal_sekarang} {jam_task}", "%Y-%m-%d %H:%M")
                        selisih = (now - jam_task_dt).total_seconds()
                        if 0 <= selisih <= 120:  # toleransi 2 menit
                            jam_cocok = True
                    except Exception:
                        pass

                if jam_cocok:
                    # Cek udah jalan hari ini?
                    kunci = f"{i}_{tanggal_sekarang}_{jam_task}"
                    if kunci in _last_run:
                        continue
                    _last_run[kunci] = True

                    # Eksekusi
                    
                    if aksi == "perintah":
                        _jalan_tugas(t, jam_task)
                    elif aksi == "maintenance":
                        try:
                            import maintenance_orion
                            maintenance_orion.maintenance_harian()
                            _log(f"Maintenance OK")
                        except Exception as e:
                            _log(f"Maintenance error: {e}")
                    elif aksi == "llm":
                        # Task pinter pakai LLM
                        try:
                            import cron_llm
                            hasil = cron_llm.eksekusi_task_llm(t)
                            if hasil:
                                _log(f"LLM: {jam_task} - {hasil[:80]}")
                            else:
                                _log(f"LLM: {jam_task} - [DIAM]")
                        except Exception as e:
                            _log(f"LLM error: {e}")
                    else:
                        # Task statis (TTS biasa)
                        print(f"\n  ⏰ [cron] {jam_task}: {pesan}")
                        _log(f"Jalan: {jam_task} - {pesan}")
                        if tts_func:
                            try:
                                tts_func(pesan)
                            except Exception as e:
                                _log(f"TTS error: {e}")

            # Bersihin cache lama (biar nggak numpuk)
            if len(_last_run) > 200:
                _last_run.clear()

        except Exception as e:
            _log(f"Loop error: {e}")

        # Tunggu 10 detik (cek stop tiap detik)
        for _ in range(10):
            if _stop.is_set():
                return
            time.sleep(1)


def mulai(tts_func=None):
    """Mulai thread cron."""
    global _thread, _aktif
    if _thread and _thread.is_alive():
        return False
    _stop.clear()
    _thread = threading.Thread(target=_loop, args=(tts_func,), daemon=True)
    _thread.start()
    _aktif = True
    _log("Cron dimulai")
    return True


def stop():
    """Stop thread cron."""
    global _aktif
    _stop.set()
    _aktif = False
    _log("Cron dihentikan")


def status():
    """Status cron."""
    return {
        "aktif": _aktif,
        "thread_alive": _thread.is_alive() if _thread else False,
        "total_tasks": len(load_tasks()),
        "tasks_file": str(TASKS_FILE),
    }


def tambah_task(jam, pesan):
    """Tambah task baru."""
    tasks = load_tasks()
    tasks.append({"jam": jam, "pesan": pesan})
    save_tasks(tasks)
    return True


def hapus_task(index):
    """Hapus task berdasarkan index."""
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
        return True
    return False


if __name__ == "__main__":
    print("=== Test cron_orion ===")
    st = status()
    print(f"Status: {st}")
    print(f"Tasks file: {st['tasks_file']}")
    print()
    tasks = load_tasks()
    print(f"Total task: {len(tasks)}")
    for i, t in enumerate(tasks):
        print(f"  [{i}] {t['jam']} -> {t['pesan'][:50]}")

_KU_CACHE = None

def _cari_kontrol_utama():
    """Import kontrol_utama.py (dicache). Return modul atau None."""
    # JANGKAR: root Orion dari lokasi cron (perbaiki_cron_ku)
    global _KU_CACHE
    if _KU_CACHE is not None:
        return _KU_CACHE
    import importlib.util
    import os
    import sys
    from pathlib import Path
    cron_dir = Path(__file__).resolve().parent
    # Root Orion = 1 level di atas folder cron (support/). Jangan andalkan
    # BASE karena di proses cron BASE bisa mengarah ke folder support.
    root = cron_dir.parent
    kandidat = [
        root / "core" / "otonom" / "kontrol" / "kontrol_utama.py",
        cron_dir / "kontrol_utama.py",
    ]
    try:
        kandidat.append(Path(BASE) / "core" / "otonom" / "kontrol" / "kontrol_utama.py")
    except NameError:
        pass
    target = None
    for k in kandidat:
        try:
            if k.is_file():
                target = k
                break
        except Exception:
            continue
    if target is None:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", "_arsip", "node_modules")]
            if "kontrol_utama.py" in filenames:
                target = Path(dirpath) / "kontrol_utama.py"
                break
    if target is None:
        _log("kontrol_utama.py tidak ketemu")
        return None
    try:
        sys.path.insert(0, str(target.parent))
        spec = importlib.util.spec_from_file_location("kontrol_utama", str(target))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _KU_CACHE = mod
        return mod
    except Exception as e:
        _log(f"gagal import kontrol_utama: {e}")
        return None

def _toast_cron(judul, pesan):
    import subprocess
    try:
        bersih = pesan.replace('"', "'").replace("\n", " ").strip()[:150]
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, "
            "Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::"
            "GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            '$t.GetElementsByTagName("text")[0].AppendChild('
            '$t.CreateTextNode("' + judul + '")) > $null; '
            '$t.GetElementsByTagName("text")[1].AppendChild('
            '$t.CreateTextNode("' + bersih + '")) > $null; '
            '[Windows.UI.Notifications.ToastNotificationManager]::'
            'CreateToastNotifier("Orion").Show($t)'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            timeout=20, capture_output=True,
        )
    except Exception as e:
        _log(f"toast gagal: {e}")


# SUARA_CRON_F1: bicarakan pesan tugas via voice F1 (non-blocking)
def _speak_async(teks):
    """Bicarakan teks via modul voice (import langsung, bukan tebak-tebakan)."""
    import sys as _sys
    import threading as _th

    def _run():
        try:
            import os as _os
            # pastikan root Orion ada di sys.path (cron jalan dari support/)
            _root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
            if _root not in _sys.path:
                _sys.path.insert(0, _root)
            import tts_orion as _t
            fn = getattr(_t, "bicara", None)
            if not callable(fn):
                _log("voice: bicara tidak callable di tts_orion")
                return
            fn(teks)
            _log(f"voice OK via tts_orion.{getattr(fn, '__name__', '?')}")
        except Exception as e:
            _log(f"voice gagal: {e}")

    _th.Thread(target=_run, daemon=True).start()

def _jalan_tugas(t, jam_task):
    """Eksekusi satu tugas 'perintah' via dispatcher kontrol_komputer."""
    tid = t.get("id", "?")
    perintah = (t.get("perintah") or "").strip()
    if not perintah:
        _log(f"Tugas {tid}: perintah kosong, dilewati")
        return
    try:
        ku = _cari_kontrol_utama()
        if ku is None:
            _toast_cron("Orion", f"Tugas {tid} gagal: kontrol_utama tidak ketemu")
            return
        nama, _, args = perintah.partition(" ")
        nama = ku._peta_alias().get(nama, nama)
        fn = ku.PERINTAH.get(nama)
        if fn is None:
            _log(f"Tugas {tid}: aksi tidak dikenal '{nama}'")
            _toast_cron("Orion", f"Tugas {tid} gagal: aksi '{nama}' tidak dikenal")
            return
        hasil = fn(args)
        ok = isinstance(hasil, dict) and hasil.get("sukses")
        ringkas = str(hasil.get("pesan") if isinstance(hasil, dict) else hasil)[:120]
        _log(f"Tugas {tid} ({jam_task}): {'OK' if ok else 'GAGAL'} - {ringkas}")
        if ok and t.get("pesan"):
            _toast_cron("Orion", t["pesan"])
            _speak_async(t["pesan"])
        if not ok:
            _toast_cron("Orion", f"Tugas {tid} gagal: {ringkas[:100]}")
    except Exception as e:
        _log(f"Tugas {tid} error: {e}")
        _toast_cron("Orion", f"Tugas {tid} error: {e}")

# tes supervisor 03:24:38

# tes supervisor 2 03:27:17

# tes supervisor 2 03:27:34

# tes supervisor 2 03:27:45

# tes supervisor 3 03:29:56

# tes supervisor 3 03:30:22

# tes supervisor 3 03:30:28
