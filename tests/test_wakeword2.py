"""test_wakeword2.py - Test mic index 5"""
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from openwakeword.utils import download_models
from scipy.signal import resample
import time

MIC = 5
SR = 44100
print(f"Pakai mic [{MIC}], SR: {SR}")

download_models()
model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

CHUNK = int(SR * 0.08)
stream = sd.InputStream(samplerate=SR, channels=1, dtype="int16", blocksize=CHUNK, device=MIC)
stream.start()

print("Bilang 'Hey Jarvis' 15 detik...")
end = time.time() + 15
max_score = 0

while time.time() < end:
    audio, _ = stream.read(CHUNK)
    audio = audio.flatten()
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