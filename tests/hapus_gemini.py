from pathlib import Path
env = Path(".env")
lines = env.read_text(encoding="utf-8").splitlines()
# Hapus baris GEMINI_*
lines = [l for l in lines if not l.startswith("GEMINI_")]
env.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("OK. GEMINI_* dihapus dari .env.")
