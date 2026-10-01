"""tambah_suara_cron.py -- Sambungkan voice F1 ke tugas cron terjadwal.

Latar: toast cron bisu dari sananya (ToastText02 tanpa audio). Riki minta
pesan tugas terjadwal ikut DIBICARAKAN pakai suara F1.

Cara: script ini INTROSPEKSI proyek -> cari fungsi yang nge-print emoji
"🔊" (penanda fungsi yang beneran menghasilkan suara, jalur yang dipakai
inisiatif engine), lalu tempel pemanggilan non-blocking ke _jalan_tugas di
support/cron_orion.py. Gagal -> log saja, toast tetap jalan.

Surgical: backup, compile-check, idempoten, fail-closed.
"""
import py_compile
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
MARKER = "# SUARA_CRON_F1"


def cari_orion_hidup():
    p = BASE / "orion_hidup.py"
    return p if p.is_file() else None


def cari_cron():
    p = BASE / "support" / "cron_orion.py"
    if p.is_file():
        return p
    import os
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules")]
        if "cron_orion.py" in filenames:
            return Path(dirpath) / "cron_orion.py"
    return None


def temukan_voice_semua():
    """Kumpulkan SEMUA def yang badannya mengandung emoji '🔊'.
    Return list [(nama, path)]."""
    import os
    hasil = []
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "_arsip", "node_modules",
                                    ".venv", "venv")]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            p = Path(dirpath) / fn
            try:
                teks = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if "🔊" not in teks:
                continue
            blok = re.split(r"(?m)^(?=def \w+\()", teks)
            for b in blok:
                m = re.match(r"def (\w+)\(", b)
                if not m:
                    continue
                nama = m.group(1)
                if nama.startswith("_"):
                    continue
                if "🔊" in b:
                    hasil.append((nama, p))
    return hasil


def pilih_voice(kandidat, paksa=None):
    """Pilih fungsi voice terbaik. paksa = nama dari argumen CLI."""
    if paksa:
        for nama, p in kandidat:
            if nama == paksa:
                return nama, p
        return None
    def skor(item):
        nama, p = item
        s = 0
        if p.name == "inisiatif_otonom.py":
            s += 10  # file-nya inisiatif engine sendiri
        if re.search(r"speak|bicara|putar|ucap|say", nama, re.I):
            s += 5
        return s
    if not kandidat:
        return None
    return max(kandidat, key=skor)


FUNGSI_SUARA = '''# SUARA_CRON_F1: bicarakan pesan tugas via voice F1 (non-blocking)
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
            import __MODUL_VOICE__ as _t
            fn = getattr(_t, "__NAMA_VOICE__", None)
            if not callable(fn):
                _log("voice: __NAMA_VOICE__ tidak callable di __MODUL_VOICE__")
                return
            fn(teks)
            _log(f"voice OK via __MODUL_VOICE__.{getattr(fn, '__name__', '?')}")
        except Exception as e:
            _log(f"voice gagal: {e}")

    _th.Thread(target=_run, daemon=True).start()

'''


def main():
    hidup = cari_orion_hidup()
    if hidup is None:
        print("GAGAL: orion_hidup.py tidak ketemu di", BASE)
        return 1
    cr = cari_cron()
    if cr is None:
        print("GAGAL: cron_orion.py tidak ketemu")
        return 1
    print("orion_hidup:", hidup)
    print("cron:", cr)

    # v7: hardcode. Introspeksi v1-v6 tidak bisa diandalkan: pilih_voice memberi
    # +10 ke inisiatif_otonom.py sehingga kepilih modul yang filenya di subfolder
    # (tidak importable) -> log "No module named 'inisiatif_otonom'".
    # Bukti kuat: tts_orion.py ada di root (importable) dan badannya ada print
    # yang sama persis dengan baris "Voice:" di log jantung.
    # Override manual: python tambah_suara_cron.py <modul> <fungsi>
    if len(sys.argv) >= 3:
        modul_voice, nama = sys.argv[1], sys.argv[2]
        asal = "manual (CLI)"
    else:
        modul_voice, nama = "tts_orion", "bicara"
        asal = "hardcode (bukti: print speaker di log jantung)"
    print(f"fungsi voice: {modul_voice}.{nama}() [{asal}]")

    teks = cr.read_text(encoding="utf-8")
    if MARKER in teks:
        # Instalasi lama (mungkin salah sasaran) -> cabut, pasang ulang fresh.
        print("Instalasi lama terdeteksi, dicabut untuk dipasang ulang...")
        teks = re.sub(r"(?m)^# SUARA_CRON_F1:.*?(?=^def _jalan_tugas\(t, jam_task\):$)",
                      "", teks, count=1, flags=re.DOTALL)
        teks = teks.replace('\n            _speak_async(t["pesan"])', "")
        if MARKER in teks:
            print("GAGAL: tidak bisa mencabut instalasi lama. Batal aman.")
            return 1
        print("Instalasi lama tercabut.")

    # 1. sisipkan _speak_async sebelum _jalan_tugas
    anchor_def = re.compile(r"(?m)^def _jalan_tugas\(t, jam_task\):$")
    if not anchor_def.search(teks):
        print("GAGAL: def _jalan_tugas(t, jam_task) tidak ketemu. Batal aman.")
        return 1
    if len(anchor_def.findall(teks)) != 1:
        print("GAGAL: anchor def tidak unik. Batal aman.")
        return 1
    fungsi = FUNGSI_SUARA.replace("__NAMA_VOICE__", nama).replace("__MODUL_VOICE__", modul_voice)
    teks = anchor_def.sub(lambda m: fungsi + m.group(0), teks, count=1)

    # 2. panggil setelah toast sukses
    anchor_toast = re.compile(
        r'(?m)^        if ok and t\.get\("pesan"\):\n'
        r'            _toast_cron\("Orion", t\["pesan"\]\)$')
    if not anchor_toast.search(teks):
        print("GAGAL: baris toast sukses tidak ketemu. Batal aman.")
        return 1
    teks = anchor_toast.sub(
        lambda m: m.group(0) + '\n            _speak_async(t["pesan"])',
        teks, count=1)

    bak = cr.with_suffix(".py.bak_suara_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(cr, bak)
    print("backup:", bak.name)
    cr.write_text(teks, encoding="utf-8")
    try:
        py_compile.compile(str(cr), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(bak, cr)
        print("GAGAL compile, restore dari backup:", e)
        return 1

    print("OK: cron sekarang bersuara via", nama + "(). Compile OK.")
    print("Langkah: double-click ORION-HIDUP.bat, lalu tes jadwal lagi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
