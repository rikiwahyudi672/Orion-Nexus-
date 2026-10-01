"""test_voice.py - Test voice command manual"""
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import wave

SR = 44100
CHANNELS = 2
DURATION = 5

print("=" * 60)
print("  VOICE COMMAND TEST")
print("=" * 60)
print()
print("Rekam 5 detik...")
print("Bilang: 'Buka notepad' atau 'Halo Orion'")
print()

# Rekam
audio = sd.rec(int(DURATION * SR), samplerate=SR, channels=CHANNELS, dtype='int16')
sd.wait()
print("Selesai rekam!")

# Convert stereo -> mono
if audio.ndim > 1:
    audio = audio.mean(axis=1)
audio = audio.flatten().astype(np.int16)

# Simpan WAV
with wave.open("voice_test.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(audio.tobytes())

print("File: voice_test.wav")
print()
print("Mengirim ke Google Speech API...")

# Recognize
r = sr.Recognizer()
with sr.AudioFile("voice_test.wav") as source:
    audio_data = r.record(source)

try:
    teks = r.recognize_google(audio_data, language="id-ID")
    print()
    print("=" * 60)
    print(f"  Lo bilang: {teks}")
    print("=" * 60)
    
    # Deteksi command
    teks_lower = teks.lower()
    print()
    print("Command yang kedeteksi:")
    if "notepad" in teks_lower:
        print("  -> Buka Notepad")
    elif "browser" in teks_lower or "google" in teks_lower:
        print("  -> Buka Browser")
    elif "halo" in teks_lower or "hai" in teks_lower:
        print("  -> Halo juga!")
    else:
        print("  -> Command gak dikenali")
except sr.UnknownValueError:
    print("Google gak ngerti suara lo")
except sr.RequestError as e:
    print(f"Error Google API: {e}")