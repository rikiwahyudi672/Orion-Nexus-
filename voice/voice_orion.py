import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""voice_orion.py - Modul Voice ORION (Whisper STT + Edge-TTS)"""
import os
# Supertonic TTS
try:
    from supertonic import TTS
    HAS_SUPERTONIC = True
except ImportError:
    HAS_SUPERTONIC = False

# Cache TTS
_tts_cache = None

def _get_tts():
    global _tts_cache
    if _tts_cache is None and HAS_SUPERTONIC:
        _tts_cache = TTS(auto_download=True)
    return _tts_cache


# Cache style - biar gak load ulang
_style_cache = {}

def _get_style(voice_name):
    global _style_cache
    if voice_name not in _style_cache:
        tts = _get_tts()
        _style_cache[voice_name] = tts.get_voice_style(voice_name=voice_name)
    return _style_cache[voice_name]
import io
import wave
import tempfile
from pathlib import Path

# Load .env
BASE = Path(__file__).parent
ENV = BASE / ".env"
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "tiny")

# Groq client
_groq_client = None

def _get_groq():
    """Lazy init Groq client."""
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key or api_key == "gsk_xxxxx":
                return None
            _groq_client = Groq(api_key=api_key)
            print("[Voice] Groq Whisper siap.")
        except Exception as e:
            print(f"[Voice] Groq init error: {e}")
            _groq_client = None
    return _groq_client


def transkrip_groq(path_audio):
    """Transkrip pakai Groq Whisper API (cepat + akurat)."""
    client = _get_groq()
    if client is None:
        return None
    try:
        with open(path_audio, "rb") as f:
            hasil = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(os.path.basename(path_audio), f.read()),
                language="id",
            )
        return hasil.text.strip() if hasattr(hasil, "text") else str(hasil).strip()
    except Exception as e:
        print(f"[Voice] Groq transkrip error: {e}")
        return None
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = os.environ.get("WHISPER_COMPUTE", "int8")
WHISPER_LANG = os.environ.get("WHISPER_LANG", "id")

_model = None


def get_model():
    """Load Whisper model (lazy)."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        print(f"[Voice] Loading Whisper {WHISPER_MODEL}...")
        _model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
        print(f"[Voice] Whisper {WHISPER_MODEL} siap!")
    return _model


def transkrip_file(path_audio):
    """Transkrip file audio -> teks. Groq dulu, fallback lokal."""
    # Coba Groq dulu
    hasil = transkrip_groq(path_audio)
    if hasil:
        return hasil
    
    # Fallback ke Whisper lokal
    model = get_model()
    segments, info = model.transcribe(
        str(path_audio),
        language=WHISPER_LANG,
        beam_size=5,
        vad_filter=True,
    )
    teks = " ".join(seg.text.strip() for seg in segments)
    return teks.strip()


def transkrip_bytes(audio_bytes, sr=16000):
    """Transkrip bytes audio (raw PCM 16-bit mono) -> teks."""
    # Simpan ke WAV temp
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name

    with wave.open(temp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_bytes)

    try:
        hasil = transkrip_file(temp_path)
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

    return hasil


