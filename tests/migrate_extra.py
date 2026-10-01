import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
conn.executescript("""
CREATE TABLE IF NOT EXISTS hobi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    alasan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mimpi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS playlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT,
    artis TEXT,
    mood TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT,
    detail TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()
print("OK. 4 tabel baru.")
conn.close()
