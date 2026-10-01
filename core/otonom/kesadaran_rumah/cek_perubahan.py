"""cek_perubahan.py - Orion tahu perubahan rumahnya."""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
SNAPSHOT_FILE = BASE / "core" / "otonom" / "kesadaran_rumah" / "snapshot_rumah.json"


def bikin_snapshot() -> dict:
    """Bikin snapshot rumah."""
    snapshot = {}
    
    for f in BASE.rglob("*"):
        if f.is_file() and "__pycache__" not in str(f) and "arsip" not in str(f).lower():
            try:
                rel = str(f.relative_to(BASE))
                snapshot[rel] = {
                    "size": f.stat().st_size,
                    "mtime": f.stat().st_mtime,
                }
            except Exception:
                pass
    
    return snapshot


def simpan_snapshot():
    """Simpan snapshot ke file."""
    snapshot = bikin_snapshot()
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return len(snapshot)


def muat_snapshot() -> dict:
    """Muat snapshot lama."""
    if not SNAPSHOT_FILE.exists():
        return {}
    try:
        return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def cek_perubahan() -> dict:
    """Cek perubahan rumah."""
    lama = muat_snapshot()
    baru = bikin_snapshot()
    
    if not lama:
        simpan_snapshot()
        return {
            "sukses": True,
            "pertama_kali": True,
            "pesan": f"Snapshot pertama: {len(baru)} file",
        }
    
    # Cari file baru
    file_baru = [f for f in baru if f not in lama]
    
    # Cari file hilang
    file_hilang = [f for f in lama if f not in baru]
    
    # Cari file berubah
    file_berubah = []
    for f in baru:
        if f in lama:
            if baru[f]["mtime"] != lama[f]["mtime"]:
                file_berubah.append(f)
    
    # Simpan snapshot baru
    simpan_snapshot()
    
    return {
        "sukses": True,
        "file_baru": file_baru,
        "file_hilang": file_hilang,
        "file_berubah": file_berubah,
        "total_baru": len(file_baru),
        "total_hilang": len(file_hilang),
        "total_berubah": len(file_berubah),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  CEK PERUBAHAN RUMAH")
    print("=" * 60)
    
    # Bikin snapshot kalau belum ada
    if not SNAPSHOT_FILE.exists():
        jumlah = simpan_snapshot()
        print(f"\n[OK] Snapshot pertama: {jumlah} file")
    else:
        hasil = cek_perubahan()
        print(f"\nFile baru: {hasil['total_baru']}")
        for f in hasil.get("file_baru", [])[:5]:
            print(f"  + {f}")
        print(f"\nFile hilang: {hasil['total_hilang']}")
        print(f"\nFile berubah: {hasil['total_berubah']}")
