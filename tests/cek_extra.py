import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))
print("Empati log:")
for r in conn.execute("SELECT mood_user, intensitas, teks FROM empathy_log ORDER BY created_at DESC LIMIT 5"):
    print(f"  {r[0]:10} ({r[1]}) | {r[2][:50]}")
print()
print("Jokes:")
for r in conn.execute("SELECT trigger, punchline, hitung FROM jokes ORDER BY hitung DESC"):
    print(f"  '{r[0]}' -> {r[1]} ({r[2]}x)")
print()
print("Dreams:")
for r in conn.execute("SELECT isi FROM dreams ORDER BY created_at DESC LIMIT 3"):
    print(f"  {r[0]}")
conn.close()
