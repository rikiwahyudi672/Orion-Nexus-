@echo off
cd /d "E:\Project Software\Orion"
for /f "tokens=TARUH_TOKEN_DISCORD_DISINI,* delims==" %%a in ('findstr /b "DISCORD_TOKEN=TARUH_TOKEN_DISCORD_DISINI
python discord_voice_orion_v2.py
