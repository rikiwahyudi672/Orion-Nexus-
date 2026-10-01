import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
# Hapus log yang kepotong
conn.execute("DELETE FROM empathy_log WHERE teks LIKE '%Kamu punya skill%' OR teks LIKE '%---%'")
conn.commit()
print("OK. Log kotor dihapus.")
for r in conn.execute("SELECT mood_user, intensitas, teks FROM empathy_log ORDER BY created_at DESC LIMIT 5"):
    print(f"  {r[0]:10} ({r[1]}) | {r[2][:60]}")
conn.close()
