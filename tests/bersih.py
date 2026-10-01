import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

# Hapus event test
conn.execute("DELETE FROM mood_events WHERE deskripsi IN ('test utc','Pujian 1','Pujian 2','Pujian 3','Riki marahin Orion','Riki lama nggak balik')")

# Reset relationship
conn.execute("UPDATE relationship SET trust=75, intimacy=55, total_dipuji=5, total_dimarahin=1, total_interaksi=0 WHERE id=1")

# Reset emotion
conn.execute("UPDATE emotion_state SET primary_emosi='kalem', primary_intensity=5, secondary_emosi=NULL, secondary_intensity=0, updated_at=CURRENT_TIMESTAMP WHERE id=1")

conn.commit()
print("OK. Data test dihapus.")
print()
print("Events tersisa:")
for r in conn.execute("SELECT event_type, deskripsi FROM mood_events ORDER BY created_at DESC LIMIT 10"):
    print(f"  {r[0]:15} | {r[1][:60]}")
print()
print("Relationship:", conn.execute("SELECT trust, intimacy, total_dipuji, total_dimarahin FROM relationship WHERE id=1").fetchone())
conn.close()
