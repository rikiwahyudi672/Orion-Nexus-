---
name: cek-sistem
description: Cek sistem - CPU, RAM, disk, proses, jaringan.
version: 1.0.0
author: Riki Wahyudi
---

﻿# Skill: Cek Sistem

## Kapan dipakai
User bilang: "cek sistem", "status PC", "gimana PC-ku", "health check".

## Langkah
1. CPU: psutil.cpu_percent(interval=1)
2. RAM: psutil.virtual_memory() -> persen terpakai
3. Disk C: psutil.disk_usage("C:")
4. Disk E: psutil.disk_usage("E:")
5. Format jadi tabel 2 kolom: Komponen | Nilai

## Catatan
Kalau CPU > 80% -> tambahkan warning "CPU tinggi, cek Task Manager."
