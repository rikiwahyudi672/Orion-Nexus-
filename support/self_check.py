import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""self_check.py - Self-check otomatis Orion sebelum output."""
import sys
import ast
import re
from pathlib import Path

BASE = Path(__file__).parent
SKILLS_DIR = BASE.parent / "skills"


class SelfCheck:
    """Self-check otomatis - cek kekurangan sebelum output."""
    
    def __init__(self):
        self.masalah = []
        self.perbaikan = []
    
    def cek_kode(self, kode):
        """Cek kode - syntax, struktur, kualitas."""
        # 1. Cek syntax
        try:
            ast.parse(kode)
        except SyntaxError as e:
            self.masalah.append(f"Syntax error: {e}")
            return False
        
        # 2. Cek markdown
        if "```" in kode:
            self.masalah.append("Ada markdown di kode")
        
        # 3. Cek docstring
        if "def " in kode and '"""' not in kode:
            self.masalah.append("Tidak ada docstring")
        
        # 4. Cek if __name__
        if "def " in kode and 'if __name__' not in kode:
            self.masalah.append("Tidak ada if __name__")
        
        # 5. Cek input()
        if "input(" in kode:
            self.masalah.append("Ada input() - bisa gagal di test")
        
        return len(self.masalah) == 0
    
    def perbaiki_kode(self, kode):
        """Perbaiki kode otomatis."""
        kode = re.sub(r"```\w*\n?", "", kode)
        kode = kode.replace("```", "")
        kode = kode.lstrip("\ufeff")
        self.perbaikan.append("Markdown & BOM dihapus")
        return kode
    
    def lapor(self):
        """Lapor hasil self-check."""
        if self.masalah:
            print(f"[SelfCheck] {len(self.masalah)} masalah:")
            for m in self.masalah:
                print(f"  - {m}")
        else:
            print("[SelfCheck] OK - tidak ada masalah")


def cek_dan_perbaiki(kode):
    """Cek & perbaiki kode otomatis."""
    sc = SelfCheck()
    sc.cek_kode(kode)
    if sc.masalah:
        kode = sc.perbaiki_kode(kode)
    sc.lapor()
    return kode


if __name__ == "__main__":
    kode_test = """```python
def tambah(a, b):
    return a + b
```"""
    hasil = cek_dan_perbaiki(kode_test)
    print(hasil)


# ============ ALIAS UNTUK KOMPATIBILITAS ============
# Ditambahkan otomatis oleh Orion
cek_semua = cek_dan_perbaiki  # alias dari cek_dan_perbaiki

