"""code_integrator.py - Orion integrasi kode (Level 3)."""
import shutil
import sys
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "core" / "otonom" / "evolusi"))

from safety import cek_path_aman, catat_evolusi
from code_tester import test_lengkap


def integrasi_file(
    source_path: str,
    target_folder: str,
    backup: bool = True,
) -> dict:
    """
    Integrasi file dari output ke folder target.
    
    Args:
        source_path: File sumber (dari output/)
        target_folder: Folder target
        backup: Backup dulu?
    
    Returns:
        {
            "sukses": bool,
            "path": str,
            "alasan": str,
        }
    """
    print(f"[Integrator] Integrasi: {Path(source_path).name}")
    
    # 1. Cek source ada
    src = Path(source_path)
    if not src.exists():
        return {"sukses": False, "path": "", "alasan": f"Source tidak ada: {src}"}
    
    # 2. Test dulu
    print("  Test kode...")
    hasil_test = test_lengkap(source_path)
    
    if not hasil_test["sukses"]:
        return {
            "sukses": False,
            "path": "",
            "alasan": f"Test gagal: {hasil_test['syntax'].get('alasan', '?')}",
        }
    
    # 3. Target path
    target_folder_path = Path(target_folder)
    target_file = target_folder_path / src.name
    
    # 4. Cek path aman
    aman, alasan = cek_path_aman(str(target_file))
    if not aman:
        return {"sukses": False, "path": "", "alasan": f"Path tidak aman: {alasan}"}
    
    # 5. Backup kalau file sudah ada
    if target_file.exists() and backup:
        backup_dir = BASE / "arsip" / f"integrasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_file, backup_dir / f"{target_file.name}.bak")
        print(f"  Backup: {backup_dir.name}")
    
    # 6. Copy file
    target_folder_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target_file)
    
    print(f"  OK: {target_file.relative_to(BASE)}")
    
    # 7. Catat evolusi
    catat_evolusi(str(target_file), "integrasi", True)
    
    return {
        "sukses": True,
        "path": str(target_file),
        "alasan": "Berhasil integrasi",
    }


def integrasi_otomatis(source_path: str) -> dict:
    """
    Integrasi otomatis — pilih folder target dari nama file.
    """
    src = Path(source_path)
    nama = src.stem.lower()
    
    # Tentukan folder target
    if "voice" in nama or "tts" in nama or "suara" in nama:
        target = BASE / "voice"
    elif "memory" in nama or "ingat" in nama:
        target = BASE / "memory"
    elif "skill" in nama or "tool" in nama:
        target = BASE / "skill"
    elif "kesadaran" in nama or "otonom" in nama:
        target = BASE / "core" / "otonom"
    else:
        target = BASE / "core" / "otonom" / "evolusi" / "modul"
    
    print(f"[Integrator] Target: {target.relative_to(BASE)}")
    return integrasi_file(source_path, str(target))


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST CODE INTEGRATOR")
    print("=" * 60)
    
    # Test integrasi otomatis
    output_dir = BASE / "core" / "otonom" / "evolusi" / "output"
    files = list(output_dir.glob("*.py"))
    
    if not files:
        print("[!] Belum ada file di output/")
    else:
        f = files[0]
        print(f"\n=== Test integrasi: {f.name} ===")
        hasil = integrasi_otomatis(str(f))
        print(f"  Sukses: {hasil['sukses']}")
        print(f"  Path: {hasil['path']}")
        print(f"  Alasan: {hasil['alasan']}")
