import os
from pathlib import Path
from openai import OpenAI

env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

c = OpenAI(
    base_url=os.environ["MORTERA_BASE_URL"],
    api_key=os.environ["MORTERA_API_KEY"],
)

models = [
    "glm-5.3-flash", "glm-5.3", "glm-5.2",
    "claude-sonnet-5", "claude-opus-5",
    "gemini-3.7-flash", "gemini-3.8-flash",
    "deepseek-v4.1-flash", "gpt-6-luna",
    "grok-4.6", "qwen3.8-max", "kimi-k3",
    "minimax-m3", "nemotron-3-ultra",
]

for m in models:
    try:
        r = c.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        print(f"OK    {m}")
    except Exception as e:
        err = str(e)[:80].replace("\n", " ")
        print(f"X     {m} -> {err}")
