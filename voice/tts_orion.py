import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""tts_orion.py - Modul TTS ORION pakai Edge-TTS + pygame"""
import asyncio
import os
import tempfile
import time
from pathlib import Path

# Konfigurasi
VOICE_DEFAULT = "id-ID-GadisNeural"
RATE = "+15%"  # Lebih cepet biar hemat waktu
RATE = None
VOLUME = None
OUTPUT_DIR = Path(__file__).parent / "output" / "tts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def _generate(text, voice, output_path, rate=None, volume=None, pitch=None):
    import edge_tts
    kwargs = {}
    if rate or RATE:
        kwargs["rate"] = rate or RATE
    if volume or VOLUME:
        kwargs["volume"] = volume or VOLUME
    if pitch:
        kwargs["pitch"] = pitch
    tts = edge_tts.Communicate(text, voice, **kwargs)
    await tts.save(str(output_path))


def _play_audio(path):
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"  pygame error: {e}")
        return False


def bicara(teks, voice=None, simpan=False, rate=None, volume=None, pitch=None):
    """TTS dengan parameter variatif.
    
    Args:
        teks: teks yang mau diucap
        voice: nama voice Edge-TTS
        simpan: simpan ke output/
        rate: kecepatan ("+10%", "-10%", dll)
        volume: volume ("+20%", "-20%", dll)
        pitch: nada ("+5Hz", "-5Hz", dll)
    """
    # === F1-SEMUA (f1_semua.py): pakai Supertonic F1 dulu ===
    try:
        from voice_orion import tts_bicara as _f1_bicara
        _f1_bicara(teks)
        return True
    except Exception:
        pass
    if not voice:
        voice = VOICE_DEFAULT

    # Hash unik berdasarkan semua parameter
    h = abs(hash((teks, voice, rate, volume, pitch))) % 100000

    if simpan:
        filename = f"orion_{h}.mp3"
        output = OUTPUT_DIR / filename
    else:
        output = Path(tempfile.gettempdir()) / f"orion_tts_{h}.mp3"

    try:
        asyncio.run(_generate(teks, voice, output, rate=rate, volume=volume, pitch=pitch))
        if not output.exists() or output.stat().st_size == 0:
            print("  TTS error: File audio kosong")
            return False
        _play_audio(output)
        if not simpan and output.exists():
            try:
                output.unlink()
            except:
                pass
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


def test():
    print("  Test suara ORION...")
    bicara("Halo Riki, saya ORION, asisten pribadi Anda.")


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST TTS ORION")
    print("=" * 60)
    print()
    print("[1] id-ID-ArdiNeural")
    bicara("Halo Riki, saya ORION. Suara saya sekarang lebih natural kan?", "id-ID-ArdiNeural")
    print()
    print("[2] id-ID-GadisNeural")
    bicara("Halo Riki, saya ORION versi wanita.", "id-ID-GadisNeural")
    print()
    print("[3] en-US-AriaNeural")
    bicara("Hello Riki, I am ORION.", "en-US-AriaNeural")
    print()
    print("[OK] Selesai!")