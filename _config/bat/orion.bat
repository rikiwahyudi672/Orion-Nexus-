@echo off
REM ORION - Launcher via Windows Terminal (PowerShell + Icon)

where wt.exe >nul 2>&1
if %errorlevel% == 0 (
    REM Pakai Windows Terminal dengan icon ORION
    wt.exe -w 0 new-tab --title "ORION" --tabColor "#7B2FF7" -d "E:\Project Software\Orion" --icon "E:\Project Software\Orion\orion_logo.ico" pwsh -NoExit -ExecutionPolicy Bypass -File "E:\Project Software\Orion\orion.ps1"
) else (
    REM Fallback: PowerShell klasik
    powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0orion.ps1"
)
