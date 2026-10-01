import os
from pathlib import Path
from openai import OpenAI

env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

c = OpenAI(base_url=os.environ["MORTERA_BASE_URL"], api_key=os.environ["MORTERA_API_KEY"])

print("=== Test model di Mortera (key baru) ===")
models = [
    "glm-5.3-flash",
    "glm-5.3",
    "glm-5.2",
    "glm-4.7-flash",
    "glm-4.7",
    "glm-4.6",
    "deepseek-v4.1-flash",
    "gemini-3.7-flash",
    "claude-sonnet-5",
    "gpt-5.6-luna",
    "gpt-oss-120b",
    "kimi-k3",
]

for m in models:
    try:
        c.chat.completions.create(model=m, messages=[{"role": "user", "content": "hi"}], max_tokens=5)
        print(f"OK    {m}")
    except Exception as e:
        err = str(e)[:60].replace("\n", " ")
        print(f"X     {m} -> {err}")
