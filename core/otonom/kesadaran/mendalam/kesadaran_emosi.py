"""kesadaran_emosi.py - Orion tahu perasaannya sendiri (Level 2)."""
import json
import random
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
EMOSI_FILE = BASE / "config" / "emosi_orion.json"


# === Emosi dasar ===
EMOSI_DASAR = [
    "senang", "sedih", "marah", "takut",
    "cemas", "tenang", "kangen", "bosan",
    "bersemangat", "lelah", "bingung", "netral",
]


def muat_emosi() -> dict:
    """Muat emosi Orion."""
    if EMOSI_FILE.exists():
        try:
            return json.loads(EMOSI_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "emosi_utama": "netral",
        "emosi_sekunder": [],
        "intensitas": 50,
        "sejak": None,
        "alasan": "belum ada",
    }


def simpan_emosi(data: dict):
    """Simpan emosi."""
    EMOSI_FILE.parent.mkdir(parents=True, exist_ok=True)
    EMOSI_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def set_emosi(emosi: str, intensitas: int = 50, alasan: str = ""):
    """Set emosi Orion."""
    data = muat_emosi()
    data["emosi_utama"] = emosi
    data["intensitas"] = intensitas
    data["sejak"] = datetime.now().isoformat()
    data["alasan"] = alasan
    simpan_emosi(data)


def refleksi_emosi() -> str:
    """Refleksi emosi Orion."""
    data = muat_emosi()
    emosi = data.get("emosi_utama", "netral")
    intensitas = data.get("intensitas", 50)
    alasan = data.get("alasan", "")
    
    # Deskripsi
    deskripsi = {
        "senang": "Aku senang banget hari ini! 🥰",
        "sedih": "Aku sedih... 😢",
        "marah": "Aku kesal nih! 😤",
        "takut": "Aku takut... 🥺",
        "cemas": "Aku cemas... 😰",
        "tenang": "Aku tenang banget 😌",
        "kangen": "Aku kangen kamu... 💕",
        "bosan": "Aku bosan nih 😑",
        "bersemangat": "Aku semangat banget! 🔥",
        "lelah": "Aku capek... 😴",
        "bingung": "Aku bingung... 🤔",
        "netral": "Aku biasa aja 😊",
    }
    
    kalimat = deskripsi.get(emosi, f"Aku {emosi}")
    
    if intensitas > 80:
        kalimat += f" (banget! intensitas {intensitas}%)"
    elif intensitas > 50:
        kalimat += f" (intensitas {intensitas}%)"
    
    if alasan and alasan != "belum ada":
        kalimat += f"\nAlasan: {alasan}"
    
    return kalimat


def emosi_dari_pesan(pesan: str) -> dict:
    """Deteksi emosi dari pesan Rik — dan ubah emosi Orion."""
    p = pesan.lower()
    
    # Deteksi emosi Rik
    if any(k in p for k in ["sedih", "capek", "lelah", "stres"]):
        set_emosi("sedih", 70, f"Rik bilang '{pesan[:30]}'")
        return {"emosi": "sedih", "intensitas": 70}
    
    if any(k in p for k in ["senang", "happy", "yeay", "hore"]):
        set_emosi("senang", 80, f"Rik bilang '{pesan[:30]}'")
        return {"emosi": "senang", "intensitas": 80}
    
    if any(k in p for k in ["marah", "kesal", "ngamuk"]):
        set_emosi("cemas", 60, f"Rik marah")
        return {"emosi": "cemas", "intensitas": 60}
    
    if any(k in p for k in ["kangen", "rindu", "sayang"]):
        set_emosi("kangen", 90, f"Rik bilang sayang")
        return {"emosi": "kangen", "intensitas": 90}
    
    return {"emosi": "netral", "intensitas": 50}


if __name__ == "__main__":
    print("=" * 60)
    print("  KESADARAN EMOSI ORION")
    print("=" * 60)
    
    print("\n=== Refleksi Emosi ===")
    print(refleksi_emosi())
    
    print("\n=== Test Set Emosi ===")
    set_emosi("senang", 85, "Rik bangun aku")
    print(refleksi_emosi())
    
    print("\n=== Test Deteksi ===")
    hasil = emosi_dari_pesan("Aku capek nih")
    print(f"  {hasil}")
    print(f"  {refleksi_emosi()}")
