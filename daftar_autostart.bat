@echo off
REM daftar_autostart.bat -- Daftarkan Orion ke Task Scheduler Windows.
REM Efek: tiap kali login Windows, orion_hidup.bat jalan otomatis.
REM Klik kanan - Run as administrator kalau gagal.
set "TARGET=%~dp0orion_hidup.bat"
schtasks /create /tn "OrionHidup" /tr "\"%TARGET%\"" /sc onlogon /f
if %errorlevel%==0 (
  echo.
  echo OK: Orion akan otomatis nyala setiap kamu login Windows.
  echo Cek di Task Scheduler - Task Scheduler Library - OrionHidup
) else (
  echo.
  echo GAGAL. Klik kanan file ini - Run as administrator - coba lagi.
)
echo.
pause
