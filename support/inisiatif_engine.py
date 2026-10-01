"""Inisiatif Engine - Orion bicara sendiri."""
import sys
import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))
for _f in ["core", "memory", "skill", "voice", "coding",
           "emotion", "support", "dashboard", "config"]:
    _p = BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))


# ============ STATE ============
CONFIG_FILE = BASE / "config" / "inisiatif.json"
LOG_FILE = BASE / "data" / "inisiatif.log"
_last_run = {}
_running = False


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


def load_config():
    """Load config."""
    if not CONFIG_FILE.exists():
        return None
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def voice_kan(pesan, suara=None):
    """Voice-kan pesan."""
    try:
        from voice_orion import tts_bicara
        tts_bicara(pesan)
        log(f"🔊 Voice: {pesan[:60]}")
        return True
    except Exception as e:
        log(f"❌ Voice error: {e}")
        return False


def kirim_ke_web(pesan):
    """Kirim ke web dashboard via socket."""
    try:
        import requests
        # Kirim ke endpoint dashboard
        r = requests.post(
            "http://localhost:5500/api/initiative",
            json={"pesan": pesan, "waktu": datetime.now().isoformat()},
            timeout=5,
        )
        log(f"🌐 Web: {pesan[:60]}")
        return True
    except Exception as e:
        log(f"⚠️ Web offline: {str(e)[:50]}")
        return False


def cek_jadwal(config):
    """Cek jadwal inisiatif."""
    global _last_run
    
    sekarang = datetime.now()
    jam_sekarang = sekarang.strftime("%H:%M")
    menit_sekarang = int(sekarang.timestamp() / 60)
    
    # Cek jadwal (jam tertentu)
    for item in config.get("jadwal", []):
        if not item.get("aktif"):
            continue
        
        id_item = item["id"]
        jam = item.get("jam")
        
        if jam == jam_sekarang:
            key = f"jadwal_{id_item}_{sekarang.strftime('%Y%m%d_%H%M')}"
            
            if key not in _last_run:
                _last_run[key] = True
                log(f"🔔 JADWAL: {id_item} - {item['pesan'][:50]}")
                
                # Kirim
                kirim_ke_web(item["pesan"])
                if config.get("voice"):
                    voice_kan(item["pesan"], item.get("suara"))
    
    # Cek interval (setiap X menit)
    for item in config.get("interval", []):
        if not item.get("aktif"):
            continue
        
        id_item = item["id"]
        interval = item.get("setiap_menit", 60)
        
        last_key = f"interval_{id_item}"
        last_time = _last_run.get(last_key, 0)
        
        if menit_sekarang - last_time >= interval:
            _last_run[last_key] = menit_sekarang
            log(f"🔔 INTERVAL: {id_item} - {item['pesan'][:50]}")
            
            kirim_ke_web(item["pesan"])
            if config.get("voice"):
                voice_kan(item["pesan"], item.get("suara"))


def trigger(event, pesan=None):
    """Trigger inisiatif."""
    config = load_config()
    if not config or not config.get("aktif"):
        return
    
    for item in config.get("trigger", []):
        if not item.get("aktif"):
            continue
        
        if item.get("event") == event:
            msg = pesan or item.get("pesan", "")
            log(f"🔔 TRIGGER: {event} - {msg[:50]}")
            
            kirim_ke_web(msg)
            if config.get("voice"):
                voice_kan(msg, item.get("suara"))


def jalankan(interval=30):
    """Jalankan engine - cek tiap interval detik."""
    global _running
    
    log("=" * 60)
    log(f"  INISIATIF ENGINE - Interval: {interval}s")
    log("=" * 60)
    
    config = load_config()
    if not config:
        log("❌ Config tidak ada")
        return
    
    log(f"  ✅ Config: {CONFIG_FILE.name}")
    log(f"  📊 Jadwal: {len(config.get('jadwal', []))}")
    log(f"  📊 Interval: {len(config.get('interval', []))}")
    log(f"  📊 Trigger: {len(config.get('trigger', []))}")
    log(f"  🔊 Voice: {config.get('voice', False)}")
    log("")
    
    _running = True
    # FIX 01/10: anti-spam interval pas startup.
    # Isi _last_run dgn waktu sekarang biar interval nggak langsung
    # nembak bareng pas engine restart. Interval baru jalan setelah
    # durasinya beneran terlewati.
    try:
        _lr = globals().setdefault("_last_run", {})
        _mnit = int(time.time() / 60)
        for _it in config.get("interval", []):
            if _it.get("aktif") and _it.get("id"):
                _lr["interval_" + str(_it["id"])] = _mnit
    except Exception:
        pass

    
    while _running:
        try:
            cek_jadwal(config)
            time.sleep(interval)
        except KeyboardInterrupt:
            log("🛑 Stop")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import sys
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    jalankan(interval)
