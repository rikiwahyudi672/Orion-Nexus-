import tts_orion
import voice_variasi as V
import time

print("Test 10 variasi acak Ardi...")
print()
for i in range(10):
    v = V.get_voice_cerdas()
    teks = f"Tes variasi nomor {i+1}"
    print(f"[{i+1}] {v['nama']}: rate={v['rate']}, vol={v['volume']}, pitch={v['pitch']}")
    tts_orion.bicara(teks, voice=v["voice"], rate=v["rate"], volume=v["volume"], pitch=v["pitch"])
    time.sleep(0.3)