def tts_bicara_batch(teks, voice=None):
    """
    TTS batch: pecah kalimat, generate semua, play berurutan.
    Jeda antar kalimat hilang.
    """
    import re
    import numpy as np
    import sounddevice as sd
    
    if not HAS_SUPERTONIC:
        try:
            import tts_orion
            return tts_orion.bicara(teks, voice=voice)
        except Exception:
            return False
    
    try:
        tts = _get_tts()
        if tts is None:
            return False
        
        # Voice default: F1 (wanita)
        voice_name = voice or "F1"
        style = _get_style(voice_name)
        
        # Normalisasi teks dulu
        try:
            import normalisasi_teks
            teks = normalisasi_teks.normalisasi(teks)
        except Exception:
            pass
        
        # Sisipkan panggilan sayang
        try:
            import panggilan_sayang
            teks = panggilan_sayang.sisipkan_panggilan(teks)
        except Exception:
            pass
        
        # Kadang ORION nyeletuk emosi natural (20%)
        try:
            import emosi_natural
            import random as _r
            if _r.random() < 0.2:
                emosi_teks = emosi_natural.pilih_emosi_natural()
                if emosi_teks:
                    teks = emosi_teks + " " + teks
        except Exception:
            pass
        
        # Pecah kalimat
        kalimat_list = re.split(r'(?<=[.!?])\s+', teks.strip())
        kalimat_list = [k.strip() for k in kalimat_list if k.strip()]
        
        if not kalimat_list:
            return False
        
        # Ambil parameter emosi
        try:
            import emotion_voice
            params = emotion_voice.get_params_suara()
            speed = params.get("speed", 1.0)
            total_steps = params.get("total_steps", 5)
            volume = params.get("volume", 0.4)
            print("[Voice] Emosi: speed=" + str(round(speed, 2)) + ", steps=" + str(total_steps) + ", volume=" + str(round(volume, 2)))
        except Exception:
            speed = 1.0
            total_steps = 5
            volume = 0.4
        
        # Generate semua dulu
        audio_list = []
        for kalimat in kalimat_list:
            wav, duration = tts.synthesize(
                kalimat,
                voice_style=style,
                lang="id",
                total_steps=total_steps,
                speed=speed,
            )
            audio = np.array(wav, dtype=np.float32).flatten()
            audio_list.append(audio)
        
        # Gabung semua audio
        if len(audio_list) == 1:
            audio_gabung = audio_list[0]
        else:
            audio_gabung = np.concatenate(audio_list)
        
        # Normalisasi dengan volume dari emosi
        max_val = np.abs(audio_gabung).max()
        if max_val > 0:
            audio_gabung = audio_gabung * (volume / max_val)
        audio_gabung = np.clip(audio_gabung, -1.0, 1.0)
        
        # Play sekali - tanpa jeda
        sd.play(audio_gabung, samplerate=44100)
        sd.wait()
        return True
    except Exception as e:
        print(f"[Voice] Batch error: {e}")
        return False


def tts_bicara(teks, voice=None):
    """TTS via Supertonic 3 (voice F1)."""
    if not HAS_SUPERTONIC:
        # Fallback ke Edge-TTS
        try:
            import tts_orion
            return tts_orion.bicara(teks, voice=voice)
        except Exception as e:
            print(f"[Voice] Edge-TTS error: {e}")
            return False
    
    try:
        import sounddevice as sd
        import numpy as np
        
        tts = _get_tts()
        if tts is None:
            return False
        
        # Voice default: F1 - pakai cache
        voice_name = voice or "F1"
        style = _get_style(voice_name)
        
        # Sintesis
        wav, duration = tts.synthesize(teks, voice_style=style, lang="id", total_steps=5)
        
        # Normalisasi volume + flatten
        audio = np.array(wav, dtype=np.float32).flatten()
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio * (0.4 / max_val)  # Volume 0.4
        audio = np.clip(audio, -1.0, 1.0)
        
        # Putar (mono - sudah di-flatten)
        sd.play(audio, samplerate=44100)
        sd.wait()
        return True
    except Exception as e:
        print(f"[Voice] Supertonic error: {e}")
        # Fallback
        try:
            import tts_orion
            return tts_orion.bicara(teks, voice=voice)
        except Exception:
            return False


# === Cache audio TTS ===
import hashlib as _hashlib
_AUDIO_CACHE_DIR = Path(__file__).parent / "cache_tts"
_AUDIO_CACHE_DIR.mkdir(exist_ok=True)

def _audio_cache_path(teks, voice, steps, samplerate):
    raw = f"{teks}|{voice}|{steps}|{samplerate}"
    key = _hashlib.md5(raw.encode("utf-8")).hexdigest()
    return _AUDIO_CACHE_DIR / f"{key}.wav"

