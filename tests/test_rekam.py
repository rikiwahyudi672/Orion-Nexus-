"""test_rekam.py - Test rekam & cek level audio"""
import sounddevice as sd
import numpy as np
import wave

SR = 44100
DURATION = 3

print(f"Default input: {sd.query_devices(kind='input')['name']}")
print(f"Rekam {DURATION} detik... BILANG: TES TES TES")
print()

audio = sd.rec(int(DURATION * SR), samplerate=SR, channels=1, dtype='int16')
sd.wait()

level_max = np.abs(audio).max()
level_avg = np.abs(audio).mean()

print(f"Level max: {level_max}")
print(f"Level rata-rata: {level_avg:.0f}")

if level_max < 100:
    print()
    print("!!! MIC GAK NANGKEP SUARA !!!")
    print("Cek:")
    print("  1. Mic di-mute? (tombol Fn+F4 atau icon mic)")
    print("  2. Windows Settings -> Privacy -> Microphone: ON")
    print("  3. Volume mic di Sound Settings")
else:
    print()
    print("OK - Mic nangkep suara!")
    # Simpan WAV
    with wave.open("test_rec.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(audio.tobytes())
    print("File: test_rec.wav")
    
    # Putar ulang
    print("Memutar ulang...")
    with wave.open("test_rec.wav", "rb") as wf:
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    sd.play(data, SR)
    sd.wait()
    print("Selesai!")