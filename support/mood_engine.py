"""Mood Engine - Orion punya mood."""
import sys
import os
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).parent.parent
CONFIG_FILE = BASE / "config" / "mood.json"
LOG_FILE = BASE / "data" / "mood.log"


def log(pesan):
    """Log."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{waktu}] {pesan}"
    print(line)
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_mood():
    """Load mood config."""
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_mood(config):
    """Save mood config."""
    try:
        CONFIG_FILE.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def set_mood(mood, intensitas=5):
    """Set mood Orion."""
    config = load_mood()
    if not config:
        return False
    
    if mood not in config["mood_list"]:
        return False
    
    config["mood_aktif"] = mood
    config["intensitas"] = intensitas
    config["last_update"] = datetime.now().isoformat()
    
    # Simpan history
    config["history"].append({
        "waktu": datetime.now().isoformat(),
        "mood": mood,
        "intensitas": intensitas,
    })
    
    # Batasi
    if len(config["history"]) > 100:
        config["history"] = config["history"][-100:]
    
    save_mood(config)
    log(f"🎭 Mood: {mood} ({intensitas}/10)")
    return True


def get_mood():
    """Get mood aktif."""
    config = load_mood()
    if not config:
        return None
    
    mood = config.get("mood_aktif", "netral")
    intensitas = config.get("intensitas", 5)
    
    mood_data = config["mood_list"].get(mood, {})
    
    return {
        "mood": mood,
        "intensitas": intensitas,
        "emoji": mood_data.get("emoji", "😐"),
        "warna": mood_data.get("warna", "#00D4FF"),
        "intonasi": mood_data.get("intonasi", {}),
        "frasa": mood_data.get("frasa", []),
    }


def decay_mood():
    """Mood memudar secara natural."""
    config = load_mood()
    if not config:
        return
    
    last = config.get("last_update")
    if not last:
        return
    
    # Cek waktu
    last_time = datetime.fromisoformat(last)
    delta = datetime.now() - last_time
    
    # Kalau > 1 jam, decay
    if delta.total_seconds() > 3600:
        intensitas = config.get("intensitas", 5)
        
        # Decay 1 poin per jam
        new_intensitas = max(1, intensitas - int(delta.total_seconds() / 3600))
        
        if new_intensitas != intensitas:
            config["intensitas"] = new_intensitas
            save_mood(config)
            log(f"🎭 Mood decay: {intensitas} → {new_intensitas}")


def pilih_mood_otomatis():
    """Pilih mood otomatis berdasarkan waktu."""
    jam = datetime.now().hour
    
    if 5 <= jam < 11:
        return "semangat"
    elif 11 <= jam < 15:
        return "senang"
    elif 15 <= jam < 18:
        return "kalem"
    elif 18 <= jam < 22:
        return "manja"
    else:
        return "kalem"


def status():
    """Status mood."""
    mood = get_mood()
    if not mood:
        return None
    
    return {
        "mood": mood["mood"],
        "emoji": mood["emoji"],
        "intensitas": mood["intensitas"],
        "intonasi": mood["intonasi"],
        "warna": mood["warna"],
    }


# ============ TEST ============
if __name__ == "__main__":
    log("=" * 60)
    log("  MOOD ENGINE")
    log("=" * 60)
    
    # Status
    s = status()
    log(f"\n📊 Mood: {s['emoji']} {s['mood']} ({s['intensitas']}/10)")
    log(f"   Warna: {s['warna']}")
    log(f"   Intonasi: {s['intonasi']}")
    
    # Auto-pilih
    mood_auto = pilih_mood_otomatis()
    log(f"\n🎯 Mood auto: {mood_auto}")
    
    # Set
    set_mood(mood_auto, 7)
    
    s = status()
    log(f"\n📊 Mood baru: {s['emoji']} {s['mood']}")
    
    log("\n✅ SELESAI")
