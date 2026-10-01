"""web_dashboard.py - Web Dashboard ORION versi catchy"""
import sys
import os
import base64
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
import core

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="ORION Dashboard")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# Baca logo orion.ico → base64
LOGO_PATH = Path(core.P["base"]) / "orion.ico"
if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode()
    LOGO_SRC = f"data:image/x-icon;base64,{LOGO_B64}"
else:
    LOGO_SRC = ""


HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⭐ ORION Dashboard</title>
<link rel="icon" href="LOGO_SRC_PLACEHOLDER">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: #050816;
    color: #e0e6ff;
    min-height: 100vh;
    padding: 20px;
    overflow-x: hidden;
    position: relative;
}

/* Background animasi bintang */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(2px 2px at 20% 30%, #64b5f6, transparent),
        radial-gradient(2px 2px at 60% 70%, #9575cd, transparent),
        radial-gradient(1px 1px at 50% 50%, #fff, transparent),
        radial-gradient(1px 1px at 80% 10%, #64b5f6, transparent),
        radial-gradient(2px 2px at 90% 60%, #9575cd, transparent),
        radial-gradient(1px 1px at 33% 80%, #fff, transparent),
        radial-gradient(1px 1px at 10% 90%, #64b5f6, transparent);
    background-size: 200% 200%;
    animation: stars 60s linear infinite;
    z-index: -1;
    opacity: 0.6;
}

@keyframes stars {
    from { background-position: 0 0; }
    to { background-position: 100% 100%; }
}

.header {
    text-align: center;
    padding: 30px 20px;
    animation: fadeInDown 0.8s ease-out;
}

.logo {
    width: 100px;
    height: 100px;
    margin-bottom: 15px;
    animation: pulse 3s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(100, 181, 246, 0.8));
}

@keyframes pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(100, 181, 246, 0.8)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 35px rgba(100, 181, 246, 1)); }
}

.title {
    font-size: 3em;
    font-weight: 800;
    letter-spacing: 12px;
    background: linear-gradient(90deg, #64b5f6, #9575cd, #64b5f6);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 3s linear infinite;
}

@keyframes shine {
    to { background-position: 200% center; }
}

.subtitle {
    color: #90a4ae;
    margin-top: 8px;
    font-size: 0.95em;
    letter-spacing: 2px;
}

/* Status bar */
.status-bar {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin: 25px 0;
}

.status-card {
    background: rgba(20, 30, 60, 0.7);
    border: 1px solid rgba(100, 181, 246, 0.3);
    border-radius: 14px;
    padding: 15px 22px;
    min-width: 110px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s;
    animation: fadeIn 0.6s ease-out backwards;
}

.status-card:hover {
    border-color: #64b5f6;
    box-shadow: 0 0 20px rgba(100, 181, 246, 0.4);
    transform: translateY(-3px);
}

.status-card .label {
    font-size: 0.7em;
    color: #90a4ae;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 5px;
}

.status-card .value {
    font-size: 1.6em;
    color: #64b5f6;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}

/* Grid tombol */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 15px;
    max-width: 1100px;
    margin: 0 auto;
    animation: fadeInUp 0.8s ease-out;
}

.card {
    background: linear-gradient(135deg, rgba(30, 40, 70, 0.8), rgba(20, 30, 60, 0.8));
    border: 1px solid rgba(100, 181, 246, 0.25);
    border-radius: 16px;
    padding: 22px 18px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(100, 181, 246, 0.2), transparent);
    transition: left 0.5s;
}

.card:hover::before { left: 100%; }

.card:hover {
    background: linear-gradient(135deg, rgba(50, 70, 120, 0.9), rgba(40, 60, 110, 0.9));
    border-color: #64b5f6;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px rgba(100, 181, 246, 0.4);
}

.card:active { transform: translateY(-2px) scale(0.98); }

.card .icon {
    font-size: 2.2em;
    margin-bottom: 10px;
    display: block;
    transition: transform 0.3s;
}

.card:hover .icon { transform: scale(1.2) rotate(-5deg); }

.card .title {
    font-size: 1em;
    color: #e0e6ff;
    font-weight: 600;
    letter-spacing: 1px;
}

.card .desc {
    font-size: 0.75em;
    color: #78909c;
    margin-top: 4px;
}

/* Toast */
.toast {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: linear-gradient(135deg, #64b5f6, #9575cd);
    color: #fff;
    padding: 14px 28px;
    border-radius: 50px;
    font-weight: 600;
    box-shadow: 0 10px 40px rgba(100, 181, 246, 0.5);
    opacity: 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
    z-index: 1000;
    letter-spacing: 1px;
}

.toast.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* Preview screenshot */
.preview-container {
    max-width: 900px;
    margin: 25px auto;
    display: none;
    animation: fadeInUp 0.5s ease-out;
}

.preview-container.show { display: block; }

.preview-container img {
    width: 100%;
    border-radius: 16px;
    border: 2px solid #64b5f6;
    box-shadow: 0 20px 60px rgba(100, 181, 246, 0.4);
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 40px;
    color: #546e7a;
    font-size: 0.85em;
    letter-spacing: 1px;
    animation: fadeIn 1s ease-out;
}

.footer .clock {
    color: #64b5f6;
    font-weight: 600;
}

/* Animasi */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mobile */
@media (max-width: 600px) {
    .title { font-size: 2em; letter-spacing: 6px; }
    .logo { width: 70px; height: 70px; }
    .status-card { padding: 12px 16px; min-width: 90px; }
    .status-card .value { font-size: 1.3em; }
    .grid { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }
    .card { padding: 16px 12px; }
    .card .icon { font-size: 1.8em; }
}
</style>
</head>
<body>

<div class="header">
    <img class="logo" src="LOGO_SRC_PLACEHOLDER" alt="ORION">
    <div class="title">ORION</div>
    <div class="subtitle">PERSONAL AI ASSISTANT</div>
</div>

<div class="status-bar">
    <div class="status-card">
        <div class="label">CPU</div>
        <div class="value" id="cpu">--%</div>
    </div>
    <div class="status-card">
        <div class="label">RAM</div>
        <div class="value" id="ram">--%</div>
    </div>
    <div class="status-card">
        <div class="label">Disk</div>
        <div class="value" id="disk">--%</div>
    </div>
    <div class="status-card">
        <div class="label">Baterai</div>
        <div class="value" id="baterai">--%</div>
    </div>
</div>

<div class="grid">
    <div class="card" onclick="aksi('screenshot')">
        <span class="icon">📸</span>
        <div class="title">Screenshot</div>
        <div class="desc">Ambil layar PC</div>
    </div>
    <div class="card" onclick="aksi('notepad')">
        <span class="icon">💻</span>
        <div class="title">Notepad</div>
        <div class="desc">Buka notepad</div>
    </div>
    <div class="card" onclick="aksi('calc')">
        <span class="icon">🧮</span>
        <div class="title">Calculator</div>
        <div class="desc">Buka kalkulator</div>
    </div>
    <div class="card" onclick="aksi('browser')">
        <span class="icon">🌐</span>
        <div class="title">Browser</div>
        <div class="desc">Buka Google</div>
    </div>
    <div class="card" onclick="aksi('volume_up')">
        <span class="icon">🔊</span>
        <div class="title">Volume +</div>
        <div class="desc">Naikin volume</div>
    </div>
    <div class="card" onclick="aksi('volume_down')">
        <span class="icon">🔉</span>
        <div class="title">Volume -</div>
        <div class="desc">Turunin volume</div>
    </div>
    <div class="card" onclick="aksi('brightness_up')">
        <span class="icon">☀️</span>
        <div class="title">Brightness +</div>
        <div class="desc">Naikin kecerahan</div>
    </div>
    <div class="card" onclick="aksi('brightness_down')">
        <span class="icon">🌙</span>
        <div class="title">Brightness -</div>
        <div class="desc">Turunin kecerahan</div>
    </div>
    <div class="card" onclick="prediksi()">
        <span class="icon">🔮</span>
        <div class="title">Prediksi AI</div>
        <div class="desc">Prediksi aktivitas</div>
    </div>
    <div class="card" onclick="aksi('lock')">
        <span class="icon">🔒</span>
        <div class="title">Lock PC</div>
        <div class="desc">Kunci layar</div>
    </div>
    <div class="card" onclick="aksi('sleep')">
        <span class="icon">😴</span>
        <div class="title">Sleep</div>
        <div class="desc">Mode tidur</div>
    </div>
    <div class="card" onclick="lihatLog()">
        <span class="icon">📋</span>
        <div class="title">Log</div>
        <div class="desc">Aktivitas terakhir</div>
    </div>
</div>

<div class="preview-container" id="previewContainer">
    <img id="preview" />
</div>

<div class="footer">
    ⭐ ORION v2.7 &nbsp;•&nbsp; by Riki Wahyudi &nbsp;•&nbsp; <span class="clock" id="clock"></span>
</div>

<div class="toast" id="toast"></div>

<script>
// Sound effect klik (Web Audio API)
function playBeep() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = 800;
        osc.type = 'sine';
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.1);
    } catch(e) {}
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2200);
}

