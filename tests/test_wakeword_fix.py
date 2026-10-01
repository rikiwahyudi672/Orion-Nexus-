"""test_wakeword_fix.py - Fix 2 channel audio"""
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from openwakeword.utils import download_models
from scipy.signal import resample
import time

info = sd.query_devices(kind="input")
SR = 44100
CHANNELS = 2  # Mic lo stereo
print(f"Mic: {info['name']}")
print(f"SR: {SR}, Channels: {CHANNELS}")

download_models()
model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

CHUNK = int(SR * 0.08)  # 80ms
stream = sd.InputStream(
    samplerate=SR,
    channels=CHANNELS,  # Baca 2 channel
    dtype="int16",
    blocksize=CHUNK
)
stream.start()

print()
print("Bilang 'Hey Jarvis' 15 detik...")
print(f"Chunk: {CHUNK}, SR: {SR}")
print()

end = time.time() + 15
max_score = 0
levels = []

while time.time() < end:
    audio, _ = stream.read(CHUNK)
    
    # Stereo -> Mono: rata-rata 2 channel
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = audio.flatten()
    
    # Cek level
    level = np.abs(audio).max()
    levels.append(level)
    
    # Resample 44100 -> 16000
    n = int(len(audio) * 16000 / SR)
    audio_16k = resample(audio, n).astype(np.int16)
    
    pred = model.predict(audio_16k)
    for k, v in pred.items():
        if v > max_score:
            max_score = v
            print(f"  Score: {max_score:.3f}  (level: {level})")

stream.stop()
stream.close()
print(f"\nMax score: {max_score:.3f}")
print(f"Level max: {max(levels)}, rata-rata: {sum(levels)/len(levels):.0f}")

if max_score > 0.3:
    print("OK - Wake word kedeteksi!")
else:
    print("GAGAL - Coba lagi lebih jelas")