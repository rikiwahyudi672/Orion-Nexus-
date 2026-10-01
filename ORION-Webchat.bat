@echo off
REM ============================================================
REM  ORION Webchat Launcher — double-click aja, ga perlu ketik.
REM  - Buka Windows Terminal, jalanin server ORION
REM  - Otomatis buka browser ke webchat (http://127.0.0.1:8001)
REM  Matikan server: Ctrl+C di jendela Terminal, atau tutup jendelanya.
REM ============================================================

where wt >nul 2>nul
if errorlevel 1 (
    REM Windows Terminal (wt) tidak ketemu -> fallback ke cmd biasa
    start "" cmd /k "cd /d E:\Project Software\Orion && python orion_webchat.py"
) else (
    start "" wt cmd /k "cd /d E:\Project Software\Orion && python orion_webchat.py"
)

REM Tunggu server naik (5 detik), lalu buka webchat di browser.
REM Hapus 2 baris di bawah ini kalau tidak mau browser auto-kebuka.
timeout /t 5 /nobreak >nul
start http://127.0.0.1:8001
