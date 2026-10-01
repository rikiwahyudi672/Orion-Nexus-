"""test_wakeword.py - Test wake word dengan auto-detect sample rate"""
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from openwakeword.utils import download_models
from scipy.signal import resample
import time

info = sd.query_devices(kind="input")
SR = int(info["default_samplerate"])
print(f"Mic default: {info['name']}")
print(f"Sample rate: {SR} Hz")

download_models()
model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

CHUNK = int(SR * 0.08)
stream = sd.InputStream(samplerate=SR, channels=1, dtype="int16", blocksize=CHUNK)
stream.start()

print()
print("Bilang 'Hey Jarvis' 15 detik...")
print()

end = time.time() + 15
max_score = 0

while time.time() < end:
    audio, _ = stream.read(CHUNK)
    audio = audio.flatten()
    
    if SR != 16000:
        n = int(len(audio) * 16000 / SR)
        audio = resample(audio, n).astype(np.int16)
    
    pred = model.predict(audio)
    for k, v in pred.items():
        if v > max_score:
            max_score = v
            print(f"  Score: {max_score:.3f}")

stream.stop()
stream.close()
print(f"\nMax score: {max_score:.3f}")

if max_score > 0.3:
    print("OK - Wake word kedeteksi!")
else:
    print("GAGAL - Coba mic lain atau lebih dekat")