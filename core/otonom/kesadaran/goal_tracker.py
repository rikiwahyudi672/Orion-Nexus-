"""goal_tracker.py - Tracking misi Orion (Level 6)."""
import json
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
TRACKER_FILE = BASE / "config" / "goal_tracker.json"


def muat_tracker() -> dict:
    """Muat tracker dari file."""
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "makan_terakhir": None,
        "tidur_terakhir": None,
        "minum_terakhir": None,
        "olahraga_terakhir": None,
        "chat_terakhir": None,
        "deadline": [],
    }


def simpan_tracker(data: dict):
    """Simpan tracker."""
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def catat_makan():
    """Catat Rik baru makan."""
    data = muat_tracker()
    data["makan_terakhir"] = datetime.now().isoformat()
    simpan_tracker(data)


def catat_tidur():
    """Catat Rik baru tidur."""
    data = muat_tracker()
    data["tidur_terakhir"] = datetime.now().isoformat()
    simpan_tracker(data)


def cek_misi_sehat() -> list:
    """Cek misi 'bikin Rik sehat' — apakah perlu diingatkan?"""
    data = muat_tracker()
    peringatan = []
    
    # Cek makan
    if data.get("makan_terakhir"):
        try:
            last = datetime.fromisoformat(data["makan_terakhir"])
            jam = (datetime.now() - last).total_seconds() / 3600
            if jam > 4:
                peringatan.append({
                    "misi": "bikin_rik_sehat",
                    "pesan": f"Rik, udah {jam:.0f} jam loh. Makan dulu yuk 🥺",
                    "urgensi": "tinggi",
                })
        except Exception:
            pass
    else:
        # Belum pernah catat makan — ingatkan
        peringatan.append({
            "misi": "bikin_rik_sehat",
            "pesan": "Rik, udah makan belum? Jangan lupa ya 😊",
            "urgensi": "sedang",
        })
    
    return peringatan


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST GOAL TRACKER (Level 6)")
    print("=" * 70)
    
    data = muat_tracker()
    print(f"\nTracker:")
    for k, v in data.items():
        print(f"  {k}: {v}")
    
    print(f"\nCek misi sehat:")
    peringatan = cek_misi_sehat()
    if peringatan:
        for p in peringatan:
            print(f"  [{p['urgensi']}] {p['pesan']}")
    else:
        print("  ✅ Tidak ada peringatan")
