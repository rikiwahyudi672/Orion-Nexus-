"""web_v2/main.py - Main entry untuk web dashboard v2"""
import sys
from pathlib import Path

# Path setup
WEB_DIR = Path(__file__).parent
BASE_DIR = WEB_DIR.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(WEB_DIR))

from fastapi.responses import HTMLResponse
from api import app
from ui import get_html


@app.get("/", response_class=HTMLResponse)
async def root():
    return get_html()


@app.get("/health")
async def health():
    return {"status": "ok", "app": "ORION v3.0"}


def get_ip():
    """Detect IP lokal untuk akses dari HP."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    import uvicorn
    import os

    # Baca .env
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    host = os.environ.get("WEB_HOST", "0.0.0.0")
    port = int(os.environ.get("WEB_PORT", "8000"))
    ip = get_ip()

    print()
    print("=" * 60)
    print("  ⭐ ORION Web Dashboard v2")
    print("=" * 60)
    print()
    print("  Akses dari:")
    print(f"  - Laptop ini  : http://localhost:{port}")
    print(f"  - HP / device : http://{ip}:{port}")
    print()
    print("  Fitur:")
    print("  - Chat JARVIS (rule-based)")
    print("  - Voice chat (Whisper offline)")
    print("  - TTS (Edge-TTS)")
    print("  - Prediksi (Top-N, per hari)")
    print("  - Knowledge (fakta, catatan, reminder)")
    print("  - Auto-update backup")
    print()
    print("=" * 60)
    print("  Tekan Ctrl+C untuk stop")
    print("=" * 60)
    print()

    uvicorn.run(app, host=host, port=port, log_level="warning")