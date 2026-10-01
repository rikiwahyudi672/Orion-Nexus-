import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
notif_orion.py - Modul notifikasi ORION ke Riki.
"""
from pathlib import Path
from datetime import datetime

LOG = Path(__file__).parent / "logs" / "notif_orion.log"


def notif_discord(pesan: str, webhook_url: str = None):
    """Kirim notif ke Discord via webhook."""
    if not webhook_url:
        webhook_url = os.getenv("DISCORD_WEBHOOK", "")
    
    if not webhook_url:
        return {"sukses": False, "error": "Webhook tidak ada"}
    
    try:
        import requests
        r = requests.post(webhook_url, json={"content": pesan}, timeout=10)
        return {"sukses": r.status_code == 204}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def kirim_notif(judul: str, pesan: str, penting: int = 0):
    """Kirim notifikasi ke Riki. Fallback bertingkat."""
    LOG.parent.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] [{judul}] {pesan}\n")

    # Coba plyer (Windows toast)
    try:
        from plyer import notification
        notification.notify(
            title=f"ORION: {judul}",
            message=pesan[:250],
            timeout=10,
        )
    except Exception:
        pass

    # Coba TTS kalau penting
    if penting:
        try:
            import tts_orion
            tts_orion.bicara(f"Bos, {judul}. {pesan}")
        except Exception:
            pass

    print(f"[NOTIF] {judul}: {pesan}")


def lapor_ke_riki(masalah: str, sudah_dicoba: str = "", saran: str = ""):
    """Format laporan terstruktur ke Riki."""
    pesan = f"Masalah: {masalah}"
    if sudah_dicoba:
        pesan += f" | Sudah dicoba: {sudah_dicoba}"
    if saran:
        pesan += f" | Saran: {saran}"
    kirim_notif("Butuh Keputusan", pesan, penting=1)


# ============================================================
# NOTIF KOMBINASI: Pop-up + Suara + Animasi
# ============================================================

_SPINNER_AKTIF = False
_SPINNER_THREAD = None


def notif_mikir(pesan: str = "Memproses..."):
    """
    Tampilkan animasi spinner di terminal.
    Return: objek spinner (untuk stop).
    """
    import sys
    import time
    import threading

    global _SPINNER_AKTIF, _SPINNER_THREAD

    _SPINNER_AKTIF = True
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _spin():
        i = 0
        while _SPINNER_AKTIF:
            sys.stdout.write(f"\r{chars[i % len(chars)]} {pesan}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        # Clear line
        sys.stdout.write("\r" + " " * (len(pesan) + 5) + "\r")
        sys.stdout.flush()

    _SPINNER_THREAD = threading.Thread(target=_spin, daemon=True)
    _SPINNER_THREAD.start()


def notif_mikir_stop():
    """Stop animasi spinner."""
    global _SPINNER_AKTIF
    _SPINNER_AKTIF = False
    import time
    time.sleep(0.15)  # kasih waktu thread berhenti


def notif_sukses(pesan: str, suara: bool = True):
    """
    Notifikasi sukses: pop-up + suara (nada sukses) + terminal.
    """
    notif_mikir_stop()
    print(f"✅ {pesan}")
    kirim_notif("Sukses", pesan, penting=0)
    if suara:
        try:
            import voice_orion
            voice_orion.tts_bicara(f"Beres, Bos. {pesan}")
        except Exception:
            pass


def notif_error(pesan: str, suara: bool = True):
    """
    Notifikasi error: pop-up + suara (nada error) + terminal.
    """
    notif_mikir_stop()
    print(f"❌ {pesan}")
    kirim_notif("Error", pesan, penting=0)
    if suara:
        try:
            import voice_orion
            voice_orion.tts_bicara(f"Waduh, ada masalah, Bos. {pesan}")
        except Exception:
            pass


def notif_info(pesan: str, suara: bool = False):
    """
    Notifikasi info: pop-up + terminal (tanpa suara).
    """
    notif_mikir_stop()
    print(f"ℹ️ {pesan}")
    kirim_notif("Info", pesan, penting=0)
    if suara:
        try:
            import voice_orion
            voice_orion.tts_bicara(pesan)
        except Exception:
            pass


if __name__ == "__main__":
    kirim_notif("Test", "Notifikasi percobaan dari terminal.", penting=0)
    lapor_ke_riki("Test masalah", "Test dicoba", "Test saran")
    print("OK.")
