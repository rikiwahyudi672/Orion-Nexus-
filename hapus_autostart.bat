@echo off
REM hapus_autostart.bat -- Cabut Orion dari Task Scheduler.
schtasks /delete /tn "OrionHidup" /f
if %errorlevel%==0 (
  echo OK: autostart Orion dicabut.
) else (
  echo Task OrionHidup tidak ditemukan (mungkin belum pernah didaftar).
)
echo.
pause
