---
name: kamera
description: Kamera realtime — deteksi wajah (10 FPS), foto, lihat kecerahan. Pakai Haarcascade.
version: 1.0.0
---

# Kamera Orion

Skill untuk akses kamera laptop Riki.

## Fungsi

- `lihat(durasi)` — Lihat kamera selama X detik
- `deteksi_wajah(durasi)` — Deteksi wajah (10 FPS)
- `foto()` — Ambil foto
- `info()` — Info kamera

## Model

- **Haarcascade** — deteksi wajah (10 FPS, ringan)
- **Face model LBPH** — kenali wajah (opsional)

## Performa

- **FPS**: 10.3
- **CPU**: 5-15%
- **RAM**: ~50 MB
- **Durasi**: Tanpa batas
