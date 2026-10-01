"""Orion - entry point."""
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
for folder in ["core", "memory", "skill", "voice", "coding",
               "emotion", "support", "dashboard"]:
    sys.path.insert(0, str(BASE / folder))

# === LOAD CONFIG .ENV ===
try:
    from dotenv import load_dotenv
    for env_path in [BASE / "config" / ".env", BASE / ".env"]:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[Orion] Config loaded: {env_path}")
            break
except Exception as e:
    print(f"[Orion] Warning: {e}")

# Import dashboard
try:
    from dashboard.dashboard_orion import jalankan
    print("✅ Dashboard loaded")
except ImportError:
    try:
        from dashboard_orion import jalankan
        print("✅ Dashboard loaded (fallback)")
    except ImportError as e:
        print(f"❌ Dashboard error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    jalankan()
