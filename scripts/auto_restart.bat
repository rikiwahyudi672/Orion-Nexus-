@echo off
title Orion Background
cd /d "E:\Project Software\Orion"

:loop
echo [%date% %time%] Orion start... >> "logs\auto_restart.log"
python orion.py
echo [%date% %time%] Orion mati. Restart 5 detik... >> "logs\auto_restart.log"
timeout /t 5 /nobreak >nul
goto loop
