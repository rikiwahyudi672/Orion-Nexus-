import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

# Hapus task gagal lama
conn.execute("DELETE FROM agent_tasks WHERE status='gagal'")

# Reset counter agent
conn.execute("UPDATE agents SET total_task=0, total_sukses=0, total_gagal=0")

conn.commit()
print("OK. Data lama dibersihin.")
print()
for r in conn.execute("SELECT nama, model, total_task, total_sukses FROM agents ORDER BY prioritas"):
    print(f"  {r[0]:10} | {r[1]:20} | task: {r[2]} | OK: {r[3]}")
conn.close()
