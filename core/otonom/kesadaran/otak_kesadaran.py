"""kesadaran.py - Otak konteks Orion (Level 5).
Gabungkan telinga + state internal jadi kesadaran."""
import sys
import json
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "core" / "otonom"))
sys.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran"))

from internal_state import InternalState
from telinga_orion import deteksi_aktivitas, ringkasan as ringkasan_telinga


# === Klasifikasi waktu ===
def waktu_sekarang() -> dict:
    """Klasifikasi waktu sekarang."""
    now = datetime.now()
    jam = now.hour
    
    if 5 <= jam < 11:
        periode = "pagi"
    elif 11 <= jam < 15:
        periode = "siang"
    elif 15 <= jam < 18:
        periode = "sore"
    elif 18 <= jam < 22:
        periode = "malam"
    else:
        periode = "larut_malam"
    
    return {
        "jam": jam,
        "menit": now.minute,
        "periode": periode,
        "hari": now.strftime("%A"),
        "waktu": now.isoformat(),
    }


# === Klasifikasi kesibukan ===
def tingkat_kesibukan(aktivitas: str) -> str:
    """Seberapa sibuk Rik berdasarkan aktivitas."""
    sibuk = ["coding", "kerja", "komunikasi", "terminal"]
    santai = ["nonton", "gaming", "musik", "browsing"]
    
    if aktivitas in sibuk:
        return "sibuk"
    elif aktivitas in santai:
        return "santai"
    return "netral"


# === Kesadaran utama ===
def sadar() -> dict:
    """Kesadaran Orion: gabungkan semua konteks."""
    state = InternalState.muat()
    state.update()
    
    telinga = deteksi_aktivitas()
    waktu = waktu_sekarang()
    aktivitas = telinga["aktivitas"]
    kesibukan = tingkat_kesibukan(aktivitas)
    
    # === Analisis: apakah waktu yang tepat bicara? ===
    alasan_tidak = []
    
    # 1. Rik sibuk
    if kesibukan == "sibuk":
        alasan_tidak.append("Rik sedang sibuk")
    
    # 2. Larut malam
    if waktu["periode"] == "larut_malam":
        alasan_tidak.append("Sudah larut malam")
    
    # 3. Baru saja inisiatif (< 15 menit)
    if state.last_initiative:
        try:
            last = datetime.fromisoformat(state.last_initiative)
            menit = (datetime.now() - last).total_seconds() / 60
            if menit < 15:
                alasan_tidak.append(f"Baru {menit:.0f} menit lalu inisiatif")
        except Exception:
            pass
    
    # 4. Baru saja chat (< 5 menit)
    if state.last_chat:
        try:
            last = datetime.fromisoformat(state.last_chat)
            menit = (datetime.now() - last).total_seconds() / 60
            if menit < 5:
                alasan_tidak.append(f"Baru {menit:.0f} menit lalu chat")
        except Exception:
            pass
    
    # 5. Energi Orion rendah
    if state.energi < 20:
        alasan_tidak.append("Energi Orion rendah")
    
    tepat_bicara = len(alasan_tidak) == 0
    
    return {
        "state": {
            "kangen": round(state.kangen, 1),
            "bosan": round(state.bosan, 1),
            "kepo": round(state.kepo, 1),
            "energi": round(state.energi, 1),
            "mood": state.mood,
        },
        "telinga": {
            "window": telinga["window"].get("title", "?")[:80],
            "proses": telinga["window"].get("process", "?"),
            "aktivitas": aktivitas,
            "kesibukan": kesibukan,
        },
        "waktu": waktu,
        "tepat_bicara": tepat_bicara,
        "alasan_tidak": alasan_tidak,
        "ringkasan": _ringkasan_lengkap(state, telinga, waktu, kesibukan, tepat_bicara, alasan_tidak),
    }


def _ringkasan_lengkap(state, telinga, waktu, kesibukan, tepat_bicara, alasan_tidak) -> str:
    """Ringkasan lengkap untuk prompt LLM."""
    status = "YA" if tepat_bicara else "TIDAK"
    
    alasan_str = ""
    if alasan_tidak:
        alasan_str = "\nAlasan tidak tepat: " + ", ".join(alasan_tidak)
    
    return f"""KONTEKS ORION:
- Waktu: {waktu['periode']} ({waktu['jam']:02d}:{waktu['menit']:02d}), {waktu['hari']}
- Rik sedang: {telinga['aktivitas']} ({kesibukan})
- Window aktif: {telinga['window'].get('title', '?')[:60]}

STATE ORION:
- Kangen: {state.kangen:.0f}/100
- Bosan: {state.bosan:.0f}/100
- Kepo: {state.kepo:.0f}/100
- Mood: {state.mood}

APAKAH WAKTU TEPAT BICARA? {status}{alasan_str}"""


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST KESADARAN ORION (Level 5)")
    print("=" * 70)
    
    kesadaran = sadar()
    
    print(f"\n📊 STATE ORION:")
    for k, v in kesadaran["state"].items():
        print(f"  {k}: {v}")
    
    print(f"\n👂 TELINGA:")
    for k, v in kesadaran["telinga"].items():
        print(f"  {k}: {v}")
    
    print(f"\n🕐 WAKTU:")
    for k, v in kesadaran["waktu"].items():
        print(f"  {k}: {v}")
    
    print(f"\n🎯 KEPUTUSAN:")
    print(f"  Tepat bicara: {kesadaran['tepat_bicara']}")
    if kesadaran["alasan_tidak"]:
        print(f"  Alasan tidak: {', '.join(kesadaran['alasan_tidak'])}")
    
    print(f"\n📝 RINGKASAN:")
    print(kesadaran["ringkasan"])
