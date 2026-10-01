# CHEATSHEET

## Python
python -c "from orion_hub import lapor_diri; lapor_diri()"
python -c "from orion_hub import proses; proses('halo')"

## Cek
where.exe python
Get-Process python*
Get-ChildItem -Directory

## DB
python -c "import sqlite3; c=sqlite3.connect('orion.db'); print([r[0] for r in c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')])"
