import os
from pathlib import Path
from openai import OpenAI

# Load .env manual
env = Path(".env")
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

# Cek key
print("MORTERA_API_KEY:", "OK" if os.environ.get("MORTERA_API_KEY") else "KOSONG")
print("GEMINI_API_KEY :", "OK" if os.environ.get("GEMINI_API_KEY") else "KOSONG")
print("GROQ_API_KEY   :", "OK" if os.environ.get("GROQ_API_KEY") else "KOSONG")
print("GEMINI_BASE_URL:", os.environ.get("GEMINI_BASE_URL", "(tidak ada)"))
print()

# Test Mortera dulu (yang pasti punya key)
print("=== Test Mortera ===")
try:
    c = OpenAI(
        base_url=os.environ["MORTERA_BASE_URL"],
        api_key=os.environ["MORTERA_API_KEY"],
    )
    r = c.chat.completions.create(
        model=os.environ["MORTERA_MODEL"],
        messages=[{"role": "user", "content": "Halo, sebutkan nama kamu 1 kata"}],
    )
    print("OK:", r.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
print()

# Test Gemini (kalau ada key)
if os.environ.get("GEMINI_API_KEY"):
    print("=== Test Gemini ===")
    try:
        c = OpenAI(
            base_url=os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            api_key=os.environ["GEMINI_API_KEY"],
        )
        r = c.chat.completions.create(
            model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
            messages=[{"role": "user", "content": "Halo"}],
        )
        print("OK:", r.choices[0].message.content)
    except Exception as e:
        print("ERROR:", e)
else:
    print("=== Gemini skip (key kosong) ===")
