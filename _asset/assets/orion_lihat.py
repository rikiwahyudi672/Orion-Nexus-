#!/usr/bin/env python3
"""
orion_lihat.py — kasih ORION kemampuan "melihat" gambar via GLM vision.

Cara pakai:
    python orion_lihat.py <path_gambar> [pertanyaan]

Contoh:
    python orion_lihat.py _asset\\avatar_orion.png "deskripsikan gambar ini"

Butuh API key Zhipu/GLM di environment variable:
    GLM_API_KEY  atau  ZHIPU_API_KEY
Model default: glm-4v-flash (gratis).
"""

import base64
import mimetypes
import os
import sys

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = os.environ.get("GLM_VISION_MODEL", "glm-4v-flash")


def cari_api_key():
    for nama in ("GLM_API_KEY", "ZHIPU_API_KEY"):
        key = os.environ.get(nama)
        if key:
            return key, nama
    return None, None


def encode_gambar(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    mime, _ = mimetypes.guess_type(path)
    return "data:%s;base64,%s" % (mime or "image/png", data)


def lihat(path_gambar, pertanyaan="Deskripsikan gambar ini dengan detail."):
    key, nama_env = cari_api_key()
    if not key:
        return ("ERR: API key GLM tidak ketemu.\n"
                "Set dulu salah satunya sebelum jalanin:\n"
                '  PowerShell (sesi ini aja): $env:GLM_API_KEY="isi_key_kamu"\n'
                '  Permanen: [Environment]::SetEnvironmentVariable("GLM_API_KEY","isi_key_kamu","User")')
    if not os.path.isfile(path_gambar):
        return "ERR: file tidak ketemu: %s" % path_gambar

    try:
        import requests
    except ImportError:
        return "ERR: butuh library 'requests'. Install dulu:  pip install requests"

    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": pertanyaan},
                {"type": "image_url", "image_url": {"url": encode_gambar(path_gambar)}},
            ],
        }],
        "max_tokens": 1024,
    }
    try:
        r = requests.post(API_URL,
                          headers={"Authorization": "Bearer " + key},
                          json=payload, timeout=60)
    except Exception as e:
        return "ERR: gagal konek ke API GLM: %s" % e
    if r.status_code != 200:
        return "ERR: API balas %s: %s" % (r.status_code, r.text[:300])
    try:
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "ERR: respon API aneh: %s\n%s" % (e, r.text[:300])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    tanya = sys.argv[2] if len(sys.argv) > 2 else "Deskripsikan gambar ini dengan detail."
    print(lihat(path, tanya))
