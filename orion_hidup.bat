@echo off
REM orion_hidup.bat -- Nyalakan jantung Orion (minimized).
REM Taruh di folder utama Orion, sejajar dengan orion_hidup.py
cd /d "%~dp0"
start /min "" py -3 orion_hidup.py
