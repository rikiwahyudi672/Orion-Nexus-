import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
conn.execute("UPDATE agents SET provider='mortera', model='glm-5.3-flash', base_url='https://mortera.cloud/v1', api_key_env='MORTERA_API_KEY' WHERE nama='analis'")
conn.commit()
print("OK. Agent 'analis' diganti ke Mortera.")
for r in conn.execute("SELECT nama, provider, model FROM agents ORDER BY prioritas"):
    print(f"  {r[0]:10} | {r[1]:10} | {r[2]}")
conn.close()
