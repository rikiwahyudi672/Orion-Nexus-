#!/usr/bin/env python3
"""tambah_jadwal_tugas.py -- Tambah jadwal_tugas: tugas ber-perintah di cron.

Latar: cron_orion + inisiatif.json cuma bisa NGOMONG (pesan terjadwal),
belum bisa NGERJAIN (eksekusi aksi). ORION minta bisa punya agenda sendiri.

Desain (numpang, bukan mesin baru):
- cron_tasks.json dapat entri {"aksi": "perintah", "perintah": "...", ...}.
- cron_orion._loop() dapat cabang `aksi == "perintah"` -> dispatch ke
  dispatcher kontrol_komputer (PERINTAH/ALIAS), hasil dicatat di logs/cron.log,
  gagal -> toast Windows. Hormati flag "aktif".
- kontrol_komputer dapat aksi jadwal_tugas: list | tambah | hapus | on | off,
  dengan validasi jam (HH:MM) dan validasi nama aksi saat didaftarkan.

Format chat:
  jadwal_tugas list
  jadwal_tugas tambah <jam HH:MM>|<perintah>|<pesan opsional>
  jadwal_tugas hapus <id>
  jadwal_tugas on|off <id>

Contoh tugas pertama yang berguna:
  jadwal_tugas tambah 03:00|copy_file memory/orion.db|memory/orion_backup.db|Backup database selesai

Safety: perintah divalidasi saat daftar (aksi harus dikenal); aksi yang butuh
konfirmasi akan gagal halus di mode headless (diskip + dilapor via toast).

Idempoten, backup per file, compile-check, auto-restore bila gagal.
"""
import os
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(os.environ.get("ORION_BASE", "E:/Project Software/Orion"))
KONTROL = BASE / "core" / "otonom" / "kontrol"

PATCHES = []  # (path, anchor_regex, sisipan, cek_idempoten)


def tambah_patch(path, anchor, sisipan, cek):
    PATCHES.append((Path(path), anchor, sisipan, cek))


def _cari_target(nama_file):
    if (BASE / nama_file).is_file():
        return BASE / nama_file
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules")]
        if nama_file in filenames:
            return Path(dirpath) / nama_file
    return None


# ---------------------------------------------------------------- kontrol_utama.py
KU = KONTROL / "kontrol_utama.py"

# 1a. wrapper _cmd_ setelah _cmd_cari_file (HARUS sebelum dict PERINTAH).
tambah_patch(
    KU,
    r"^def _cmd_cari_file\(x\):\n    return cari_file\(x\)$",
    '''def _cmd_cari_file(x):
    return cari_file(x)

def _cmd_jadwal_tugas(x):
    return jadwal_tugas(x)''',
    "def _cmd_jadwal_tugas(",
)

# 1b. implementasi, append di akhir file (idempoten via cek string).
KU_FUNCS = '''

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
                "pesan": "Tugas terjadwal:\\n" + "\\n".join(baris)}
    if a.startswith("tambah"):
        isi = a[len("tambah"):].strip()
        parts = [p.strip() for p in isi.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            return {"sukses": False, "pesan":
                    "Format: jadwal_tugas tambah <jam HH:MM>|<perintah>|<pesan opsional>"}
        jam, perintah = parts[0], parts[1]
        pesan = parts[2] if len(parts) > 2 else ""
        if not re.match(r"^([01]\\d|2[0-3]):[0-5]\\d$", jam):
            return {"sukses": False,
                    "pesan": "Jam harus format HH:MM (00:00-23:59)."}
        nama = perintah.split(" ", 1)[0]
        nama_asli = ALIAS.get(nama, nama)
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
            "Format: jadwal_tugas list | tambah <jam>|<perintah> | hapus <id> | on|off <id>"}
'''

tambah_patch(KU, r"\Z", KU_FUNCS, "def jadwal_tugas(")

