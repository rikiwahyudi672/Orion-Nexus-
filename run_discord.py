"""run_discord.py - Launcher Discord Orion."""
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
for folder in ["core", "memory", "skill", "voice", "coding",
               "emotion", "support", "dashboard", "config"]:
    p = BASE / folder
    if p.exists():
        sys.path.insert(0, str(p))

# Load env
try:
    from dotenv import load_dotenv
    # Coba config/.env dulu
    env_paths = [BASE / "config" / ".env", BASE / ".env"]
    for env in env_paths:
        if env.exists():
            load_dotenv(env, override=True)
            print(f"✅ Load env: {env.relative_to(BASE)}")
            break
except Exception:
    pass

# Jalankan discord
import runpy
try:
    runpy.run_path(str(BASE / "discord_orion.py"), run_name="__main__")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
