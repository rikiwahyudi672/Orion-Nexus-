@echo off
REM ORION - Windows Terminal Edition
REM Tampilan modern: font Cascadia, warna, tab

chcp 65001 >nul

REM Jalankan via Windows Terminal
wt.exe ^
    --title "ORION" ^
    --suppressApplicationTitle ^
    -p "PowerShell" ^
    -d "E:\Project Software\Orion" ^
    cmd /k "chcp 65001 >nul && color 0D && python orion.py"

exit