def tts_supertonic_bytes(teks, voice=None, samplerate=44100):
    """
    TTS via Supertonic -> bytes WAV (buat Discord/web).
    Tidak putar di speaker lokal, cuma return audio bytes.
    """
    if not HAS_SUPERTONIC:
        print("[Voice] Supertonic tidak ada, fallback ke Edge TTS")
        return tts_bytes(teks, voice=voice)
    
    try:
        import numpy as np
        import io as _io
        import wave
        
        tts = _get_tts()
        if tts is None:
            return None
        
        # Voice default: F1
        voice_name = voice or "F1"
        steps = 5

        # Cek cache dulu
        cache_path = _audio_cache_path(teks, voice_name, steps, samplerate)
        if cache_path.exists():
            print(f"[Voice] Cache hit: {cache_path.name}")
            return cache_path.read_bytes()

        style = _get_style(voice_name)
        
        # Sintesis (sama seperti tts_bicara, tapi tidak putar di speaker)
        wav, duration = tts.synthesize(teks, voice_style=style, lang="id", total_steps=steps)
        
        # Normalisasi
        audio = np.array(wav, dtype=np.float32).flatten()
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio * (0.8 / max_val)
        audio = np.clip(audio, -1.0, 1.0)
        
        # Konversi ke int16 (format WAV)
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Bikin WAV bytes
        buf = _io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)       # Mono
            wf.setsampwidth(2)       # 16-bit
            wf.setframerate(samplerate)
            wf.writeframes(audio_int16.tobytes())
        
        wav_bytes = buf.getvalue()

        # Simpan ke cache
        try:
            cache_path.write_bytes(wav_bytes)
            print(f"[Voice] Cache saved: {cache_path.name}")
        except Exception as e:
            print(f"[Voice] Cache save error: {e}")

        return wav_bytes
    except Exception as e:
        print(f"[Voice] Supertonic bytes error: {e}")
        # Fallback ke Edge TTS
        return tts_bytes(teks, voice=voice)


def tts_bytes(teks, voice=None):
    """TTS -> bytes MP3 (buat web, safe di async loop)."""
    try:
        import edge_tts
        import concurrent.futures

        voice = voice or os.environ.get("TTS_VOICE", "id-ID-GadisNeural")

        async def _gen():
            communicate = edge_tts.Communicate(teks, voice)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf.getvalue()

        # Jalanin di thread baru (biar gak konflik sama event loop FastAPI)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(lambda: asyncio.new_event_loop().run_until_complete(_gen())).result(timeout=30)
    except Exception as e:
        print(f"[Voice] TTS bytes error: {e}")
        return None


# Test
# === SUARA NATURAL (colok_suara_natural.py) ===
def tts_bicara_natural(teks, voice=None, steps=12):
    """TTS Supertonic F1 lebih natural: sintesis per kalimat + steps lebih banyak.

    Tanpa sisipan panggilan sayang, tanpa celetukan emosi — teks apa adanya.
    steps=12: lebih natural dari default 5, tapi sintesis lebih lambat.
    """
    if not HAS_SUPERTONIC:
        return tts_bicara(teks, voice=voice)
    try:
        import re
        import numpy as np
        import sounddevice as sd

        tts = _get_tts()
        if tts is None:
            return False

        voice_name = voice or "F1"
        style = _get_style(voice_name)

        # Normalisasi teks (angka, singkatan) biar pengucapan wajar
        try:
            import normalisasi_teks
            teks = normalisasi_teks.normalisasi(teks)
        except Exception:
            pass

        # Pecah per kalimat: intonasi lebih hidup daripada sekali generate panjang
        kalimat_list = [k.strip() for k in re.split(r'(?<=[.!?])\s+', str(teks).strip()) if k.strip()]
        if not kalimat_list:
            return False

        audio_list = []
        for kalimat in kalimat_list:
            wav, duration = tts.synthesize(kalimat, voice_style=style, lang="id", total_steps=steps)
            audio_list.append(np.array(wav, dtype=np.float32).flatten())

        audio = audio_list[0] if len(audio_list) == 1 else np.concatenate(audio_list)
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio * (0.4 / max_val)
        audio = np.clip(audio, -1.0, 1.0)

        sd.play(audio, samplerate=44100)
        sd.wait()
        return True
    except Exception as e:
        print(f"[Voice] Natural error: {e}")
        try:
            return tts_bicara(teks, voice=voice)
        except Exception:
            return False


