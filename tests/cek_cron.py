import cron_orion

print("Task di cron_tasks.json:")
print()
for t in cron_orion.load_tasks():
    jam = t.get("jam", "?")
    aksi = t.get("aksi", "tts")
    isi = t.get("pesan") or t.get("prompt", "")
    print(f"  {jam} [{aksi}] {isi[:60]}")
