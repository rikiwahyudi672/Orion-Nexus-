import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
voice_stream.py - Streaming TTS untuk ORION (versi simple, single-thread).
LLM stream -> potong per kalimat -> TTS langsung (berurutan).
"""
import re
from pathlib import Path

BASE = Path(__file__).parent


def _potong_kalimat(teks: str):
    """Potong teks jadi kalimat lengkap + sisa."""
    pola = r'([^.!?\n]+[.!?\n]+)'
    matches = re.findall(pola, teks)
    if not matches:
        return [], teks
    total_matched = sum(len(m) for m in matches)
    sisa = teks[total_matched:]
    kalimat_list = [m.strip() for m in matches if m.strip()]
    return kalimat_list, sisa


def stream_dan_tts(pesan, llm_stream_func, tts_func, history=None, min_panjang=8):
    """
    Stream output LLM, potong per kalimat, TTS langsung (berurutan).
    Single-thread: lebih simple, urutan terjamin.
    """
    buffer = ""
    full_text = []
    kalimat_diucap = []

    try:
        for chunk in llm_stream_func(pesan, history=history):
            if not chunk:
                continue
            full_text.append(chunk)
            buffer += chunk

            # Cek kalimat lengkap
            kalimat_list, sisa = _potong_kalimat(buffer)
            buffer = sisa

            for kalimat in kalimat_list:
                if len(kalimat) >= min_panjang:
                    print(f"  🔊 {kalimat}")
                    try:
                        tts_func(kalimat)
                    except Exception as e:
                        print(f"  [TTS error] {e}")
                    kalimat_diucap.append(kalimat)
                else:
                    # Terlalu pendek, gabung ke buffer
                    buffer = kalimat + " " + buffer

        # Sisa terakhir
        if buffer.strip():
            print(f"  🔊 {buffer.strip()}")
            try:
                tts_func(buffer.strip())
            except Exception as e:
                print(f"  [TTS error] {e}")
            kalimat_diucap.append(buffer.strip())

    except Exception as e:
        print(f"[voice_stream] Error: {e}")

    return "".join(full_text), kalimat_diucap


def stream_jawab(pesan, history=None):
    """Wrapper: pakai otak_orion untuk stream, voice_orion untuk TTS."""
    try:
        import otak_orion
        import voice_orion
    except Exception as e:
        print(f"[voice_stream] Import error: {e}")
        return None

    def llm_stream(p, history=None):
        if hasattr(otak_orion, "diskusi_orion_stream"):
            yield from otak_orion.diskusi_orion_stream(p, history=history)
        elif hasattr(otak_orion, "diskusi_stream"):
            yield from otak_orion.diskusi_stream(p, history=history)
        else:
            hasil = otak_orion.diskusi_orion(p, history=history)
            yield hasil

    def tts(teks):
        try:
            voice_orion.tts_bicara(teks)
        except Exception as e:
            print(f"[voice_stream] TTS error: {e}")

    hasil_text, kalimat = stream_dan_tts(pesan, llm_stream, tts, history=history)
    return hasil_text


if __name__ == "__main__":
    print("=== Test voice_stream (single-thread) ===")

    teks = "Halo bos. Apa kabar? Gue Orion. Siap bantu!"
    kalimat, sisa = _potong_kalimat(teks)
    print(f"Kalimat: {kalimat}")
    print(f"Sisa: '{sisa}'")
    print()

    def dummy_tts(t):
        print(f"  >> TTS selesai: {t}")

    def dummy_llm(pesan, history=None):
        for chunk in ["Halo bos. ", "Apa kabar? ", "Gue Orion. ", "Siap bantu!"]:
            yield chunk

    hasil, kalimat = stream_dan_tts("test", dummy_llm, dummy_tts)
    print()
    print(f"Full text: {hasil}")
    print(f"Kalimat diucap: {kalimat}")
