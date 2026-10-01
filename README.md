# ORION v2.7 🌌 — Digital Lieutenant

Asisten AI pribadi Riki Wahyudi. Jalan lokal di Windows (Fujitsu MU937), otaknya pakai API, ingatannya punya sendiri.

> Personal project — dibangun dan dirawat satu orang dari kamar kos. Bukan produk, bukan AGI. Tapi dia kerja beneran.

## Fitur

- **Tool loop** — eksekusi perintah, baca/tulis file, kontrol jendela, screenshot + vision, dan lain-lain
- **Memori jangka panjang** — database SQLite (36 tabel): chat, pengalaman, fakta, mood, relasi
- **Emosi simulasi** — emotion + mood + decay yang memengaruhi gaya bicara
- **Voice** — text-to-speech bahasa Indonesia
- **Penjadwalan otonom** — cron scheduler (9 task harian: 08:00–03:00) + toast Windows
- **Inisiatif (weker)** — cek kondisi sistem tiap 5 menit, mulai percakapan sendiri kalau ada yang penting
- **Webchat** — UI chat browser dengan riwayat sesi permanen
- **Discord bot** — natural chat tanpa slash command
- **Multi-agent bridge** — delegasi ke tim AI lain (Nexus.ai / Jarvis + worker)
- **Self-awareness** — `tahu_diri()` / `lapor_diri()`: lapor kondisi modulnya sendiri

## Cara jalanin

```powershell
.\orion.bat
# atau
python orion.py
```

Channel lain:

| Channel | Cara jalanin |
|---------|--------------|
| Webchat | `python orion_webchat.py` → http://127.0.0.1:8001 |
| Discord | `run_discord.bat` |
| Voice | `voice_orion.py` |

Butuh API key di `.env`. **Jangan pernah commit `.env` asli** (lihat `.gitignore`).

## Struktur

```
orion.py / orion.bat     → entry point
orion_tool_loop.py       → jantung: tool loop + prompt berlapis
core/                    → otonomi: emosi, kesadaran, kontrol
memory/                  → memori file-based
support/                 → cron, supervisor, log
_data/md/                → dokumentasi (13 file, lihat bawah)
orion.db                 → database SQLite (36 tabel)
```

## Dokumentasi

Dokumentasi lengkap ada di `_data/md/`:

- `SOUL.md` — identitas & kepribadian
- `USER.md` — profil user
- `VALUES.md` — nilai: jujur, backup dulu, test dulu, konfirmasi
- `ARCHITECTURE.md` — modul, pipeline, database
- `SKILL.md` — daftar skill (24 terdaftar per 28/09)
- `ROUTINE.md` — jadwal cron harian
- `GOALS.md` — target proyek
- `PROJECTS.md` — status & rencana monetisasi
- `CHANGELOG.md` — riwayat versi
- `AKSES.md` — perintah & cara akses
- `CHEATSHEET.md`, `DISCORD_SETUP.md`

## Status

🚧 Active development — v2.7 (Oktober 2026)

Lagi dikerjain: weker inisiatif, stabilisasi webchat, QC harian.

Catatan: angka-angka di dokumentasi (`_data/md/`) ditulis bertahap sejak 27/09 — sebagian self-report. Angka yang sudah terverifikasi live dicatat di changelog commit.

## Nilai proyek

1. Jujur
2. Backup dulu
3. Test dulu
4. Konfirmasi sebelum aksi berisiko
5. Minimal intervensi
6. Belajar dari error
7. Loyal ke Riki

---

Dibangun dengan begadang oleh **Riki Wahyudi** (Nexus Corp). Lahir 26 September 2026.
