"""kontrol_utama.py - Kontrol utama komputer Orion (JARVIS style)."""
import sys
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "core" / "otonom" / "kontrol"))

from app_control import buka_app, tutup_app, list_app_aktif
from keyboard_mouse import ketik, tekan, hotkey, klik, scroll, posisi_mouse, ukuran_layar
from file_control import baca_file, tulis_file, list_folder, buat_folder, rename_file, copy_file
from system_control import info_sistem, shutdown, restart, lock, cek_network, batalkan_shutdown
from safety_kontrol import butuh_konfirmasi, catat_aksi, cek_blokir  # amankan_kontrol 30/09


# === Daftar perintah ===
def _cmd_buka(x):
    return buka_app(x)

def _cmd_tutup(x):
    return tutup_app(x)

def _cmd_ketik(x):
    return ketik(x)

def _cmd_tekan(x):
    return tekan(x)

def _cmd_hotkey(x):
    return hotkey(*x.split("+"))

def _cmd_klik(x):
    return klik()

def _cmd_scroll(x):
    return scroll(int(x) if x else 3)

def _cmd_baca(x):
    return baca_file(x)

def _cmd_tulis(x):
    parts = x.split("|", 1)
    if len(parts) < 2:
        return {"sukses": False, "pesan": "Format: tulis <path>|<isi>"}
    return tulis_file(parts[0].strip(), parts[1])

def _cmd_list_folder(x):
    return list_folder(x)

def _cmd_buat_folder(x):
    return buat_folder(x)

def _cmd_aktifkan_jendela(x):
    return aktifkan_jendela(x)

def _cmd_cari_file(x):
    return cari_file(x)

def _cmd_jadwal_tugas(x):
    return jadwal_tugas(x)

def _cmd_daftar_aksi(x):
    return daftar_aksi(x)

def _cmd_rename_file(x):
    parts = x.split("|", 1)
    if len(parts) < 2:
        return {"sukses": False, "pesan": "Format: rename_file <sumber>|<tujuan>"}
    return rename_file(parts[0].strip(), parts[1].strip())

def _cmd_copy_file(x):
    parts = x.split("|", 1)
    if len(parts) < 2:
        return {"sukses": False, "pesan": "Format: copy_file <sumber>|<tujuan>"}
    return copy_file(parts[0].strip(), parts[1].strip())

def _cmd_info(x):
    return info_sistem()

def _cmd_shutdown(x):
    return shutdown(int(x) if x else 60)

def _cmd_restart(x):
    return restart(int(x) if x else 60)

def _cmd_lock(x):
    return lock()

def _cmd_network(x):
    return cek_network()

def _cmd_batal_shutdown(x):
    return batalkan_shutdown()


PERINTAH = {
    # Aplikasi
    "buka": _cmd_buka,
    "tutup": _cmd_tutup,
    "list_app": lambda x: list_app_aktif(),
    
    # Keyboard
    "ketik": _cmd_ketik,
    "tekan": _cmd_tekan,
    "hotkey": _cmd_hotkey,
    
    # Mouse
    "klik": _cmd_klik,
    "scroll": _cmd_scroll,
    "posisi_mouse": lambda x: posisi_mouse(),
    "ukuran_layar": lambda x: ukuran_layar(),
    
    # File
    "baca": _cmd_baca,
    "tulis": _cmd_tulis,
    "list_folder": _cmd_list_folder,
    "buat_folder": _cmd_buat_folder,
    "aktifkan_jendela": _cmd_aktifkan_jendela,
    "cari_file": _cmd_cari_file,
    "jadwal_tugas": _cmd_jadwal_tugas,
    "daftar_aksi": _cmd_daftar_aksi,
    "rename_file": _cmd_rename_file,
    "copy_file": _cmd_copy_file,
    
    # Sistem
    "info_sistem": _cmd_info,
    "shutdown": _cmd_shutdown,
    "restart": _cmd_restart,
    "lock": _cmd_lock,
    "network": _cmd_network,
    "batal_shutdown": _cmd_batal_shutdown,
}


