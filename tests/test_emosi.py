import tts_orion
import voice_variasi as V

kalimat = {
    "marah": "Bos! Gue udah bilang jangan gitu!",
    "sedih": "Bos, gue sedih...",
    "takut": "Riki, gue takut!",
    "kaget": "WHAT?! Serius?!",
    "ketus": "Iya.",
    "lelah": "Gue capek, bos...",
}

for emosi, teks in kalimat.items():
    p = V.get_emosi_params(emosi)
    print(f"[{emosi}] {teks}")
    tts_orion.bicara(teks, voice=p["voice"], rate=p["rate"], volume=p["volume"], pitch=p["pitch"])
    import time
    time.sleep(0.5)