async function aksi(cmd) {
    playBeep();
    try {
        const r = await fetch('/api/' + cmd, { method: 'POST' });
        const data = await r.json();
        if (cmd === 'screenshot' && data.file) {
            const img = document.getElementById('preview');
            const cont = document.getElementById('previewContainer');
            img.src = '/screenshot/' + data.file + '?t=' + Date.now();
            cont.classList.add('show');
        }
        showToast(data.message || 'OK');
    } catch(e) {
        showToast('Error: ' + e);
    }
}

async function prediksi() {
    playBeep();
    const jam = prompt('Jam berapa? (0-23)', new Date().getHours());
    if (jam === null) return;
    try {
        const r = await fetch('/api/prediksi?jam=' + jam, { method: 'POST' });
        const data = await r.json();
        showToast(data.message);
    } catch(e) {
        showToast('Error');
    }
}

async function lihatLog() {
    playBeep();
    try {
        const r = await fetch('/api/log');
        const data = await r.json();
        alert('Log 10 terakhir:\\n\\n' + data.log);
    } catch(e) {
        showToast('Error');
    }
}

async function updateStatus() {
    try {
        const r = await fetch('/api/status');
        const d = await r.json();
        document.getElementById('cpu').textContent = d.cpu + '%';
        document.getElementById('ram').textContent = d.ram + '%';
        document.getElementById('disk').textContent = d.disk + '%';
        document.getElementById('baterai').textContent = d.baterai + '%';
    } catch(e) {}
}

