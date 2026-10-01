"""evolusi_kode.py - Loop utama evolusi kode Orion (Level 3)."""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "core" / "otonom" / "evolusi"))

from safety import cek_limit_evolusi, catat_evolusi
from code_generator import generate_fungsi
from code_tester import test_lengkap
from code_integrator import integrasi_otomatis


# === Antrian evolusi ===
ANTRIAN_FILE = BASE / "core" / "otonom" / "evolusi" / "antrian.json"


def muat_antrian() -> list:
    """Muat antrian evolusi."""
    if ANTRIAN_FILE.exists():
        try:
            return json.loads(ANTRIAN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def simpan_antrian(antrian: list):
    """Simpan antrian."""
    ANTRIAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    ANTRIAN_FILE.write_text(json.dumps(antrian, indent=2, ensure_ascii=False), encoding="utf-8")


def tambah_antrian(deskripsi: str, nama_fungsi: str = None):
    """Tambah antrian evolusi."""
    antrian = muat_antrian()
    antrian.append({
        "deskripsi": deskripsi,
        "nama_fungsi": nama_fungsi,
        "waktu": datetime.now().isoformat(),
        "status": "pending",
    })
    simpan_antrian(antrian)
    print(f"[Evolusi] Antrian ditambah: {deskripsi[:60]}")


def proses_antrian() -> dict:
    """Proses satu antrian evolusi."""
    antrian = muat_antrian()
    
    # Cari yang pending
    pending = [a for a in antrian if a.get("status") == "pending"]
    
    if not pending:
        return {"sukses": False, "alasan": "Tidak ada antrian pending"}
    
    # Ambil yang pertama
    item = pending[0]
    print(f"\n[Evolusi] Proses: {item['deskripsi'][:60]}")
    
    # Cek limit
    bisa, alasan = cek_limit_evolusi()
    if not bisa:
        print(f"  X: {alasan}")
        return {"sukses": False, "alasan": alasan}
    
    # 1. Generate
    print("  [1/3] Generate kode...")
    hasil_gen = generate_fungsi(item["deskripsi"], item.get("nama_fungsi"))
    
    if not hasil_gen["sukses"]:
        item["status"] = "gagal"
        item["error"] = hasil_gen["alasan"]
        simpan_antrian(antrian)
        return {"sukses": False, "alasan": hasil_gen["alasan"]}
    
    # 2. Test
    print("  [2/3] Test kode...")
    hasil_test = test_lengkap(hasil_gen["path"])
    
    if not hasil_test["sukses"]:
        item["status"] = "gagal_test"
        item["error"] = hasil_test["syntax"].get("alasan", "?")
        simpan_antrian(antrian)
        return {"sukses": False, "alasan": f"Test gagal: {item['error']}"}
    
    # 3. Integrasi
    print("  [3/3] Integrasi...")
    hasil_int = integrasi_otomatis(hasil_gen["path"])
    
    if not hasil_int["sukses"]:
        item["status"] = "gagal_integrasi"
        item["error"] = hasil_int["alasan"]
        simpan_antrian(antrian)
        return {"sukses": False, "alasan": hasil_int["alasan"]}
    
    # Sukses
    item["status"] = "sukses"
    item["path"] = hasil_int["path"]
    item["waktu_selesai"] = datetime.now().isoformat()
    simpan_antrian(antrian)
    
    catat_evolusi(hasil_int["path"], "evolusi", True)
    
    print(f"  OK: {hasil_int['path']}")
    
    return {
        "sukses": True,
        "path": hasil_int["path"],
        "alasan": "Berhasil",
    }


def main():
    """Loop utama evolusi kode."""
    print("=" * 60)
    print("  ORION EVOLUSI KODE - Level 3")
    print("=" * 60)
    print()
    print("  Perintah:")
    print("    tambah <deskripsi>  - Tambah antrian")
    print("    proses              - Proses antrian")
    print("    list                - Lihat antrian")
    print("    quit                - Keluar")
    print()
    
    while True:
        try:
            cmd = input("Evolusi> ").strip()
            
            if not cmd:
                continue
            
            if cmd == "quit":
                break
            elif cmd == "list":
                antrian = muat_antrian()
                for a in antrian:
                    status = a.get("status", "?")
                    print(f"  [{status}] {a['deskripsi'][:60]}")
            elif cmd.startswith("tambah "):
                deskripsi = cmd[7:].strip()
                tambah_antrian(deskripsi)
            elif cmd == "proses":
                hasil = proses_antrian()
                print(f"  Hasil: {hasil}")
            else:
                print(f"  Perintah tidak dikenal: {cmd}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n[Evolusi] Selesai")


if __name__ == "__main__":
    main()
