import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

# Hapus semua agent lama
conn.execute("DELETE FROM agents")

# Daftar ulang - pakai model VALID
agents = [
    # (nama, model, capabilities, prioritas)
    ("cepat",   "glm-5.3-flash",    "cepat,ringan,murah,chat",         1),
    ("analis",  "gemini-3.7-flash", "analisis,riset,data,wikipedia",   2),
    ("koding",  "glm-5.3",          "coding,debug,refactor,review",    3),
    ("kreatif", "glm-5.2",          "kreatif,tulis,konten,humor",      4),
    ("umum",    "glm-5.3-flash",    "umum,chat,diskusi",               5),
]

for nama, model, caps, prio in agents:
    conn.execute("""
        INSERT INTO agents (nama, provider, model, base_url, api_key_env, capabilities, prioritas, aktif)
        VALUES (?, 'mortera', ?, 'https://mortera.cloud/v1', 'MORTERA_API_KEY', ?, ?, 1)
    """, (nama, model, caps, prio))

conn.commit()
print("OK. 5 agent didaftarkan.")
print()
for r in conn.execute("SELECT nama, model, capabilities, prioritas FROM agents ORDER BY prioritas"):
    print(f"  [{r[3]}] {r[0]:10} | {r[1]:20} | {r[2]}")
conn.close()