# === SUARA STREAMING (colok_suara_stream.py) ===
def tts_bicara_stream(teks, voice=None, steps=12):
    """TTS Supertonic F1 streaming per kalimat: kalimat pertama langsung bunyi
    selagi kalimat berikutnya di-generate (pipeline). Tanpa sisipan sayang."""
    if not HAS_SUPERTONIC:
        return tts_bicara(teks, voice=voice)
    try:
        import re
        import threading
        import numpy as np
        import sounddevice as sd

        tts = _get_tts()
        if tts is None:
            return False

        voice_name = voice or "F1"
        style = _get_style(voice_name)

        try:
            import normalisasi_teks
            teks = normalisasi_teks.normalisasi(teks)
        except Exception:
            pass

        kalimat_list = [k.strip() for k in re.split(r'(?<=[.!?])\s+', str(teks).strip()) if k.strip()]
        if not kalimat_list:
            return False

        def _synth(kalimat):
            wav, duration = tts.synthesize(kalimat, voice_style=style, lang="id", total_steps=steps)
            audio = np.array(wav, dtype=np.float32).flatten()
            max_val = np.abs(audio).max()
            if max_val > 0:
                audio = audio * (0.4 / max_val)
            return np.clip(audio, -1.0, 1.0)

        audios = {}

        def _gen(i):
            try:
                audios[i] = _synth(kalimat_list[i])
            except Exception:
                audios[i] = None

        dimainkan = 0
        th = threading.Thread(target=_gen, args=(0,), daemon=True)
        th.start()
        for i in range(len(kalimat_list)):
            th.join()
            audio = audios.get(i)
            if i + 1 < len(kalimat_list):
                th = threading.Thread(target=_gen, args=(i + 1,), daemon=True)
                th.start()
            if audio is not None:
                sd.play(audio, samplerate=44100)
                sd.wait()
                dimainkan += 1

        if dimainkan == 0:
            return tts_bicara(teks, voice=voice)
        return True
    except Exception as e:
        print(f"[Voice] Stream error: {e}")
        try:
            return tts_bicara(teks, voice=voice)
        except Exception:
            return False


# === SUARA NATURAL (colok_suara_natural.py) ===
def tts_bicara_natural(teks, voice=None, steps=12):
    """TTS Supertonic F1 lebih natural: sintesis per kalimat + steps lebih banyak.

    Tanpa sisipan panggilan sayang, tanpa celetukan emosi — teks apa adanya.
    steps=12: lebih natural dari default 5, tapi sintesis lebih lambat.
    """
    if not HAS_SUPERTONIC:
        return tts_bicara(teks, voice=voice)
    try:
        import re
        import numpy as np
        import sounddevice as sd

        tts = _get_tts()
        if tts is None:
            return False

        voice_name = voice or "F1"
        style = _get_style(voice_name)

        # Normalisasi teks (angka, singkatan) biar pengucapan wajar
        try:
            import normalisasi_teks
            teks = normalisasi_teks.normalisasi(teks)
        except Exception:
            pass

        # Pecah per kalimat: intonasi lebih hidup daripada sekali generate panjang
        kalimat_list = [k.strip() for k in re.split(r'(?<=[.!?])\s+', str(teks).strip()) if k.strip()]
        if not kalimat_list:
            return False

        audio_list = []
        for kalimat in kalimat_list:
            wav, duration = tts.synthesize(kalimat, voice_style=style, lang="id", total_steps=steps)
            audio_list.append(np.array(wav, dtype=np.float32).flatten())

        audio = audio_list[0] if len(audio_list) == 1 else np.concatenate(audio_list)
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio * (0.4 / max_val)
        audio = np.clip(audio, -1.0, 1.0)

        sd.play(audio, samplerate=44100)
        sd.wait()
        return True
    except Exception as e:
        print(f"[Voice] Natural error: {e}")
        try:
            return tts_bicara(teks, voice=voice)
        except Exception:
            return False


if __name__ == "__main__":
    print("=" * 50)
    print("  VOICE ORION - Test")
    print("=" * 50)
    print(f"  Model   : {WHISPER_MODEL}")
    print(f"  Device  : {WHISPER_DEVICE}")
    print(f"  Compute : {WHISPER_COMPUTE}")
    print(f"  Lang    : {WHISPER_LANG}")
    print()

    # Test load model
    print("[1] Load model...")
    get_model()
    print("    OK")

    # Test TTS
    print()
    print("[2] Test TTS...")
    hasil = tts_bicara("Halo bos, saya Orion, siap membantu.")
    print(f"    TTS: {'OK' if hasil else 'GAGAL'}")

    print()
    print("=" * 50)
    print("  SELESAI")
    print("=" * 50)

