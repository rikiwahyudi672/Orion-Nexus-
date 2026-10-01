---
name: refleksi-diri
description: Refleksi diri - evaluasi tindakan, perbaiki diri.
version: 1.0.0
author: Riki Wahyudi
---

﻿# Skill: Refleksi Diri

## Kapan dipakai
Setelah Orion menyelesaikan tugas berat, atau tiap 10 interaksi.

## Langkah
1. Tanya ke diri sendiri (di prompt LLM):
   - "Tadi aku ngapain?"
   - "Ada yang bisa diperbaiki?"
   - "Ada pelajaran yang layak disimpan?"
2. Kalau ada -> INSERT ke agent_memory dengan topik + isi + penting (0/1).
3. Kalau tidak ada -> skip, jangan sampahin DB.

## Aturan Memori
- Maksimal 200 karakter per memori.
- Cuma simpan yang benar-benar berguna.
- Jangan simpan: sapaan, obrolan ringan, hal yang sudah obvious.
