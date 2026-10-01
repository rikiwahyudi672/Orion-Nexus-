"""inisiatif_otonom.py - Loop utama inisiatif Orion (Level 4)."""
import os
import sys
import time
import json
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "core"))
sys.path.insert(0, str(BASE / "core" / "otonom"))
sys.path.insert(0, str(BASE / "voice"))
sys.path.insert(0, str(BASE / "support"))

from internal_state import InternalState
from hati_nurani import haruskah_bicara

# === Konfigurasi ===
INTERVAL = 60              # Cek tiap 60 detik
MIN_INTERVAL = 900         # Minimal 15 menit antar inisiatif
WEBHOOK_URL = os.environ.get("ORION_WEBHOOK", "")  # Discord webhook (opsional)
LOG_FILE = BASE / "logs" / "inisiatif_otonom.log"


def log(msg: str):
    """Log ke file + terminal."""
    waktu = datetime.now().strftime("%H:%M:%S")
    line = f"[{waktu}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def kirim_webhook(pesan: str) -> bool:
    """Kirim pesan ke Discord webhook (kalau ada)."""
    if not WEBHOOK_URL:
        return False
    
    try:
        payload = {
            "content": pesan,
            "username": "Orion",
        }
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 204
    except Exception as e:
        log(f"Webhook error: {e}")
        return False


def putar_suara(pesan: str):
    """Putar suara F1 (offline)."""
    try:
        from voice_orion import tts_supertonic_bytes
        import sounddevice as sd
        import numpy as np
        import io
        import wave
        
        wav_bytes = tts_supertonic_bytes(pesan, voice="F1")
        if not wav_bytes:
            return False
        
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
        
        sd.play(audio, sr)
        sd.wait()
        return True
    except Exception as e:
        log(f"Suara error: {e}")
        return False


def sudah_waktunya_inisiatif(state: InternalState) -> bool:
    """Cek apakah sudah waktunya inisiatif (jangan spam)."""
    if not state.last_initiative:
        return True
    
    try:
        last = datetime.fromisoformat(state.last_initiative)
        detik = (datetime.now() - last).total_seconds()
        return detik >= MIN_INTERVAL
    except Exception:
        return True


def main():
    log("=" * 60)
    log("  ORION INISIATIF OTONOM — Level 4")
    log("=" * 60)
    log(f"  Interval cek: {INTERVAL}s")
    log(f"  Minimal jeda inisiatif: {MIN_INTERVAL}s ({MIN_INTERVAL//60} menit)")
    log(f"  Webhook: {'ADA' if WEBHOOK_URL else 'TIDAK ADA'}")
    log("")

    while True:
        try:
            # 1. Muat + update state
            state = InternalState.muat()
            state.update()

            # 2. Cek dorongan
            dorongan = state.ada_dorongan()

            if not dorongan:
                state.simpan()
                time.sleep(INTERVAL)
                continue

            log(f"Dorongan: {[d[0] for d in dorongan]}")

            # 3. Cek apakah sudah waktunya (jangan spam)
            if not sudah_waktunya_inisiatif(state):
                log("  Skip — belum waktunya (jeda minimal)")
                state.simpan()
                time.sleep(INTERVAL)
                continue

            # 4. Panggil hati nurani
            log("  Panggil hati nurani...")
            keputusan = haruskah_bicara(state.ringkasan(), dorongan)

            log(f"  Keputusan: bicara={keputusan['bicara']}")
            log(f"  Alasan: {keputusan['alasan'][:80]}")

            # 5. Kalau bicara → kirim
            if keputusan["bicara"] and keputusan["pesan"]:
                pesan = keputusan["pesan"]
                log(f"  💬 Pesan: {pesan}")

                # Kirim ke webhook (kalau ada)
                if WEBHOOK_URL:
                    ok = kirim_webhook(pesan)
                    log(f"  Webhook: {'OK' if ok else 'GAGAL'}")

                # Putar suara F1
                log("  🔊 Putar suara F1...")
                putar_suara(pesan)

                # Catat inisiatif
                state.catat_initiative()
                log("  ✅ Inisiatif tercatat")
            else:
                log("  → Orion memutuskan untuk tidak bicara")

            # 6. Simpan state
            state.simpan()
            log("")

        except KeyboardInterrupt:
            log("\n[STOP] Orion inisiatif otonom dimatikan")
            break
        except Exception as e:
            log(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
