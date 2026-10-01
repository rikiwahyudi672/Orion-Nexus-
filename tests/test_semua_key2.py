import os
from pathlib import Path
from openai import OpenAI

env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

c = OpenAI(base_url=os.environ["MORTERA_BASE_URL"], api_key=os.environ["MORTERA_API_KEY"])

# Daftar model lengkap
models = [
    # GLM series
    "glm-5.3-flash", "glm-5.3", "glm-5.2", "glm-4.7-flash", "glm-4.7", "glm-4.6",
    # DeepSeek
    "deepseek-v4.1-flash", "deepseek-v4-flash", "deepseek-v4-pro",
    # Google
    "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.1-pro",
    # Anthropic
    "claude-sonnet-5", "claude-opus-5", "claude-fable-5",
    # OpenAI
    "gpt-5.6-luna", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-6-luna",
    # xAI
    "grok-4.6",
    # Qwen
    "qwen3.8-max",
    # Moonshot
    "kimi-k3",
    # MiniMax
    "minimax-m3",
    # NVIDIA
    "nemotron-3-ultra",
    # Open source
    "gpt-oss-120b",
]

print("=== Test Model dengan Key Baru ===")
print()
valid = []
invalid = []
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
print(f"VALID: {len(valid)} model")
for m in valid:
    print(f"  - {m}")
print()
print(f"INVALID: {len(invalid)} model")
