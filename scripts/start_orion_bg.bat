@echo off
title Orion Background
cd /d "E:\Project Software\Orion"

:loop
echo [%date% %time%] Orion BG start... >> "logs\orion_bg.log"
python orion_background.py >> "logs\orion_bg_output.log" 2>&1
echo [%date% %time%] Orion BG mati. Restart 5 detik... >> "logs\orion_bg.log"
timeout /t 5 /nobreak >nul
goto loop