function updateClock() {
    const now = new Date();
    const opts = { weekday: 'long', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
    document.getElementById('clock').textContent = now.toLocaleString('id-ID', opts);
}

updateStatus();
updateClock();
setInterval(updateStatus, 3000);
setInterval(updateClock, 1000);
</script>
</body>
</html>
"""

# Ganti placeholder logo
HTML = HTML.replace("LOGO_SRC_PLACEHOLDER", LOGO_SRC)


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


@app.get("/api/status")
async def status():
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    bat = psutil.sensors_battery()
    return {"cpu": round(cpu), "ram": round(mem.percent), "disk": round(disk.percent), "baterai": round(bat.percent) if bat else 0}


@app.post("/api/screenshot")
async def screenshot():
    try:
        import pyautogui
        Path(core.P["output"]).mkdir(exist_ok=True)
        nama = f"web_shot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file = Path(core.P["output"]) / nama
        pyautogui.screenshot(str(file))
        core.catat(f"Web screenshot: {nama}")
        return {"message": "Screenshot diambil", "file": nama}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/screenshot/{nama}")
async def get_screenshot(nama: str):
    file = Path(core.P["output"]) / nama
    if not file.exists():
        raise HTTPException(404, "File tidak ditemukan")
    return FileResponse(file)


@app.post("/api/notepad")
async def notepad():
    subprocess.Popen("notepad", shell=True)
    core.catat("Web: notepad")
    return {"message": "Notepad dibuka di PC"}


@app.post("/api/calc")
async def calc():
    subprocess.Popen("calc", shell=True)
    core.catat("Web: calculator")
    return {"message": "Calculator dibuka"}


@app.post("/api/browser")
async def browser():
    webbrowser.open("https://google.com")
    core.catat("Web: browser")
    return {"message": "Browser dibuka"}


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


@app.post("/api/brightness_up")
async def brightness_up():
    try:
        import screen_brightness_control as sbc
        cur = sbc.get_brightness()[0]
        new = min(100, cur + 10)
        sbc.set_brightness(new)
        return {"message": f"Brightness: {new}%"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/brightness_down")
async def brightness_down():
    try:
        import screen_brightness_control as sbc
        cur = sbc.get_brightness()[0]
        new = max(0, cur - 10)
        sbc.set_brightness(new)
        return {"message": f"Brightness: {new}%"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/prediksi")
async def prediksi(jam: float = 8):
    try:
        otak = core.Otak()
        akt, conf = otak.prediksi(jam)
        if akt:
            core.catat(f"Web prediksi jam {jam}")
            return {"message": f"Jam {jam:.0f}:00 → {akt} ({conf*100:.0f}%)"}
        return {"message": "Model belum dilatih"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/lock")
async def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    core.catat("Web: lock")
    return {"message": "PC dikunci"}


@app.post("/api/sleep")
async def sleep():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return {"message": "PC tidur"}


@app.get("/api/log")
async def log():
    rows = core.db_exec("SELECT aksi, waktu FROM log_aksi ORDER BY id DESC LIMIT 10")
    if not rows:
        return {"log": "(kosong)"}
    lines = [f"{w[:19]} - {a}" for a, w in rows]
    return {"log": "\\n".join(lines)}


if __name__ == "__main__":
    core.init_db()
    print()
    print("=" * 60)
    print("  ⭐ ORION Web Dashboard")
    print("=" * 60)
    print()
    print("  Akses dari:")
    print("  - Laptop ini  : http://localhost:8000")
    print("  - HP / device : http://192.168.43.122:8000")
    print()
    print("=" * 60)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")