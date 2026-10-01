import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""orion_voice.py - Voice natural - voice-to-voice."""
import os
import sys
import io
import asyncio
import tempfile
import threading
from pathlib import Path
from datetime import datetime

# ============ KONFIGURASI ============
BASE = Path(__file__).parent
VOICE_DIR = BASE / "voice"
VOICE_DIR.mkdir(exist_ok=True)

# Voice natural - edge_tts
VOICE_NATURAL = "id-ID-GadisNeural"  # Indonesia - wanita
VOICE_ALTERNATIF = "id-ID-GadisNeural"  # Indonesia - wanita

# ============ 1. TTS - EDGE TTS (NATURAL) ============
def tts_edge(teks, output_file=None):
    """TTS dengan edge_tts - suara natural."""
    # === F1-SEMUA (f1_semua.py): Supertonic F1 dulu, fallback Edge-TTS ===
    try:
        from voice_orion import tts_bicara as _f1_bicara
        _f1_bicara(teks)
        return {"sukses": True, "file": None, "voice": "supertonic-F1",
                "size": 0, "mode": "supertonic-f1"}
    except Exception:
        pass
    if output_file is None:
        output_file = VOICE_DIR / f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    
    try:
        import edge_tts
        
        async def _generate():
            communicate = edge_tts.Communicate(teks, VOICE_NATURAL)
            await communicate.save(str(output_file))
        
        asyncio.run(_generate())
        
        return {
            "sukses": True,
            "file": str(output_file),
            "voice": VOICE_NATURAL,
            "size": output_file.stat().st_size,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def tts_gtts(teks, output_file=None):
    """TTS dengan gTTS - suara Google."""
    if output_file is None:
        output_file = VOICE_DIR / f"gtts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    
    try:
        from gtts import gTTS
        tts = gTTS(teks, lang="id", slow=False)
        tts.save(str(output_file))
        
        return {
            "sukses": True,
            "file": str(output_file),
            "voice": "gtts-id",
            "size": output_file.stat().st_size,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def tts_play(file_path):
    """Play TTS file."""
    try:
        import winsound
        winsound.PlaySound(str(file_path), winsound.SND_FILENAME)
        return True
    except Exception:
        try:
            from playsound import playsound
            playsound(str(file_path))
            return True
        except Exception:
            return False


def tts_speak(teks, play=True, mode="auto"):
    """Speak - TTS + play. Fallback: edge_tts -> gtts -> pyttsx3."""
    
    # 1. Edge TTS (natural)
    if mode in ["auto", "edge"]:
        hasil = tts_edge(teks)
        if hasil["sukses"]:
            if play and hasil.get("file"):
                tts_play(hasil["file"])
            hasil["mode"] = "edge_tts"
            return hasil
    
    # 2. gTTS (Google)
    if mode in ["auto", "gtts"]:
        hasil = tts_gtts(teks)
        if hasil["sukses"]:
            if play and hasil.get("file"):
                tts_play(hasil["file"])
            hasil["mode"] = "gtts"
            return hasil
    
    # 3. pyttsx3 (offline)
    if mode in ["auto", "pyttsx3"]:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(teks)
            engine.runAndWait()
            return {"sukses": True, "mode": "pyttsx3"}
        except Exception as e:
            return {"sukses": False, "error": str(e)}
    
    return {"sukses": False, "error": "Semua TTS gagal"}


# ============ 2. STT - SPEECH RECOGNITION ============
def stt_speech(duration=5, bahasa="id-ID"):
    """STT dengan speech_recognition."""
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            print(f"🎤 Mendengarkan... ({duration} detik)")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
        
        print("🔄 Memproses...")
        
        # Coba Google (online)
        try:
            teks = r.recognize_google(audio, language=bahasa)
            return {"sukses": True, "teks": teks, "mode": "google"}
        except sr.UnknownValueError:
            return {"sukses": False, "error": "Tidak bisa mengenali suara"}
        except sr.RequestError as e:
            return {"sukses": False, "error": f"Google error: {e}"}
    
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def stt_vosk(duration=5):
    """STT dengan vosk - offline."""
    try:
        import vosk
        import sounddevice as sd
        import json
        
        # Cari model
        model_dir = BASE / "models" / "vosk"
        if not model_dir.exists():
            return {"sukses": False, "error": "Vosk model belum ada"}
        
        # Cari model Indonesia
        model_path = None
        for p in model_dir.iterdir():
            if p.is_dir() and "id" in p.name.lower():
                model_path = p
                break
        
        if not model_path:
            return {"sukses": False, "error": "Model Indonesia tidak ada"}
        
        model = vosk.Model(str(model_path))
        rec = vosk.KaldiRecognizer(model, 16000)
        
        print(f"🎤 Mendengarkan... ({duration} detik)")
        
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1) as stream:
            for _ in range(int(duration * 16000 / 8000)):
                data, _ = stream.read(8000)
                if rec.AcceptWaveform(bytes(data)):
                    pass
        
        result = json.loads(rec.FinalResult())
        teks = result.get("text", "")
        
        if teks:
            return {"sukses": True, "teks": teks, "mode": "vosk"}
        else:
            return {"sukses": False, "error": "Tidak ada suara terdeteksi"}
    
    except Exception as e:
        return {"sukses": False, "error": str(e)}


# ============ 3. VOICE-TO-VOICE ============
def stt_whisper(duration=5):
    """STT dengan Whisper - support Indonesia."""
    try:
        import whisper
        import sounddevice as sd
        import tempfile
        import os
        from scipy.io.wavfile import write
        
        model = whisper.load_model("small")
        
        samplerate = 16000
        
        print(f"🎤 Mendengarkan... ({duration} detik)")
        
        recording = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        temp_file = tempfile.mktemp(suffix=".wav")
        write(temp_file, samplerate, recording)
        
        print("🔄 Transcribe...")
        result = model.transcribe(temp_file, language="id")
        teks = result.get("text", "").strip()
        os.remove(temp_file)
        
        if teks:
            return {"sukses": True, "teks": teks, "mode": "whisper"}
        else:
            return {"sukses": False, "error": "Tidak ada suara terdeteksi"}
    
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def voice_to_voice(duration=5):
    """Voice-to-voice - dengarkan, proses, jawab."""
    print("=" * 60)
    print("  VOICE-TO-VOICE")
    print("=" * 60)
    
    # 1. STT
    print("\n[1] MENDENGARKAN")
    hasil_stt = stt_speech(duration)
    
    if not hasil_stt["sukses"]:
        print(f"❌ STT gagal: {hasil_stt['error']}")
        return hasil_stt
    
    teks_user = hasil_stt["teks"]
    print(f"✅ Kamu: {teks_user}")
    
    # 2. Proses di Orion
    print("\n[2] PROSES ORION")
    try:
        sys.path.insert(0, str(BASE / "py"))
        from otak_orion import diskusi_orion
        
        jawab = diskusi_orion(teks_user)
        print(f"✅ Orion: {jawab}")
    except Exception as e:
        print(f"❌ Orion error: {e}")
        return {"sukses": False, "error": str(e)}
    
    # 3. TTS
    print("\n[3] BICARA")
    hasil_tts = tts_speak(jawab, play=True)
    
    return {
        "sukses": True,
        "user": teks_user,
        "orion": jawab,
        "tts": hasil_tts,
    }


# ============ 4. TEST ============
if __name__ == "__main__":
    print("=" * 60)
    print("  ORION VOICE")
    print("=" * 60)
    
    # Test TTS
    print("\n[TEST 1] TTS - Edge TTS")
    hasil = tts_speak("Halo Rik, gue Orion. Suara gue natural kan?", play=False)
    print(f"  Hasil: {hasil}")
    
    # Test STT
    print("\n[TEST 2] STT - Speech Recognition")
    print("  (Skip - butuh microphone)")
    
    # Voice-to-voice
    print("\n[TEST 3] Voice-to-Voice")
    print("  (Jalankan manual: python orion_voice.py voice)")
    
    # Cek argumen
    if len(sys.argv) > 1:
        if sys.argv[1] == "voice":
            voice_to_voice(5)
        elif sys.argv[1] == "tts":
            tts_speak(" ".join(sys.argv[2:]))
        elif sys.argv[1] == "stt":
            hasil = stt_speech(5)
            print(hasil)