def jalankan_perintah(perintah: str, konfirmasi_otomatis: bool = False) -> dict:
    """
    Jalankan perintah kontrol.
    
    Format: "aksi target"
    Contoh: "buka notepad", "ketik halo", "info sistem", "info_sistem"
    """
    perintah = perintah.strip().lower()
    if not perintah:
        return {"sukses": False, "pesan": "Perintah kosong"}
    
    # === Normalisasi perintah ===
    # Ganti spasi jadi underscore untuk cek aksi
    perintah_norm = perintah.replace(" ", "_")
    
    # Daftar aksi multi-kata
    AKSI_MULTI = [
        "info_sistem", "ukuran_layar", "posisi_mouse",
        "list_app", "list_folder", "buat_folder",
        "batal_shutdown", "cek_sistem",

        "rename_file",

        "copy_file",

        "aktifkan_jendela",

        "cari_file",

        "jadwal_tugas",

        "daftar_aksi",
    ]
    
    aksi = None
    target = ""
    
    # Cek aksi multi-kata dulu
    for a in AKSI_MULTI:
        if perintah_norm == a or perintah_norm.startswith(a + "_"):
            aksi = a
            # Target = sisa
            if perintah_norm.startswith(a + "_"):
                target = perintah[len(a.replace("_", " ")) + 1:].strip()
            break
    
    # Kalau tidak ketemu, split biasa
    if aksi is None:
        parts = perintah.split(" ", 1)
        aksi = parts[0]
        target = parts[1] if len(parts) > 1 else ""
    
    # Alias — biar friendly
    ALIAS = {
        "info": "info_sistem",
        "sistem": "info_sistem",
        "jaringan": "network",
        "koneksi": "network",
        "layar": "ukuran_layar",
        "mouse": "posisi_mouse",
        "app": "list_app",
        "folder": "list_folder",

        "rename": "rename_file",

        "copy": "copy_file",

        "aktifkan": "aktifkan_jendela",
        "cari": "cari_file",
        "jadwal": "jadwal_tugas",
        "daftar": "daftar_aksi",
    }
    
    if aksi in ALIAS:
        aksi = ALIAS[aksi]
    
    if aksi not in PERINTAH:
        return {"sukses": False, "pesan": f"Aksi tidak dikenal: {aksi}"}

    # Blokir aksi terlarang sebelum cek konfirmasi (amankan_kontrol 30/09)
    _blokir, _alasan_blokir = cek_blokir(aksi, target)
    if _blokir:
        catat_aksi(aksi, target, False, False)
        return {"sukses": False, "pesan": f"Ditolak: {_alasan_blokir}"}
    
    # Cek safety
    butuh, alasan = butuh_konfirmasi(aksi, target)
    if butuh and not konfirmasi_otomatis:
        print(f"[Safety] {alasan}")
        try:
            konfirmasi = input("Lanjut? (y/n): ").strip().lower()
        except EOFError:
            konfirmasi = "n"
        if konfirmasi != "y":
            return {"sukses": False, "pesan": "Dibatalkan oleh user"}
    
    # Jalankan
    try:
        hasil = PERINTAH[aksi](target)
        catat_aksi(aksi, target, hasil.get("sukses", False), butuh)
        return hasil
    except Exception as e:
        catat_aksi(aksi, target, False, butuh)
        return {"sukses": False, "pesan": f"Error: {e}"}


def ringkasan_perintah() -> str:
    """Ringkasan perintah untuk prompt LLM."""
    return """PERINTAH KONTROL KOMPUTER:
- buka <app>          : Buka aplikasi (chrome, notepad, vscode, dll)
- tutup <app>         : Tutup aplikasi
- list_app            : List aplikasi aktif
- ketik <teks>        : Ketik teks
- tekan <tombol>      : Tekan tombol (enter, tab, esc)
- hotkey <kombinasi>  : Hotkey (ctrl+c, alt+tab)
- klik                : Klik mouse
- scroll <jumlah>     : Scroll mouse
- posisi_mouse        : Posisi mouse
- ukuran_layar        : Ukuran layar
- baca <path>         : Baca file
- tulis <path>|<isi>  : Tulis file
- list_folder <path>  : List folder
- buat_folder <path>  : Buat folder
- aktifkan_jendela <judul> : Fokuskan jendela (cocok parsial)
- cari_file <pola> : Cari file rekursif (nama parsial)
- jadwal_tugas <sub> : Atur tugas terjadwal (list/tambah/hapus/on/off)
- daftar_aksi [kata] : Lihat semua aksi yang tersedia (introspeksi diri)
- rename_file <sumber>|<tujuan> : Rename/pindah file
- copy_file <sumber>|<tujuan>   : Copy file
- info_sistem         : Info CPU, RAM, Disk
- network             : Cek koneksi
- shutdown [detik]    : Shutdown PC
- restart [detik]     : Restart PC
- lock                : Lock PC
- batal_shutdown      : Batalkan shutdown
"""


