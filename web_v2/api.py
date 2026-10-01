"""web_v2/api.py - API backend untuk web dashboard"""
import os
import sys
import json
import io
import sqlite3
import subprocess
import webbrowser
import tempfile
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / 'voice'))
sys.path.insert(0, str(BASE / 'core'))

import core
import orion_jarvis
import voice_orion

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="ORION API v2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

orion_jarvis.init_db_knowledge()


# ============ STATUS ============
@app.get("/api/status")
async def status():
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    bat = psutil.sensors_battery()
    return {
        "cpu": round(cpu),
        "ram": round(mem.percent),
        "disk": round(disk.percent),
        "baterai": round(bat.percent) if bat else 0,
    }


# ============ AKSI ============
@app.post("/api/screenshot")
async def screenshot():
    try:
        import pyautogui
        Path(core.P["output"]).mkdir(exist_ok=True)
        nama = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file = Path(core.P["output"]) / nama
        pyautogui.screenshot(str(file))
        core.catat(f"Web screenshot: {nama}")
        return {"message": "Screenshot diambil", "file": nama}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/notepad")
async def notepad():
    subprocess.Popen("notepad", shell=True)
    return {"message": "Notepad dibuka"}


@app.post("/api/browser")
async def browser():
    webbrowser.open("https://google.com")
    return {"message": "Browser dibuka"}


@app.post("/api/lock")
async def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return {"message": "PC dikunci"}


