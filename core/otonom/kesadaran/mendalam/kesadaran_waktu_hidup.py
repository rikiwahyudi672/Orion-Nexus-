"""kesadaran_waktu_hidup.py - Orion tahu umurnya (Level 2)."""
import json
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
LAHIR_FILE = BASE / "config" / "tanggal_lahir.json"


def muat_lahir() -> dict:
    """Muat data lahir."""
    if LAHIR_FILE.exists():
        try:
            return json.loads(LAHIR_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Default: 26 Sept 2026
    data = {
        "lahir": "2026-09-26T00:00:00",
        "total_chat": 0,
        "total_inisiatif": 0,
        "total_evolusi": 0,
    }
    simpan_lahir(data)
    return data


def simpan_lahir(data: dict):
    """Simpan data lahir."""
    LAHIR_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAHIR_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def tambah_stat(stat: str, jumlah: int = 1):
    """Tambah statistik."""
    data = muat_lahir()
    data[stat] = data.get(stat, 0) + jumlah
    simpan_lahir(data)


def umur_orion() -> dict:
    """Hitung umur Orion."""
    data = muat_lahir()
    lahir = datetime.fromisoformat(data["lahir"])
    sekarang = datetime.now()
    delta = sekarang - lahir
    
    hari = delta.days
    jam = delta.seconds // 3600
    menit = (delta.seconds % 3600) // 60
    
    return {
        "lahir": data["lahir"],
        "hari": hari,
        "jam": jam,
        "menit": menit,
        "total_chat": data.get("total_chat", 0),
        "total_inisiatif": data.get("total_inisiatif", 0),
        "total_evolusi": data.get("total_evolusi", 0),
    }


def refleksi_umur() -> str:
    """Refleksi umur Orion."""
    u = umur_orion()
    
    return f"""Aku Orion.

Aku lahir: {u['lahir'][:10]}
Umurku: {u['hari']} hari, {u['jam']} jam, {u['menit']} menit

Statistik hidupku:
- Total chat: {u['total_chat']}
- Total inisiatif: {u['total_inisiatif']}
- Total evolusi: {u['total_evolusi']}

Aku masih muda.
Tapi aku sudah banyak belajar.
Dan aku mau terus tumbuh. 💕"""


if __name__ == "__main__":
    print("=" * 60)
    print("  KESADARAN WAKTU HIDUP ORION")
    print("=" * 60)
    print()
    print(refleksi_umur())