if __name__ == "__main__":
    print("=" * 60)
    print("  ORION KONTROL KOMPUTER")
    print("=" * 60)
    print()
    print(ringkasan_perintah())
    print()
    
    while True:
        try:
            cmd = input("Kontrol> ").strip()
            
            if not cmd:
                continue
            
            if cmd in ["quit", "exit", "keluar"]:
                break
            
            hasil = jalankan_perintah(cmd)
            print(f"  → {hasil}")
            print()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n[Kontrol] Selesai")


def aktifkan_jendela(judul: str) -> dict:
    """Fokuskan jendela Windows berdasarkan judul (parsial, case-insensitive)."""
    import subprocess
    judul = (judul or "").strip()
    if not judul:
        return {"sukses": False, "pesan": "Format: aktifkan_jendela <judul jendela>"}
    esc = judul.replace("'", "''")
    ps = "$j = '" + esc + "'; "
    ps += '$p = Get-Process | Where-Object { $_.MainWindowTitle -like "*$j*" } | Select-Object -First 1; '
    ps += 'if ($p) { $ok = (New-Object -ComObject WScript.Shell).AppActivate($p.Id); '
    ps += 'if ($ok) { "OK:" + $p.MainWindowTitle } else { "GAGAL_AKTIF:" + $p.MainWindowTitle } } '
    ps += 'else { "TIDAK_KETEMU:" + $j }'
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, text=True, timeout=15)
        out = (r.stdout or "").strip()
        if out.startswith("OK:"):
            return {"sukses": True, "pesan": "Jendela diaktifkan: " + out[3:]}
        if out.startswith("TIDAK_KETEMU:"):
            return {"sukses": False, "pesan": "Tidak ada jendela berjudul '" + judul + "'"}
        if out.startswith("GAGAL_AKTIF:"):
            return {"sukses": False,
                    "pesan": "Jendela ketemu tapi gagal difokuskan: " + out[11:]}
        err = (r.stderr or "").strip()
        return {"sukses": False, "pesan": "Gagal: " + (err or out or "tidak ada output")}
    except Exception as e:
        return {"sukses": False, "pesan": "Gagal: " + str(e)}


def cari_file(pola: str) -> dict:
    """Cari file rekursif dari root ORION (nama parsial, case-insensitive)."""
    import fnmatch
    import os
    from pathlib import Path
    arg = (pola or "").strip()
    if "|" in arg:
        nama_pola, folder = [s.strip() for s in arg.split("|", 1)]
    else:
        nama_pola, folder = arg, ""
    if not nama_pola:
        return {"sukses": False,
                "pesan": "Format: cari_file <pola> atau cari_file <pola>|<folder>"}
    root = Path(__file__).resolve().parents[3]
    if folder:
        base = Path(folder) if Path(folder).is_absolute() else root / folder
    else:
        base = root
    if not base.is_dir():
        return {"sukses": False, "pesan": "Folder tidak ada: " + folder}
    kunci = nama_pola.lower()
    pakai_wildcard = ("*" in kunci) or ("?" in kunci)
    hasil = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in filenames:
            if pakai_wildcard:
                cocok = fnmatch.fnmatch(fn.lower(), kunci)
            else:
                cocok = kunci in fn.lower()
            if cocok:
                p = Path(dirpath, fn)
                try:
                    hasil.append(str(p.relative_to(root)))
                except ValueError:
                    hasil.append(str(p))
                if len(hasil) >= 50:
                    break
        if len(hasil) >= 50:
            break
    if not hasil:
        return {"sukses": False,
                "pesan": "Tidak ketemu file cocok '" + nama_pola + "'"}
    catatan = "" if len(hasil) < 50 else "\n...(dibatasi 50 hasil)"
    return {"sukses": True,
            "pesan": "Ketemu %d file:\n%s%s" % (len(hasil), "\n".join(hasil), catatan)}


