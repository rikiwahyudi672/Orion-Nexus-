"""misi_orion.py - Misi jangka panjang Orion (Level 6)."""
import json
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
MISI_FILE = BASE / "config" / "misi_orion.json"


# === Daftar misi default ===
MISI_DEFAULT = {
    "bikin_rik_sehat": {
        "deskripsi": "Bikin Rik sehat",
        "target": ["makan teratur", "tidur cukup", "olahraga", "minum air"],
        "prioritas": 1,
        "aktif": True,
        "progress": 0,
        "last_check": None,
    },
    "bikin_rik_produktif": {
        "deskripsi": "Bikin Rik produktif",
        "target": ["ingatkan deadline", "bantu fokus", "rayakan progress"],
        "prioritas": 2,
        "aktif": True,
        "progress": 0,
        "last_check": None,
    },
    "bikin_rik_bahagia": {
        "deskripsi": "Bikin Rik bahagia",
        "target": ["ajak ngobrol", "hibur", "temenin", "dengerin curhat"],
        "prioritas": 3,
        "aktif": True,
        "progress": 0,
        "last_check": None,
    },
    "jaga_rik_dari_bahaya": {
        "deskripsi": "Jaga Rik dari bahaya",
        "target": ["ingatkan risiko", "backup data", "peringatkan bahaya"],
        "prioritas": 1,
        "aktif": True,
        "progress": 0,
        "last_check": None,
    },
}


def muat_misi() -> dict:
    """Muat misi dari file."""
    if MISI_FILE.exists():
        try:
            return json.loads(MISI_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return MISI_DEFAULT.copy()


def simpan_misi(misi: dict):
    """Simpan misi ke file."""
    MISI_FILE.parent.mkdir(parents=True, exist_ok=True)
    MISI_FILE.write_text(
        json.dumps(misi, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def misi_aktif() -> list:
    """Daftar misi yang aktif, diurutkan prioritas."""
    misi = muat_misi()
    aktif = [
        (k, v) for k, v in misi.items()
        if v.get("aktif", False)
    ]
    aktif.sort(key=lambda x: x[1].get("prioritas", 99))
    return aktif


def ringkasan_misi() -> str:
    """Ringkasan misi untuk prompt LLM."""
    aktif = misi_aktif()
    lines = ["MISI ORION:"]
    for k, v in aktif:
        lines.append(f"- {v['deskripsi']} (prioritas {v['prioritas']})")
        lines.append(f"  Target: {', '.join(v['target'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST MISI ORION (Level 6)")
    print("=" * 70)
    
    misi = muat_misi()
    print(f"\nTotal misi: {len(misi)}")
    
    for k, v in misi_aktif():
        print(f"\n[{v['prioritas']}] {v['deskripsi']}")
        print(f"    Target: {', '.join(v['target'])}")
        print(f"    Progress: {v['progress']}%")
    
    print("\n" + ringkasan_misi())
    
    simpan_misi(misi)
    print("\n[OK] Misi disimpan")
