import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
print("=== Agents ===")
for r in conn.execute("SELECT nama, provider, model, api_key_env, base_url FROM agents ORDER BY prioritas"):
    print(f"  {r[0]:10} | {r[1]:10} | {r[2]:20} | {r[3]}")
print()
print("=== Task Terakhir ===")
for r in conn.execute("SELECT agent_nama, status, error FROM agent_tasks ORDER BY created_at DESC LIMIT 5"):
    print(f"  {r[0]:10} | {r[1]:8} | {(r[2] or '')[:80]}")
conn.close()