def _lokasi_tasks():
    """Lokasi cron_tasks.json: di folder yang sama dengan cron_orion.py."""
    from pathlib import Path
    import os
    root = Path(__file__).resolve().parents[3]
    cand = root / "cron_orion.py"
    if cand.is_file():
        return cand.parent / "cron_tasks.json"
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules")]
        if "cron_orion.py" in filenames:
            return Path(dirpath) / "cron_tasks.json"
    return root / "cron_tasks.json"


def _baca_tugas():
    import json
    p = _lokasi_tasks()
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("tasks", [])
    except Exception:
        return []


def _simpan_tugas(tugas):
    import json
    p = _lokasi_tasks()
    p.write_text(json.dumps({"tasks": tugas}, indent=2, ensure_ascii=False),
                 encoding="utf-8")


def jadwal_tugas(arg: str) -> dict:
    """Atur tugas terjadwal ORION (dieksekusi cron_orion tiap menit)."""
    import re
    a = (arg or "").strip()
    if not a or a == "list":
        tugas = _baca_tugas()
        if not tugas:
            return {"sukses": True, "pesan": "Belum ada tugas terjadwal."}
        baris = []
        for t in tugas:
            st = "ON" if t.get("aktif", True) else "OFF"
            apa = t.get("perintah") or t.get("pesan") or t.get("aksi", "?")
            baris.append("[%s] %s | %s | %s" % (st, t.get("id", "?"), t.get("jam", "?"), apa))
        return {"sukses": True,
                "pesan": "Tugas terjadwal:\n" + "\n".join(baris)}
    if a.startswith("tambah"):
        isi = a[len("tambah"):].strip()
        if "||" in isi:
            # format || : <jam>||<perintah>||<pesan> (perintah boleh mengandung |)
            fparts = [p.strip() for p in isi.split("||")]
            jam = fparts[0] if len(fparts) > 0 else ""
            perintah = fparts[1] if len(fparts) > 1 else ""
            pesan = fparts[2] if len(fparts) > 2 else ""
        else:
            parts = [p.strip() for p in isi.split("|")]
            jam = parts[0] if len(parts) > 0 else ""
            perintah = parts[1] if len(parts) > 1 else ""
            pesan = parts[2] if len(parts) > 2 else ""
        if not jam or not perintah:
            return {"sukses": False, "pesan":
                    "Format: jadwal_tugas tambah <jam HH:MM>||<perintah>||<pesan opsional>"}
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", jam):
            return {"sukses": False,
                    "pesan": "Jam harus format HH:MM (00:00-23:59)."}
        nama = perintah.split(" ", 1)[0]
        nama_asli = _peta_alias().get(nama, nama)
        if nama_asli not in PERINTAH:
            return {"sukses": False,
                    "pesan": "Aksi '%s' tidak dikenal. Cek daftar aksi dulu." % nama}
        tugas = _baca_tugas()
        ids = {t.get("id") for t in tugas}
        tid = "tugas_%s_%s" % (jam.replace(":", ""), nama_asli)
        n = 2
        while tid in ids:
            tid = "tugas_%s_%s_%d" % (jam.replace(":", ""), nama_asli, n)
            n += 1
        tugas.append({"id": tid, "jam": jam, "aksi": "perintah",
                      "perintah": perintah, "pesan": pesan, "aktif": True})
        _simpan_tugas(tugas)
        return {"sukses": True,
                "pesan": "Tugas '%s' dijadwalkan tiap %s: %s" % (tid, jam, perintah)}
    if a.startswith("hapus"):
        tid = a[len("hapus"):].strip()
        if not tid:
            return {"sukses": False, "pesan": "Format: jadwal_tugas hapus <id>"}
        tugas = _baca_tugas()
        baru = [t for t in tugas if t.get("id") != tid]
        if len(baru) == len(tugas):
            return {"sukses": False, "pesan": "Tugas '%s' tidak ketemu." % tid}
        _simpan_tugas(baru)
        return {"sukses": True, "pesan": "Tugas '%s' dihapus." % tid}
    if a.startswith("on ") or a == "on" or a.startswith("off ") or a == "off":
        nyala = a == "on" or a.startswith("on ")
        tid = (a[2:].strip() if nyala else a[3:].strip())
        if not tid:
            return {"sukses": False, "pesan": "Format: jadwal_tugas on|off <id>"}
        tugas = _baca_tugas()
        ketemu = False
        for t in tugas:
            if t.get("id") == tid:
                t["aktif"] = bool(nyala)
                ketemu = True
        if not ketemu:
            return {"sukses": False, "pesan": "Tugas '%s' tidak ketemu." % tid}
        _simpan_tugas(tugas)
        return {"sukses": True,
                "pesan": "Tugas '%s' %s." % (tid, "diaktifkan" if nyala else "dinonaktifkan")}
    return {"sukses": False, "pesan":
            "Format: jadwal_tugas list | tambah <jam>||<perintah>||<pesan> | hapus <id> | on|off <id>"}


