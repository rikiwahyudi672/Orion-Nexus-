import json
from pathlib import Path

f = Path("cron_tasks.json")
data = json.loads(f.read_text(encoding="utf-8"))

# Hapus task test
data["tasks"] = [
    t for t in data["tasks"]
    if "Test fix" not in (t.get("pesan") or "")
    and "Test LLM" not in (t.get("prompt") or "")
    and "Cek aktivitas Riki sekarang" not in (t.get("prompt") or "")
]

f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK. Task test dihapus. Sisa: {len(data['tasks'])}")
print()
for t in data["tasks"]:
    print(f"  {t['jam']} [{t.get('aksi', 'tts')}] {(t.get('pesan') or t.get('prompt', ''))[:50]}")
