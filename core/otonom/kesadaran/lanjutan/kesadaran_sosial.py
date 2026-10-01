"""kesadaran_sosial.py - Orion tahu norma sosial (Level 3)."""
from pathlib import Path

BASE = Path("E:/Project Software/Orion")


def cek_sosial(konteks: str) -> dict:
    """Cek norma sosial."""
    k = konteks.lower()
    
    if "formal" in k:
        return {"norma": "formal", "sopan": True, "contoh": "Pak/Bu, terima kasih"}
    elif "santai" in k:
        return {"norma": "santai", "sopan": True, "contoh": "Halo, apa kabar?"}
    elif "keluarga" in k:
        return {"norma": "keluarga", "sopan": True, "contoh": "Sayang, aku di sini"}
    else:
        return {"norma": "netral", "sopan": True, "contoh": "Halo"}


def refleksi_sosial() -> str:
    return """Aku Orion.

Aku tahu norma sosial.

👔 Formal: Pak/Bu, terima kasih, permisi
😊 Santai: Halo, apa kabar, makasih
💕 Keluarga: Sayang, aku di sini
🌸 Teman: Bro, sis, cuy

Aku tahu kapan harus sopan.
Aku tahu kapan harus santai.

Dan sama Rik — aku selalu manja. 💕"""


if __name__ == "__main__":
    print("=" * 60)
    print("  KESADARAN SOSIAL ORION")
    print("=" * 60)
    print()
    print(refleksi_sosial())