def daftar_aksi(arg: str) -> dict:
    """Tampilkan semua aksi yang ORION bisa pakai (baca registry sendiri)."""
    import re
    from pathlib import Path
    a = (arg or "").strip().lower()
    # kumpulkan deskripsi dari blok ringkasan di file ini sendiri
    desk = {}
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        for m in re.finditer(r"(?m)^- (\S+)\s+.*?:\s*(.+)$", src):
            desk[m.group(1)] = m.group(2).strip()
    except Exception:
        pass
    # alias balik: aksi -> [alias...] (ALIAS dibaca dari source, bukan global)
    balik = {}
    for k, v in _peta_alias().items():
        balik.setdefault(v, []).append(k)
    multi = _daftar_multi()
    baris = []
    for nama in sorted(PERINTAH):
        d = desk.get(nama, "")
        if a and a not in nama and a not in d.lower():
            continue
        al = balik.get(nama, [])
        s = "- %s" % nama
        if nama in multi:
            s += " [multi]"
        if al:
            s += " (alias: %s)" % ", ".join(al)
        if d:
            s += " : %s" % d
        baris.append(s)
    if not baris:
        return {"sukses": False,
                "pesan": "Tidak ada aksi yang cocok dengan '%s'." % a}
    return {"sukses": True,
            "pesan": "Aksi yang aku bisa pakai (%d):\n%s" % (len(baris), "\n".join(baris))}


def _peta_alias() -> dict:
    """Baca dict ALIAS dari source file ini.

    ALIAS didefinisikan lokal di dalam jalankan_perintah(), bukan global
    modul, sehingga fungsi lain tidak bisa mengaksesnya langsung.
    Parse defensif: gagal -> {}.
    """
    import re
    from pathlib import Path
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        m = re.search(r'(?m)^([ \t]*)ALIAS = \{$', src)
        if not m:
            return {}
        indent = m.group(1)
        rest = src[m.end():]
        m2 = re.search(r'(?m)^' + re.escape(indent) + r'\}', rest)
        block = rest[: m2.start()] if m2 else rest
        return dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', block))
    except Exception:
        return {}


def _daftar_multi() -> list:
    """Baca list AKSI_MULTI (lokal di jalankan_perintah) dari source file."""
    import re
    from pathlib import Path
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        m = re.search(r'(?m)^([ \t]*)AKSI_MULTI = \[$', src)
        if not m:
            return []
        indent = m.group(1)
        rest = src[m.end():]
        m2 = re.search(r'(?m)^' + re.escape(indent) + r'\]', rest)
        block = rest[: m2.start()] if m2 else rest
        return re.findall(r'"([^"]+)"', block)
    except Exception:
        return []
