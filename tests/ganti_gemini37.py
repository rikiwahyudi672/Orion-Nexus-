from pathlib import Path
env = Path(".env")
lines = env.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("GEMINI_MODEL="):
        lines[i] = "GEMINI_MODEL=gemini-3.7-flash"
env.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("OK. Ganti ke gemini-3.7-flash")