# 2. daftarkan di PERINTAH
tambah_patch(
    KU,
    r'^    "cari_file": _cmd_cari_file,$',
    '''    "cari_file": _cmd_cari_file,
    "jadwal_tugas": _cmd_jadwal_tugas,''',
    '"jadwal_tugas": _cmd_jadwal_tugas,',
)

# 3. ringkasan_perintah untuk prompt LLM
tambah_patch(
    KU,
    r"^- cari_file <pola> : Cari file rekursif \(nama parsial\)$",
    """- cari_file <pola> : Cari file rekursif (nama parsial)
- jadwal_tugas <sub> : Atur tugas terjadwal (list/tambah/hapus/on/off)""",
    "- jadwal_tugas <sub>",
)

# 4. alias pendek: jadwal -> jadwal_tugas (ditangani khusus)
tambah_patch(KU, None, None, '"jadwal": "jadwal_tugas",')

# 5. AKSI_MULTI (ditangani khusus)
tambah_patch(KU, None, None, '"jadwal_tugas",')


# ---------------------------------------------------------------- cron_orion.py
CR = _cari_target("cron_orion.py")
if CR is None:
    print("GAGAL: cron_orion.py tidak ketemu di", BASE)
    sys.exit(1)
print("target cron:", CR)

# 6. cabang aksi == "perintah" di _loop (sebelum cabang maintenance)
tambah_patch(
    CR,
    r'^                    if aksi == "maintenance":$',
    '''                    if aksi == "perintah":
                        _jalan_tugas(t, jam_task)
                    elif aksi == "maintenance":''',
    '_jalan_tugas(t, jam_task)',
)

# 7. hormati flag "aktif" di blok skip
tambah_patch(
    CR,
    r'^                if aksi == "tts" and not pesan:\n                    continue$',
    '''                if aksi == "tts" and not pesan:
                    continue
                if t.get("aktif") is False:
                    continue''',
    't.get("aktif") is False',
)

# 8. helper dispatch + toast, append di akhir file
CR_FUNCS = '''

_KU_CACHE = None

def _cari_kontrol_utama():
    """Import kontrol_utama.py (dicache). Return modul atau None."""
    global _KU_CACHE
    if _KU_CACHE is not None:
        return _KU_CACHE
    import importlib.util
    import os
    import sys
    from pathlib import Path
    kandidat = [BASE / "core" / "otonom" / "kontrol" / "kontrol_utama.py"]
    target = None
    for k in kandidat:
        if k.is_file():
            target = k
            break
    if target is None:
        for dirpath, dirnames, filenames in os.walk(BASE):
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
        bersih = pesan.replace('"', "'").replace("\\n", " ").strip()[:150]
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
        nama = ku.ALIAS.get(nama, nama)
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
        if not ok:
            _toast_cron("Orion", f"Tugas {tid} gagal: {ringkas[:100]}")
    except Exception as e:
        _log(f"Tugas {tid} error: {e}")
        _toast_cron("Orion", f"Tugas {tid} error: {e}")
'''

tambah_patch(CR, r"\Z", CR_FUNCS, "def _jalan_tugas(")


# ---------------------------------------------------------------- orion_tool_loop.py
TL = BASE / "orion_tool_loop.py"
tambah_patch(
    TL,
    r"cari file rekursif",
    "cari file rekursif, jadwal tugas",
    "jadwal tugas",
)


