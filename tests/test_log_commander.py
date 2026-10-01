import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

print("=" * 60)
print("LOG COMMANDER")
print("=" * 60)
print()

print("=== 5 Commander Log Terakhir ===")
rows = conn.execute("SELECT perintah, agents_dipakai, durasi_total_ms, created_at FROM commander_log ORDER BY created_at DESC LIMIT 5").fetchall()
if rows:
    for r in rows:
        print(f"  [{r[3][:19]}]")
        print(f"    Perintah : {r[0][:80]}")
        print(f"    Agents   : {r[1]}")
        print(f"    Durasi   : {r[2]}ms")
        print()
else:
    print("  (belum ada)")
print()

print("=== 10 Agent Task Terakhir ===")
rows = conn.execute("SELECT agent_nama, status, durasi_ms, created_at FROM agent_tasks ORDER BY created_at DESC LIMIT 10").fetchall()
if rows:
    for r in rows:
        print(f"  [{r[3][:19]}] {r[0]:10} | {r[1]:8} | {r[2]}ms")
else:
    print("  (belum ada)")
print()

print("=== Statistik Agent ===")
rows = conn.execute("SELECT nama, model, total_task, total_sukses, total_gagal FROM agents ORDER BY prioritas").fetchall()
for r in rows:
    print(f"  {r[0]:10} | {r[1]:20} | task: {r[2]:3} | OK: {r[3]:3} | gagal: {r[4]:3}")
print()

conn.close()
print("=" * 60)
