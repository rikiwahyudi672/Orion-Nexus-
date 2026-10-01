@echo off
REM =====================================================
REM  ORION HIDUP - Launcher jantung ORION
REM  Double-click untuk menyalakan. Jangan tutup jendelanya.
REM  (Nyalakan dari folder Orion supaya logs/ tidak nyasar)
REM =====================================================
title ORION HIDUP - JANTUNG (jangan ditutup)
cd /d "E:\Project Software\Orion"

echo Mematikan jantung lama (biar tidak dobel)...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*orion_hidup.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
timeout /t 2 /nobreak >nul

echo.
echo Menyalakan jantung ORION...
python "E:\Project Software\Orion\orion_hidup.py"

echo.
echo Jantung berhenti. Jendela boleh ditutup.
pause >nul
