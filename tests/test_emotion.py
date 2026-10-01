import emotion_orion as E
import time

print("=" * 60)
print("SIMULASI EMOTIONAL STATE ORION")
print("=" * 60)
print()

# Reset dulu
import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
conn.execute("UPDATE emotion_state SET primary_emosi='kalem', primary_intensity=5, secondary_emosi=NULL, secondary_intensity=0 WHERE id=1")
conn.execute("DELETE FROM mood_events")
conn.commit()
conn.close()

print("[1] State awal:")
print("   ", E.get_emotion())
print()

print("[2] Kamu puji Orion 3x:")
for i in range(3):
    E.catat_event("dipuji", f"Pujian {i+1}")
print("   Emosi:", E.get_emotion())
print("   Relasi:", E.get_relationship())
print()

print("[3] Kamu marahin Orion:")
E.catat_event("dimarahin", "Riki marahin Orion")
print("   Emosi:", E.get_emotion())
print("   Relasi:", E.get_relationship())
print()

print("[4] Kamu tinggalin 30 menit:")
E.catat_event("ditinggal", "Riki lama nggak balik")
print("   Emosi:", E.get_emotion())
print()

print("[5] Event terakhir:")
for ev in E.event_terakhir(5):
    print("   ", ev)
print()

print("[6] Prompt modifier (buat LLM):")
print(E.prompt_modifier())
