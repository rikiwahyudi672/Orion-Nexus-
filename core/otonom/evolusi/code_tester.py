"""code_tester.py - Orion test kode (Level 3)."""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")


def test_syntax(file_path: str) -> dict:
    """Test syntax Python."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            kode = f.read()
        
        import ast
        ast.parse(kode)
        return {"sukses": True, "alasan": "Syntax valid"}
    except SyntaxError as e:
        return {"sukses": False, "alasan": f"Syntax error: baris {e.lineno}: {e.msg}"}
    except Exception as e:
        return {"sukses": False, "alasan": f"Error: {e}"}


def test_import(file_path: str) -> dict:
    """Test import module."""
    try:
        # Dapatkan nama module dari path
        p = Path(file_path)
        module_name = p.stem
        
        # Tambah folder ke sys.path
        sys.path.insert(0, str(p.parent))
        
        # Coba import
        __import__(module_name)
        
        return {"sukses": True, "alasan": "Import berhasil"}
    except Exception as e:
        return {"sukses": False, "alasan": f"Import error: {e}"}


def test_jalan(file_path: str, timeout: int = 10) -> dict:
    """Test jalankan file Python."""
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(file_path).parent),
        )
        
        if result.returncode == 0:
            return {
                "sukses": True,
                "alasan": "Berhasil jalan",
                "output": result.stdout[:500],
            }
        else:
            return {
                "sukses": False,
                "alasan": f"Exit code {result.returncode}",
                "error": result.stderr[:500],
            }
    except subprocess.TimeoutExpired:
        return {"sukses": False, "alasan": f"Timeout {timeout}s"}
    except Exception as e:
        return {"sukses": False, "alasan": f"Error: {e}"}


def test_lengkap(file_path: str) -> dict:
    """Test lengkap — syntax + import + jalan."""
    print(f"[CodeTest] Test: {Path(file_path).name}")
    
    hasil = {
        "file": file_path,
        "syntax": test_syntax(file_path),
        "import": test_import(file_path),
        "jalan": test_jalan(file_path),
    }
    
    # Sukses kalau syntax + import OK
    hasil["sukses"] = hasil["syntax"]["sukses"] and hasil["import"]["sukses"]
    
    print(f"  Syntax: {'OK' if hasil['syntax']['sukses'] else 'X'}")
    print(f"  Import: {'OK' if hasil['import']['sukses'] else 'X'}")
    print(f"  Jalan: {'OK' if hasil['jalan']['sukses'] else 'X'}")
    
    return hasil


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST CODE TESTER")
    print("=" * 60)
    
    # Test file yang baru dibuat
    output_dir = BASE / "core" / "otonom" / "evolusi" / "output"
    files = list(output_dir.glob("*.py"))
    
    if not files:
        print("[!] Belum ada file di output/")
    else:
        for f in files[:3]:
            print()
            hasil = test_lengkap(str(f))
