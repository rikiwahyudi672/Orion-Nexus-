import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

# Tambah / update agent coding
# Pakai model yang biasanya kuat buat coding di Mortera
conn.execute("""
    INSERT OR REPLACE INTO agents 
    (nama, provider, model, base_url, api_key_env, capabilities, prioritas, aktif)
    VALUES 
    ('coding', 'mortera', 'glm-5.3-flash', 'https://mortera.cloud/v1', 'MORTERA_API_KEY',
     'coding,debug,review,refactor,arsitektur', 3, 1)
""")

# Tambah agent coding spesialis (opsional)
conn.execute("""
    INSERT OR REPLACE INTO agents 
    (nama, provider, model, base_url, api_key_env, capabilities, prioritas, aktif)
    VALUES 
    ('coding_pro', 'mortera', 'glm-5.3', 'https://mortera.cloud/v1', 'MORTERA_API_KEY',
     'coding-advanced,arsitektur,optimasi,security', 6, 1)
""")

conn.commit()
print("OK. Agent coding ditambahkan.")
print()
for r in conn.execute("SELECT nama, provider, model, capabilities, prioritas FROM agents ORDER BY prioritas"):
    print(f"  [{r[4]}] {r[0]:12} | {r[1]:10} | {r[2]:20} | {r[3]}")
conn.close()
