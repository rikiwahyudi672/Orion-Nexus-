---
name: display-cyan-message
description: Menampilkan teks berwarna cyan di PowerShell untuk menyoroti informasi penting 😊
version: 1.0.0
author: Orion
---

# Menampilkan Pesan Cyan di PowerShell

## Kapan Digunakan
- Saat ingin menyoroti informasi penting di terminal
- Saat membuat skrip CLI dengan output berwarna

## Prosedur
1. Buka PowerShell atau file skrip `.ps1`.
2. Tulis perintah `Write-Host "=== Cari fungsi chat di dashboard CLI ===" -ForegroundColor Cyan`.
3. Jalankan skrip atau perintah tersebut untuk melihat teks berwarna cyan di layar.

## Contoh
**Query:**  
```powershell
Write-Host "=== Cari fungsi chat di dashboard CLI ===" -ForegroundColor Cyan
```

**Hasil:**  
Teks `=== Cari fungsi chat di dashboard CLI ===` muncul dengan warna cyan di konsol.