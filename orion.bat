@echo off
title ORION - Command Center
color 0B
:menu
cls
echo.
echo ============================================================
echo   ORION - COMMAND CENTER
echo ============================================================
echo.
echo   [1] Cek Kesehatan
echo   [2] Evolve + Learn (1 klik)
echo   [3] Learn - Analisa Pola
echo   [4] Improve - Rekomendasi
echo   [5] Report - Laporan Mingguan
echo   [6] Build Manifest
echo   [7] Monitor (5 menit)
echo   [8] Auto Evolve (loop 1 jam)
echo   [9] Test Notif Windows
echo   [T] Tool Loop (skill otomatis)
echo   [0] Keluar
echo.
echo ============================================================
set /p pilih="  Pilih [0-9]: "

if "%pilih%"=="1" python orion_health.py & pause & goto menu
if "%pilih%"=="2" python orion_evolve_v3.py & pause & goto menu
if "%pilih%"=="3" python orion_learn.py & pause & goto menu
if "%pilih%"=="4" python orion_improve.py & pause & goto menu
if "%pilih%"=="5" python orion_report.py & pause & goto menu
if "%pilih%"=="6" python orion_build_manifest.py & pause & goto menu
if "%pilih%"=="7" python orion_monitor.py & pause & goto menu
if "%pilih%"=="8" python orion_auto.py & pause & goto menu
if "%pilih%"=="9" python orion_alert.py & pause & goto menu
if /i "%pilih%"=="T" python orion_tool_loop.py & pause & goto menu
if "%pilih%"=="0" exit

goto menu
