import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

# Hapus agent flash47 (yang pakai glm-4.7-flash)
conn.execute("DELETE FROM agents WHERE model LIKE 'glm-4.7%' OR nama='flash47'")

# Kalau ada agent 'coding' yang ke-set ke glm-4.7, balikin ke glm-5.3-flash
conn.execute("""
    UPDATE agents 
    SET model='glm-5.3-flash'
    WHERE model LIKE 'glm-4.7%'
""")

conn.commit()
print("OK. Model GLM-4.7 dihapus dari agent.")
print()
print("=== Agents Sekarang ===")
for r in conn.execute("SELECT nama, provider, model, api_key_env, prioritas FROM agents ORDER BY prioritas"):
    print(f"  [{r[4]}] {r[0]:12} | {r[1]:10} | {r[2]:20} | {r[3]}")
conn.close()
