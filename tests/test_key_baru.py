import os
from pathlib import Path
from openai import OpenAI

env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

print("Test Mortera dengan API key baru...")
print()

c = OpenAI(base_url=os.environ["MORTERA_BASE_URL"], api_key=os.environ["MORTERA_API_KEY"])

# Test model yang ada + GLM-4.7-Flash
models = [
    "glm-4.7-flash",      # baru - gratis
    "glm-4.7",            # kandidat
    "glm-5.3-flash",      # yang lama
    "glm-5.3",
    "glm-5.2",
]

for m in models:
    try:
        r = c.chat.completions.create(model=m, messages=[{"role": "user", "content": "hi"}], max_tokens=5)
        print(f"OK    {m}")
    except Exception as e:
        err = str(e)[:70].replace("\n", " ")
        print(f"X     {m} -> {err}")
