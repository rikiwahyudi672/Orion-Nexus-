import json
from pathlib import Path

f = Path("cron_tasks.json")
data = json.loads(f.read_text(encoding="utf-8"))

# Hapus task yang jam 06:25 dan 06:26
data["tasks"] = [t for t in data["tasks"] if t["jam"] not in ("06:25", "06:26", "06:21")]

f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("OK. Task lama dihapus.")
print()
print("Task tersisa:")
for t in data["tasks"]:
    print(f"  {t['jam']} [{t.get('aksi', 'tts')}] {(t.get('pesan') or t.get('prompt', ''))[:40]}")
