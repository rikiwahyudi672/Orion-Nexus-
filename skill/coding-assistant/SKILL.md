# coding-assistant

Tulis, baca, jalankan, dan perbaiki kode Python secara otomatis.

## Cara pakai (argumen untuk jalankan)

- `tulis:<path>:<kode>` — tulis kode ke file
- `baca:<path>` — baca isi file kode
- `run:<path>` — jalankan file Python (timeout 60 detik)
- `<goal bebas>` — mode otomatis: tulis kode, jalankan, cek error, fix sendiri

## Contoh

- `buatkan fungsi faktorial rekursif`
- `tulis:halo.py:print("halo")`
- `run:halo.py`

## Catatan

Skill ini adalah wrapper dari `coding/coding_assistant.py`.