# ============ ALIAS UNTUK KOMPATIBILITAS ============
# Ditambahkan otomatis oleh Orion
tts_speak = _get_tts  # alias dari _get_tts



# ============ FUNGSI VOICE-KAN ============
def voice_kan(pesan, **kwargs):
    """Voice-kan pesan. Wrapper untuk tts_bicara."""
    try:
        return tts_bicara(pesan, **kwargs)
    except TypeError:
        # Kalau ada parameter yang tidak dikenal, coba tanpa kwargs
        return tts_bicara(pesan)




# ============ GROQ HELPER ============
def get_groq_client():
    """Ambil Groq client - TANPA base_url override."""
    import os
    from groq import Groq
    from dotenv import load_dotenv
    from pathlib import Path
    
    BASE = Path(__file__).parent.parent
    for env in [BASE / ".env", BASE.parent / ".env"]:
        if env.exists():
            load_dotenv(env, override=True)
            break
    
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY tidak ada")
    
    # JANGAN pakai base_url - Groq client sudah punya default
    return Groq(api_key=api_key)


def groq_transcribe(audio_path, model="whisper-large-v3-turbo"):
    """Transkrip audio pakai Groq Whisper."""
    try:
        client = get_groq_client()
        
        with open(audio_path, "rb") as f:
            r = client.audio.transcriptions.create(
                file=(audio_path, f.read()),
                model=model,
            )
        return {"sukses": True, "teks": r.text}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def groq_chat(pesan, model="openai/gpt-oss-120b"):
    """Chat pakai Groq."""
    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": pesan}],
            max_tokens=2000,
        )
        return {"sukses": True, "jawaban": r.choices[0].message.content}
    except Exception as e:
        return {"sukses": False, "error": str(e)}
# ============ END HELPER ============


# ====================================================================
# TTS CEPAT - TANPA JEDA LAMA
# ====================================================================

def tts_cepat(teks, voice=None):
    """TTS cepat - batch + overlap."""
    import threading
    import re
    
    # Split kalimat
    kalimat = re.split(r'(?<=[.!?])\s+', teks)
    kalimat = [k.strip() for k in kalimat if k.strip()]
    
    if not kalimat:
        return False
    
    # Generate semua audio paralel
    threads = []
    hasil_audio = [None] * len(kalimat)
    
    def generate_audio(i, k):
        try:
            hasil_audio[i] = _generate_audio(k, voice)
        except Exception:
            pass
    
    for i, k in enumerate(kalimat):
        t = threading.Thread(target=generate_audio, args=(i, k))
        t.start()
        threads.append(t)
    
    # Tunggu semua generate selesai
    for t in threads:
        t.join()
    
    # Play berurutan - TANPA jeda
    for audio in hasil_audio:
        if audio:
            _play_audio(audio)
    
    return True


def tts_stream(teks, voice=None):
    """TTS stream - play sambil generate."""
    import threading
    import queue
    import re
    
    kalimat = re.split(r'(?<=[.!?])\s+', teks)
    kalimat = [k.strip() for k in kalimat if k.strip()]
    
    q = queue.Queue()
    
    def generate():
        for k in kalimat:
            try:
                audio = _generate_audio(k, voice)
                q.put(audio)
            except Exception:
                q.put(None)
        q.put("DONE")
    
    # Start generate thread
    threading.Thread(target=generate, daemon=True).start()
    
    # Play sambil tunggu
    while True:
        audio = q.get()
        if audio == "DONE":
            break
        if audio:
            _play_audio(audio)
    
    return True


def _generate_audio(teks, voice=None):
    """Generate audio dari teks - internal."""
    try:
        # Coba pakai TTS engine
        tts = _get_tts()
        # Simpan ke temp file
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()
        # Generate
        tts.save_audio(teks, tmp.name, voice=voice)
        return tmp.name
    except Exception:
        return None


def _play_audio(audio_path):
    """Play audio - internal."""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # Hapus file
        import os
        os.remove(audio_path)
    except Exception:
        pass


# ====================================================================
# END TTS CEPAT
# ====================================================================

