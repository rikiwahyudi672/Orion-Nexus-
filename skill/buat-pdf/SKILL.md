---
name: buat-pdf
description: Digunakan saat user meminta pembuatan dokumen PDF baru dari teks, panduan, atau laporan menggunakan ReportLab.
version: 1.0.0
author: Orion
---

# Pembuatan Dokumen PDF

## Kapan Digunakan
- User meminta membuat atau generate file PDF baru.
- Menyimpan panduan, catatan, atau laporan ke dalam format `.pdf`.
- Menyimpan dokumen PDF pada path atau direktori lokal tertentu.

## Prosedur
1. Identifikasi struktur konten teks yang diminta dan tentukan path direktori output.
2. Susun script Python menggunakan pustaka `reportlab` (`SimpleDocTemplate`, `Paragraph`, `Spacer`).
3. Eksekusi build dokumen untuk menghasilkan file PDF pada direktori tujuan yang diminta.

## Contoh
- Query: "buat pdf isinya cara shutdown orion terus simpen di folder c luar yon"
- Hasil: File PDF berisi tata cara shutdown berhasil dibuat dan disimpan di `C:/cara_shutdown_orion.pdf`.