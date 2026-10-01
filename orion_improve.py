"""orion_improve.py - Improve fix otomatis berdasarkan pola error."""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
LEARN_LOG = BASE / "arsip" / "learn_log.json"
IMPROVE_LOG = BASE / "arsip" / "improve_log.json"


def load_learn():
    """Load hasil analisa."""
    if not LEARN_LOG.exists():
        return None
    try:
        return json.loads(LEARN_LOG.read_text(encoding="utf-8"))
    except Exception:
        return None


def rekomendasi():
    """Kasih rekomendasi improve."""
    learn = load_learn()
    if not learn:
        return {"error": "Belum ada analisa - jalankan orion_learn.py dulu"}
    
    rekomendasi_list = []
    
    # Cek error yang sering muncul
    messages = learn.get("error_messages", {})
    
    if messages.get("BOM", 0) > 0:
        rekomendasi_list.append({
            "prioritas": "tinggi",
            "aksi": "Tambah fixer BOM di semua file .py",
            "alasan": f"BOM muncul {messages['BOM']}x",
        })
    
    if messages.get("Mojibake", 0) > 0:
        rekomendasi_list.append({
            "prioritas": "tinggi",
            "aksi": "Perluas pattern anti-mojibake",
            "alasan": f"Mojibake muncul {messages['Mojibake']}x",
        })
    
    if messages.get("Import error", 0) > 0:
        rekomendasi_list.append({
            "prioritas": "sedang",
            "aksi": "Perbaiki sys.path di modul terkait",
            "alasan": f"Import error {messages['Import error']}x",
        })
    
    # Cek modul yang sering error
    modules = learn.get("error_modules", {})
    for mod, count in list(modules.items())[:3]:
        if count >= 2:
            rekomendasi_list.append({
                "prioritas": "sedang",
                "aksi": f"Review modul: {mod}",
                "alasan": f"Error {count}x",
            })
    
    return {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rekomendasi": len(rekomendasi_list),
        "rekomendasi": rekomendasi_list,
    }


def laporan():
    """Tampilkan rekomendasi."""
    print("=" * 70)
    print("  ORION IMPROVE - REKOMENDASI")
    print("=" * 70)
    
    hasil = rekomendasi()
    
    if "error" in hasil:
        print(f"\n  {hasil['error']}")
        return
    
    print(f"\n  Total rekomendasi: {hasil['total_rekomendasi']}")
    
    if hasil["rekomendasi"]:
        print(f"\n  === Rekomendasi ===")
        for r in hasil["rekomendasi"]:
            print(f"\n  [{r['prioritas'].upper()}] {r['aksi']}")
            print(f"    Alasan: {r['alasan']}")
    else:
        print(f"\n  ✅ Tidak ada rekomendasi - Orion sehat")
    
    print("=" * 70)
    
    # Simpan
    IMPROVE_LOG.parent.mkdir(parents=True, exist_ok=True)
    IMPROVE_LOG.write_text(json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Laporan: {IMPROVE_LOG.relative_to(BASE)}")


if __name__ == "__main__":
    laporan()
