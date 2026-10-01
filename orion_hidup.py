#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orion_hidup.py -- JANTUNG Orion.

Menyalakan mesin inisiatif + cron di background, dan memastikan
pesan inisiatif NYAMPE ke Riki via notifikasi Windows (toast),
bukan cuma ke dashboard yang mungkin mati.

Jalankan:  py -3 orion_hidup.py        (console terlihat, buat tes)
           orion_hidup.bat             (minimized)
           + daftar_autostart.bat      (nyala otomatis tiap login Windows)

Log: data/orion_hidup.log
Berhenti: Ctrl+C
"""

import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
for _sub in ["core", "memory", "skill", "voice", "coding",
             "emotion", "support", "dashboard", "config"]:
    _p = BASE / _sub
    if _p.exists():
        sys.path.insert(0, str(_p))

LOG_FILE = BASE / "data" / "orion_hidup.log"


def log(pesan):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {pesan}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def toast_windows(judul, pesan):
    """Notifikasi toast Windows via PowerShell. Tanpa pip, tanpa dependensi."""
    try:
        bersih = pesan.replace('"', "'").replace("\n", " ").strip()[:150]
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, "
            "Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::"
            "GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            f'$t.GetElementsByTagName("text")[0].AppendChild('
            f'$t.CreateTextNode("{judul}")) > $null; '
            f'$t.GetElementsByTagName("text")[1].AppendChild('
            f'$t.CreateTextNode("{bersih}")) > $null; '
            '[Windows.UI.Notifications.ToastNotificationManager]::'
            'CreateToastNotifier("Orion").Show($t)'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            timeout=20, capture_output=True,
        )
        return True
    except Exception as e:
        log(f"toast gagal: {e}")
        return False


def main():
    log("=" * 55)
    log("  ORION HIDUP -- jantung dinyalakan")
    log("=" * 55)

    # --- Mesin 1: inisiatif_engine (Orion bicara sendiri) ---
    try:
        import inisiatif_engine as ie

        _kirim_asli = ie.kirim_ke_web

        def kirim_plus_toast(pesan):
            """Kirim ke dashboard (asli) + toast Windows (tambahan)."""
            try:
                ok = _kirim_asli(pesan)
            except Exception:
                ok = False
            toast_windows("Orion", pesan)
            log(f"inisiatif terkirim: {pesan[:60]}")
            return ok

        ie.kirim_ke_web = kirim_plus_toast

        t1 = threading.Thread(target=ie.jalankan, kwargs={"interval": 30},
                              daemon=True, name="inisiatif")
        t1.start()
        log("OK: inisiatif_engine jalan (cek tiap 30 detik)")
    except Exception:
        log("GAGAL: inisiatif_engine\n" + traceback.format_exc())

    # --- Mesin 2: cron_orion (jadwal HH:MM) ---
    try:
        import cron_orion as cr
        if cr.mulai():
            log("OK: cron_orion jalan")
        else:
            log("cron_orion sudah jalan sebelumnya")
    except Exception:
        log("GAGAL: cron_orion\n" + traceback.format_exc())

    toast_windows("Orion", "Aku udah bangun dan siap nemenin kamu hari ini!")
    log("Jantung berdetak. Ctrl+C untuk berhenti.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log("Orion berhenti (Ctrl+C). Sampai jumpa!")


if __name__ == "__main__":
    main()
