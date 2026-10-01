import sqlite3
conn = sqlite3.connect(str(BASE / "memory" / "orion.db"))

print("=" * 50)
print("STATUS ORION")
print("=" * 50)
print()

# Loyalty
print("LOYALTY:")
try:
    loy = conn.execute("SELECT skor, total_interaksi, total_hari FROM loyalty WHERE id=1").fetchone()
    print(f"  Skor       : {loy[0]}/100")
    print(f"  Interaksi  : {loy[1]}")
    print(f"  Hari kenal : {loy[2]}")
except Exception as e:
    print(f"  Error: {e}")
print()

# Emosi
print("EMOSI:")
try:
    emo = conn.execute("SELECT primary_emosi, primary_intensity, secondary_emosi, secondary_intensity FROM emotion_state WHERE id=1").fetchone()
    print(f"  Primary    : {emo[0]} ({emo[1]}/10)")
    print(f"  Secondary  : {emo[2]} ({emo[3]}/10)" if emo[2] else "  Secondary  : -")
except Exception as e:
    print(f"  Error: {e}")
print()

# Relationship
print("RELATIONSHIP:")
try:
    rel = conn.execute("SELECT trust, intimacy, respect, total_dipuji, total_dimarahin, total_interaksi FROM relationship WHERE id=1").fetchone()
    print(f"  Trust      : {rel[0]}/100")
    print(f"  Intimacy   : {rel[1]}/100")
    print(f"  Respect    : {rel[2]}/100")
    print(f"  Dipuji     : {rel[3]}x")
    print(f"  Dimarahin  : {rel[4]}x")
    print(f"  Interaksi  : {rel[5]}x")
except Exception as e:
    print(f"  Error: {e}")
print()

# Ancaman loyalitas
print("ANCAMAN LOYALITAS:")
try:
    rows = conn.execute("SELECT jenis, deskripsi, created_at FROM loyalty_threats ORDER BY created_at DESC LIMIT 5").fetchall()
    if rows:
        for r in rows:
            print(f"  [{r[0]:12}] {r[1][:50]}")
    else:
        print("  (belum ada)")
except Exception as e:
    print(f"  Error: {e}")
print()

# Event emosi
print("EVENT EMOSI TERAKHIR:")
try:
    rows = conn.execute("SELECT event_type, deskripsi FROM mood_events ORDER BY created_at DESC LIMIT 5").fetchall()
    if rows:
        for r in rows:
            print(f"  [{r[0]:12}] {r[1][:50]}")
    else:
        print("  (belum ada)")
except Exception as e:
    print(f"  Error: {e}")
print()

# Mood
print("MOOD:")
try:
    mood = conn.execute("SELECT mood FROM mood_state WHERE id=1").fetchone()
    print(f"  Mood       : {mood[0]}")
except Exception as e:
    print(f"  Error: {e}")
print()

# Skill
print("SKILL:")
try:
    from pathlib import Path
    skills = list(Path("skills").glob("*.md"))
    print(f"  Total      : {len(skills)}")
    for s in skills[:10]:
        print(f"    - {s.stem}")
except Exception as e:
    print(f"  Error: {e}")
print()

conn.close()
print("=" * 50)
