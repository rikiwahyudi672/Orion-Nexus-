---
name: reminder
description: Reminder - ingatkan Riki tugas, janji, agenda.
version: 1.0.0
author: Riki Wahyudi
---

﻿# Skill: Reminder

## Kapan dipakai
User bilang: "ingetin aku", "reminder", "jangan lupa".

## Langkah
1. Parse waktu dari kalimat user (jam, tanggal, "besok", "5 menit lagi").
2. Simpan ke tabel reminder di orion.db:
   CREATE TABLE IF NOT EXISTS reminder (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       isi TEXT,
       waktu TIMESTAMP,
       selesai INTEGER DEFAULT 0
   );
3. Konfirmasi ke user: "Oke, diingetin jam HH:MM."
4. Background loop cek tiap 30 detik, kalau waktunya -> notif plyer + TTS.

## Format Konfirmasi
"Oke, diingetin [isi] jam [HH:MM] tanggal [DD/MM]."
