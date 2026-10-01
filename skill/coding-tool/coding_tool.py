"""coding_tool.py - Wrapper tool_eksekusi untuk tool loop."""
import sys
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "coding"))
sys.path.insert(0, str(BASE))


def jalankan(aksi="", path="", isi="", perintah="", folder="", file_path="", instruksi=""):
    """
    Jalankan aksi coding.
    
    Args:
        aksi: "buka_notepad" / "buka_vscode" / "buka_cmd" / "buka_powershell" /
              "buka_windows_terminal" / "buka_file" / "tulis" / "baca" /
              "terminal" / "fix_bug" / "analisis" / "scan" / "list"
        path: path file/folder
        isi: isi file (untuk tulis)
        perintah: perintah terminal
        folder: folder (untuk scan/list)
        file_path: file (untuk fix_bug/analisis)
        instruksi: instruksi (untuk fix_file)
    """
    try:
        import tool_eksekusi as te
        
        # === BUKA APP ===
        if aksi == "buka_notepad":
            return te.buka_notepad(path or None)
        
        elif aksi == "buka_vscode":
            return te.buka_vscode(path or None)
        
        elif aksi == "buka_cmd":
            return te.buka_cmd(path or None)
        
        elif aksi == "buka_powershell":
            return te.buka_powershell(path or None)
        
        elif aksi == "buka_windows_terminal":
            return te.buka_windows_terminal(path or None)
        
        elif aksi == "buka_vs2022":
            return te.buka_vs2022(path or None)
        
        elif aksi == "buka_file":
            if not path:
                return {"sukses": False, "error": "Path harus diisi"}
            return te.buka_file(path)
        
        # === FILE ===
        elif aksi == "tulis":
            if not path or not isi:
                return {"sukses": False, "error": "Path dan isi harus diisi"}
            return te.tulis_file(path, isi)
        
        elif aksi == "baca":
            if not path:
                return {"sukses": False, "error": "Path harus diisi"}
            return te.baca_file(path)
        
        # === TERMINAL ===
        elif aksi == "terminal":
            if not perintah:
                return {"sukses": False, "error": "Perintah harus diisi"}
            return te.jalankan_terminal(perintah)
        
        # === FIX ===
        elif aksi == "fix_bug":
            if not file_path:
                return {"sukses": False, "error": "File path harus diisi"}
            return te.fix_bug(file_path)
        
        elif aksi == "analisis":
            if not file_path:
                return {"sukses": False, "error": "File path harus diisi"}
            return te.analisis_file(file_path)
        
        # === FOLDER ===
        elif aksi == "scan":
            return te.scan_folder(folder or "E:/Project Software/Orion")
        
        elif aksi == "list":
            return te.list_file(folder or ".")
        
        # === DEFAULT ===
        else:
            return {
                "sukses": False,
                "error": f"Aksi tidak dikenal: {aksi}",
                "aksi_tersedia": [
                    "buka_notepad", "buka_vscode", "buka_cmd", "buka_powershell",
                    "buka_windows_terminal", "buka_vs2022", "buka_file",
                    "tulis", "baca", "terminal", "fix_bug", "analisis", "scan", "list",
                ],
            }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


if __name__ == "__main__":
    print("=== Test coding_tool ===")
    
    # Test list
    print("\n[1] List folder:")
    hasil = jalankan(aksi="list", folder="E:/Project Software/Orion")
    print(f"  Sukses: {hasil.get('sukses')}")
    if hasil.get('sukses'):
        print(f"  Items: {len(hasil.get('items', []))}")
    
    # Test scan
    print("\n[2] Scan folder coding:")
    hasil = jalankan(aksi="scan", folder="E:/Project Software/Orion/coding")
    print(f"  Sukses: {hasil.get('sukses')}")
