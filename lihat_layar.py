"""lihat_layar.py -- Mata ORION: motret layar SEKALI, jelaskan isinya pakai AI vision.

Dipakai sebagai tool ORION: lihat_layar(pertanyaan="ada error apa di layar ini?")
- Screenshot sekali via PIL.ImageGrab (fallback: pyautogui).
- Gambar dikirim ke model vision: utama qwen/qwen3.8-27b via Groq
  (model vision resmi Groq per dokumentasinya; Llama 4 sudah dipensiunkan),
  cadangan Llama 4 Scout/Maverick via NVIDIA.
- API key diambil dari env GROQ_API_KEY / NVIDIA_API_KEY (atau .env di folder
  yang sama).
- Screenshot terakhir disimpan ke output/lihat_layar_terakhir.png biar bisa dicek
  Riki ("nyata/bukan halu").
- Tidak pernah mencetak API key ke output/log.
"""

import base64
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Kandidat (base_url, nama_key, model) dicoba berurutan.
# Groq mempensiunkan Llama 4 Scout (17 Jul 2026) & Maverick (9 Mar 2026);
# model vision resmi di Groq sekarang: qwen/qwen3.8-27b (per console.groq.com/docs/vision).
# NVIDIA masih hosting Llama 4 Scout/Maverick sebagai pintu cadangan.
_KANDIDAT = [
    ("https://api.groq.com/openai/v1/chat/completions", "GROQ_API_KEY",
     "qwen/qwen3.8-27b"),
    ("https://integrate.api.nvidia.com/v1/chat/completions", "NVIDIA_API_KEY",
     "meta/llama-4-scout-17b-16e-instruct"),
    ("https://integrate.api.nvidia.com/v1/chat/completions", "NVIDIA_API_KEY",
     "meta/llama-4-maverick-17b-128e-instruct"),
]


def _ambil_key(nama):
    key = os.environ.get(nama, "").strip()
    if key:
        return key
    env = ROOT / ".env"
    if env.is_file():
        for baris in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            b = baris.strip()
            if b.startswith(nama + "="):
                return b.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _screenshot():
    try:
        from PIL import ImageGrab

        return ImageGrab.grab()
    except Exception:
        pass
    try:
        import pyautogui

        return pyautogui.screenshot()
    except Exception:
        return None


def _kecilkan(img, maks=1600):
    w, h = img.size
    if max(w, h) > maks:
        skala = maks / max(w, h)
        img = img.resize((int(w * skala), int(h * skala)))
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


def lihat_layar(
    pertanyaan="Jelaskan apa yang terlihat di layar ini dengan bahasa Indonesia yang santai dan jelas."
):
    """Tool ORION: motret layar sekali lalu menjelaskan isinya."""
    key_groq = _ambil_key("GROQ_API_KEY")
    key_nvidia = _ambil_key("NVIDIA_API_KEY")
    if not key_groq and not key_nvidia:
        return (
            "[lihat_layar] GROQ_API_KEY / NVIDIA_API_KEY tidak ketemu "
            "di environment / .env, jadi aku belum bisa melihat."
        )
    img = _screenshot()
    if img is None:
        return (
            "[lihat_layar] Gagal motret layar (Pillow/pyautogui tidak ada). "
            "Install: pip install pillow"
        )
    try:
        outdir = ROOT / "output"
        outdir.mkdir(exist_ok=True)
        img.save(outdir / "lihat_layar_terakhir.png")
    except Exception:
        pass

    b64 = base64.b64encode(_kecilkan(img)).decode("ascii")

    gagal = []
    for base_url, nama_key, model in _KANDIDAT:
        key = key_groq if nama_key == "GROQ_API_KEY" else key_nvidia
        if not key:
            continue
        payload = {
            "model": model,
            "max_tokens": 1024,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": pertanyaan},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64," + b64
                            },
                        },
                    ],
                }
            ],
        }
        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                # Cloudflare (error 1010) ngeblok user-agent bawaan Python,
                # jadi samarin sebagai browser biasa.
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            # Baca pesan asli server buat diagnosa (jangan cuma "HTTP 403").
            try:
                body = e.read().decode("utf-8", errors="ignore")[:300]
                detail = json.loads(body).get("error", {}).get("message", body)
            except Exception:
                detail = body if body else "HTTP %s" % e.code
            gagal.append("[%s] %s" % (model, detail))
        except Exception as e:  # noqa: BLE001 - pesan error perlu sampai ke ORION
            gagal.append("[%s] %s" % (model, e))
    return "[lihat_layar] Gagal menghubungi AI vision:\n" + "\n".join(gagal)


def main():
    import sys

    tanya = " ".join(sys.argv[1:]) or "Jelaskan apa yang terlihat di layar ini."
    print(lihat_layar(tanya))


if __name__ == "__main__":
    main()