@app.post("/api/volume_up")
async def volume_up():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        device = AudioUtilities.GetSpeakers()
        iface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(iface, POINTER(IAudioEndpointVolume))
        cur = round(vol.GetMasterVolumeLevelScalar() * 100)
        new = min(100, cur + 10)
        vol.SetMasterVolumeLevelScalar(new/100, None)
        return {"message": f"Volume: {new}%"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/volume_down")
async def volume_down():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        device = AudioUtilities.GetSpeakers()
        iface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(iface, POINTER(IAudioEndpointVolume))
        cur = round(vol.GetMasterVolumeLevelScalar() * 100)
        new = max(0, cur - 10)
        vol.SetMasterVolumeLevelScalar(new/100, None)
        return {"message": f"Volume: {new}%"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/status")
async def status_action():
    return {"message": "Cek status di Home"}


# ============ CHAT ============
@app.post("/api/chat")
async def chat(data: dict):
    pesan = data.get("pesan", "").strip()
    if not pesan:
        raise HTTPException(400, "Pesan kosong")
    balasan = orion_jarvis.proses(pesan)
    if balasan == "__EXIT__":
        balasan = "Sampai jumpa, bos!"
    if balasan is None:
        balasan = "(ok)"
    return {"balasan": balasan}


# ============ VOICE ============
@app.post("/api/voice")
async def voice(audio: UploadFile = File(...)):
    try:
        # Simpan audio
        data = await audio.read()
        suffix = ".webm"
        if audio.filename:
            suffix = Path(audio.filename).suffix or ".webm"

        temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp.write(data)
        temp.close()

        # Convert ke WAV pakai ffmpeg (kalau ada), atau langsung transkrip
        wav_path = temp.name
        try:
            import subprocess as sp
            wav_out = temp.name + ".wav"
            sp.run(["ffmpeg", "-y", "-i", temp.name, "-ar", "16000", "-ac", "1", wav_out],
                   capture_output=True, timeout=30)
            if Path(wav_out).exists():
                wav_path = wav_out
        except Exception:
            pass

        # Transkrip
        teks = voice_orion.transkrip_file(wav_path)

        # Hapus temp
        for p in [temp.name, wav_path]:
            try:
                os.unlink(p)
            except Exception:
                pass

        if not teks:
            return {"teks": "", "balasan": "Gak kedengeran, bos. Coba lagi."}

        # Proses
        balasan = orion_jarvis.proses(teks)
        if balasan == "__EXIT__":
            balasan = "Sampai jumpa!"
        if balasan is None:
            balasan = "(ok)"

        return {"teks": teks, "balasan": balasan}
    except Exception as e:
        raise HTTPException(500, f"Voice error: {e}")


# ============ TTS ============
@app.get("/api/tts")
async def tts(teks: str):
    try:
        audio = voice_orion.tts_supertonic_bytes(teks, voice="F1")
        if not audio:
            raise HTTPException(500, "TTS gagal")
        return Response(content=audio, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(500, str(e))


# ============ PREDIKSI ============
@app.post("/api/prediksi")
async def prediksi(jam: float = 8):
    try:
        otak = core.Otak()
        akt, conf = otak.prediksi(jam)
        if akt:
            return {"message": f"Jam {jam:04.1f} â†’ <strong>{akt}</strong> ({conf*100:.1f}%)"}
        return {"message": "Otak belum dilatih"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/topn")
async def topn(jam: float = 8, n: int = 3):
    try:
        otak = core.Otak()
        hasil = otak.prediksi_top_n(jam, n=n)
        return {"hasil": [{"aktivitas": a, "conf": c} for a, c in hasil]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/perhari")
async def perhari(hari: str = "Senin", jam: float = 8):
    try:
        otak = core.Otak()
        akt, conf = otak.prediksi_per_hari(jam, hari)
        return {"message": f"{hari} jam {jam:04.1f} â†’ <strong>{akt}</strong> ({conf*100:.1f}%)"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ============ KNOWLEDGE ============
@app.post("/api/fakta")
async def simpan_fakta(data: dict):
    key = data.get("key", "").strip()
    val = data.get("value", "").strip()
    if not key or not val:
        raise HTTPException(400, "Key & value wajib")
    orion_jarvis.ingat(key, val)
    return {"message": f"Diingat: {key}"}


@app.get("/api/fakta")
async def get_fakta():
    rows = orion_jarvis.lihat_fakta()
    return {"fakta": [{"key": k, "value": v} for k, v in rows]}


@app.post("/api/note")
async def simpan_note(data: dict):
    isi = data.get("isi", "").strip()
    if not isi:
        raise HTTPException(400, "Isi kosong")
    orion_jarvis.catat_note(isi)
    return {"message": "Tercatat"}


# ============ REMINDER ============
@app.post("/api/reminder")
async def simpan_reminder(data: dict):
    jam = data.get("jam", "").strip()
    pesan = data.get("pesan", "").strip()
    if not jam or not pesan:
        raise HTTPException(400, "Jam & pesan wajib")
    orion_jarvis.set_reminder(jam, pesan)
    return {"message": f"Reminder set: {jam}"}


@app.get("/api/reminder")
async def get_reminder():
    rows = orion_jarvis.lihat_reminders()
    return {"reminder": [{"id": i, "jam": j, "pesan": p} for i, j, p in rows]}


# ============ INFO ============
@app.get("/api/info-otak")
async def info_otak():
    model = Path(core.P["model"])
    if model.exists():
        size = model.stat().st_size
        return {
            "status": "ada",
            "size": size,
            "aktivitas": core.CFG["model"]["aktivitas"],
            "titik": len(core.DATA_HABIT),
        }
    return {"status": "belum"}


@app.get("/api/backup")
async def get_backup():
    backup_dir = BASE / "backups"
    if not backup_dir.exists():
        return {"backup": []}
    files = sorted(backup_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)[:20]
    return {"backup": [{"nama": f.name, "size": f.stat().st_size} for f in files]}

# ============ FITUR TAMBAHAN ============

@app.get("/api/cuaca")
async def cuaca(kota: str = None):
    """Cuaca dari OpenWeather atau fallback."""
    try:
        import requests
        api = core.CFG["cuaca"]["api_key"]
        if api == "GANTI_DENGAN_API_KEY_OPENWEATHER":
            return {"error": "API key belum di-set", "kota": kota or core.CFG["cuaca"]["kota"]}
        kota = kota or core.CFG["cuaca"]["kota"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={kota}&appid={api}&units=metric&lang=id"
        r = requests.get(url, timeout=5).json()
        return {
            "kota": r["name"],
            "suhu": round(r["main"]["temp"]),
            "feels": round(r["main"]["feels_like"]),
            "cuaca": r["weather"][0]["description"],
            "kelembapan": r["main"]["humidity"],
            "angin": r["wind"]["speed"],
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/berita")
async def berita(sumber: str = "detik"):
    """Berita dari sumber."""
    try:
        import requests
        from bs4 import BeautifulSoup
        urls = {
            "detik": "https://www.detik.com/terpopuler",
            "kompas": "https://www.kompas.com/",
            "cnn": "https://www.cnnindonesia.com/",
            "tempo": "https://www.tempo.co/",
        }
        url = urls.get(sumber, urls["detik"])
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        berita_list = []
        seen = set()
        for a in soup.find_all("a", href=True):
            judul = a.get_text(strip=True)
            link = a["href"]
            if judul and len(judul) > 30 and link.startswith("http") and judul not in seen:
                seen.add(judul)
                berita_list.append({"judul": judul[:120], "link": link})
            if len(berita_list) >= 10:
                break
        return {"sumber": sumber, "berita": berita_list}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/saham")
async def saham(kode: str = "BBCA.JK"):
    """Harga saham."""
    try:
        import requests
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{kode.upper()}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10).json()
        meta = r["chart"]["result"][0]["meta"]
        harga = meta["regularMarketPrice"]
        prev = meta.get("previousClose", harga)
        perubahan = harga - prev
        persen = (perubahan / prev) * 100 if prev else 0
        return {
            "kode": meta.get("symbol", kode),
            "harga": harga,
            "prev": prev,
            "perubahan": perubahan,
            "persen": persen,
            "naik": perubahan > 0,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/kurs")
async def kurs():
    """Kurs mata uang."""
    try:
        import requests
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=10).json()
        rates = r["rates"]
        idr = rates.get("IDR", 0)
        hasil = {"USD": idr}
        for mata in ["EUR", "GBP", "JPY", "SGD", "MYR", "CNY"]:
            if mata in rates:
                hasil[mata] = idr / rates[mata]
        return hasil
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/log")
async def get_log():
    """Log aktivitas."""
    rows = core.db_exec("SELECT aksi, waktu FROM log_aksi ORDER BY id DESC LIMIT 20")
    return {"log": [{"aksi": a, "waktu": w[:19]} for a, w in rows]}


@app.get("/api/grafik")
async def grafik():
    """Grafik habit dari log."""
    rows = core.db_exec(
        "SELECT substr(waktu, 1, 13) as jam, COUNT(*) FROM log_aksi GROUP BY jam ORDER BY jam DESC LIMIT 12"
    )
    return {"grafik": [{"jam": j, "count": c} for j, c in rows]}
