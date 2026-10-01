import os
from pathlib import Path
from openai import OpenAI

env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

c = OpenAI(base_url=os.environ["MORTERA_BASE_URL"], api_key=os.environ["MORTERA_API_KEY"])

models = [
    "glm-5.3-flash", "glm-5.3", "glm-5.2", "glm-4.7-flash", "glm-4.7", "glm-4.6",
    "deepseek-v4.1-flash", "deepseek-v4-flash", "deepseek-v4-pro",
    "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.1-pro",
    "claude-sonnet-5", "claude-opus-5",
    "gpt-5.6-luna", "gpt-5.6-terra", "gpt-6-luna",
    "grok-4.6", "qwen3.8-max", "kimi-k3", "gpt-oss-120b",
]

valid = []
invalid = []
print("=== Test Model ===")
print()
for m in models:
    try:
        c.chat.completions.create(model=m, messages=[{"role": "user", "content": "hi"}], max_tokens=5)
        print(f"OK    {m}")
        valid.append(m)
    except Exception as e:
        err = str(e)[:60].replace("\n", " ")
        print(f"X     {m} -> {err}")
        invalid.append(m)

print()
print("=" * 50)
print(f"VALID: {len(valid)}")
for m in valid:
    print(f"  ✓ {m}")
print()
print(f"INVALID: {len(invalid)}")