# ================================================================ engine
def _baca(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _tulis(p: Path, teks: str):
    p.write_text(teks, encoding="utf-8")


def _compile_ok(p: Path) -> bool:
    try:
        py_compile.compile(str(p), doraise=True)
        return True
    except Exception as e:
        print(f"COMPILE GAGAL {p.name}: {e}")
        return False


def _terapkan(p: Path, anchor: str, sisipan: str, cek: str) -> str:
    teks = _baca(p)
    if cek in teks:
        return "sudah"
    if anchor == r"\Z":
        _tulis(p, teks + sisipan)
        return "ok(append)"
    m = re.search(anchor, teks, re.MULTILINE)
    if not m:
        return "GAGAL: anchor tidak ketemu"
    if len(re.findall(anchor, teks, re.MULTILINE)) != 1:
        return "GAGAL: anchor tidak unik"
    baru = teks[: m.start()] + sisipan + teks[m.end():]
    _tulis(p, baru)
    return "ok"


def _patch_alias(p: Path, entries: dict) -> str:
    """Sisip entries ke dict ALIAS sebelum kurung tutupnya (tahan indent)."""
    teks = _baca(p)
    if all('"%s": "%s"' % (k, v) in teks for k, v in entries.items()):
        return "sudah"
    m = re.search(r"(?m)^([ \t]*)ALIAS = \{$", teks)
    if not m:
        return "GAGAL: ALIAS tidak ketemu"
    base_indent = m.group(1)
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^" + re.escape(base_indent) + r"\}", rest)
    if not m2:
        return "GAGAL: tutup ALIAS tidak ketemu"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^([ \t]+)"', rest[: m2.start()])
    indent = m3.group(1) if m3 else base_indent + "    "
    sisip = "".join('%s"%s": "%s",\n' % (indent, k, v) for k, v in entries.items())
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def _patch_list_tambah(p: Path, nama_list: str, entries: list) -> str:
    """Tambah entries ke list (mis. AKSI_MULTI) sebelum ']' penutup."""
    teks = _baca(p)
    m = re.search(r"(?m)^\s*" + re.escape(nama_list) + r"\s*=\s*\[$", teks)
    if not m:
        return f"GAGAL: {nama_list} tidak ketemu"
    rest = teks[m.end():]
    m2 = re.search(r"(?m)^\s*\]", rest)
    if not m2:
        return f"GAGAL: tutup {nama_list} tidak ketemu"
    block = rest[: m2.start()]
    if all('"%s"' % e in block or "'%s'" % e in block for e in entries):
        return "sudah"
    pos = m.end() + m2.start()
    m3 = re.search(r'(?m)^(\s+)"', rest[: m2.start()])
    indent = m3.group(1) if m3 else "    "
    sisip = "".join('%s"%s",\n' % (indent, e) for e in entries)
    _tulis(p, teks[:pos] + sisip + teks[pos:])
    return "ok"


def main():
    print("=== tambah_jadwal_tugas.py ===")
    targets = {str(p) for p, _, _, _ in PATCHES}
    backups = {}
    for t in targets:
        p = Path(t)
        bak = p.with_name(p.name + ".bak_jadwal_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        shutil.copy2(p, bak)
        backups[t] = bak
        print(f"backup: {bak.name}")

    hasil = []
    for p, anchor, sisipan, cek in PATCHES:
        if anchor is None or sisipan is None:
            continue  # ditangani khusus
        r = _terapkan(p, anchor, sisipan, cek)
        hasil.append((p.name, r))
        print(f"[{p.name}] {r}")

    # patch khusus
    r = _patch_alias(KU, {"jadwal": "jadwal_tugas"})
    hasil.append((KU.name + ":ALIAS", r))
    print(f"[{KU.name}:ALIAS] {r}")

    r = _patch_list_tambah(KU, "AKSI_MULTI", ["jadwal_tugas"])
    hasil.append((KU.name + ":AKSI_MULTI", r))
    print(f"[{KU.name}:AKSI_MULTI] {r}")

    gagal = [h for h in hasil if h[1].startswith("GAGAL")]
    if gagal:
        print("ADA YANG GAGAL, restore backup...")
        for t, bak in backups.items():
            shutil.copy2(bak, t)
        print("restore selesai.")
        sys.exit(1)

    for t in targets:
        if not _compile_ok(Path(t)):
            print("COMPILE GAGAL, restore backup...")
            for tt, bak in backups.items():
                shutil.copy2(bak, tt)
            sys.exit(1)

    print(f"[OK] {len(hasil)} patch diproses, semua compile OK.")


if __name__ == "__main__":
    main()
