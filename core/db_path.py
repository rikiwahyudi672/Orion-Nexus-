"""Helper - path database Orion."""

from pathlib import Path
import sqlite3

_BASE = Path(__file__).parent.parent

DB_PATH = _BASE / "memory" / "orion.db"

if not DB_PATH.exists():
    for _p in [_BASE / "memory" / "orion.db", _BASE / "orion.db"]:
        if _p.exists():
            DB_PATH = _p
            break


def get_db_path():
    return str(DB_PATH)


def get_conn():
    return sqlite3.connect(str(DB_PATH))
