import json
from pathlib import Path
from datetime import datetime, timedelta

f = Path("cron_tasks.json")
data = json.loads(f.read_text(encoding="utf-8"))

# Hapus task test lama
data["tasks"] = [t for t in data["tasks"] if "Test LLM" not in (t.get("prompt") or "")]

# Tambah task 2 menit dari sekarang
jam = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M")
data["tasks"].append({
    "jam": jam,
    "aksi": "llm",
    "prompt": "Test LLM task. Kasih komentar singkat tentang laptop Riki."
})

f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK. Task test jam {jam}")
