"""anti_mojibake.py - Skill Orion cek & fix mojibake."""
import re
import shutil
from pathlib import Path
from datetime import datetime

# === PATTERN MOJIBAKE ===
# Pakai chr() biar aman dari encoding
PATTERNS = [
    # Emoji
    (chr(0xC3) + chr(0xB0) + chr(0xC5) + chr(0xB8) + chr(0xCB) + chr(0x9C) + chr(0xC2) + chr(0xA0), chr(0x1F60A)),  # 😊
    (chr(0xC3) + chr(0xB0) + chr(0xC5) + chr(0xB8) + chr(0xCB) + chr(0x9C) + chr(0xC2) + chr(0xA4), chr(0x1F624)),  # 😤
    (chr(0xC3) + chr(0xB0) + chr(0xC5) + chr(0xB8) + chr(0xC2) + chr(0xA5) + chr(0xC2) + chr(0xB0), chr(0x1F970)),  # 🥰
    (chr(0xC3) + chr(0xB0) + chr(0xC5) + chr(0xB8) + chr(0xE2) + chr(0x80) + chr(0x99) + chr(0xC2) + chr(0xA2), chr(0x1F495)),  # 💕
    (chr(0xC3) + chr(0xB0) + chr(0xC5) + chr(0xB8) + chr(0xC2) + chr(0xA4) + chr(0xE2) + chr(0x80) + chr(0x93), chr(0x1F916)),  # 🤖
    
    # Simbol
    (chr(0xC3) + chr(0xA2) + chr(0xE2) + chr(0x82) + chr(0xAC) + chr(0xE2) + chr(0x80) + chr(0x9D), chr(0x2014)),  # -
    (chr(0xC3) + chr(0xA2) + chr(0xE2) + chr(0x82) + chr(0xAC) + chr(0xE2) + chr(0x84) + chr(0xA2), chr(0x2019)),  # '
    (chr(0xC3) + chr(0xA2) + chr(0xE2) + chr(0x82) + chr(0xAC) + chr(0xC2) + chr(0xA2), chr(0x2022)),  # •
    (chr(0xC3) + chr(0xA2) + chr(0xE2) + chr(0x82) + chr(0xAC), chr(0x20AC)),  # €
    (chr(0xC3) + chr(0x82) + chr(0xC2) + chr(0xB7), chr(0xB7)),  # ·
    (chr(0xC3) + chr(0xA9), chr(0xE9)),  # é
    (chr(0xC3) + chr(0xA0), chr(0xE0)),  # à
]


def cek_mojibake(file_path):
    """Cek mojibake di file."""
    file_path = Path(file_path)
    if not file_path.exists():
        return {"error": f"File tidak ada: {file_path}"}
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e)}
    
    lines = content.split(chr(10))
    baris_mojibake = []
    
    for i, line in enumerate(lines, 1):
        for moji, _ in PATTERNS:
            if moji in line:
                baris_mojibake.append({
                    "baris": i,
                    "teks": line.strip()[:80],
                })
                break
    
    return {
        "file": str(file_path),
        "ada_mojibake": len(baris_mojibake) > 0,
        "jumlah_baris": len(baris_mojibake),
        "contoh": baris_mojibake[:5],
    }


def fix_mojibake(file_path, backup=True):
    """Fix mojibake di file."""
    file_path = Path(file_path)
    if not file_path.exists():
        return {"error": "File tidak ada", "sukses": False}
    
    backup_path = None
    if backup:
        backup_path = file_path.with_suffix(
            f"{file_path.suffix}.bak_moji_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(file_path, backup_path)
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e), "sukses": False}
    
    original = content
    count = 0
    
    for moji, asli in PATTERNS:
        if moji in content:
            n = content.count(moji)
            content = content.replace(moji, asli)
            count += n
    
    if content == original:
        return {
            "file": str(file_path),
            "sukses": True,
            "diperbaiki": 0,
            "backup": str(backup_path) if backup_path else None,
            "pesan": "Tidak ada mojibake",
        }
    
    file_path.write_text(content, encoding="utf-8")
    
    return {
        "file": str(file_path),
        "sukses": True,
        "diperbaiki": count,
        "backup": str(backup_path) if backup_path else None,
    }


def fix_folder(folder, pattern="*.py", exclude=None):
    """Fix mojibake di semua file dalam folder."""
    folder = Path(folder)
    exclude = exclude or ["arsip", "backup", "__pycache__", "node_modules"]
    
    hasil = []
    for f in folder.rglob(pattern):
        if any(x in str(f) for x in exclude):
            continue
        hasil.append(fix_mojibake(f))
    
    return hasil


def laporan(folder="E:/Project Software/Orion"):
    """Laporan mojibake."""
    print("=" * 70)
    print("  ANTI-MOJIBAKE - LAPORAN")
    print("=" * 70)
    
    folder = Path(folder)
    hasil = []
    for f in folder.rglob("*.py"):
        if any(x in str(f) for x in ["arsip", "backup", "__pycache__", "node_modules"]):
            continue
        hasil.append(cek_mojibake(f))
    
    ada = [h for h in hasil if h.get("ada_mojibake")]
    
    print(f"\nTotal dicek: {len(hasil)}")
    print(f"Ada mojibake: {len(ada)}")
    
    if ada:
        for h in ada[:20]:
            print(f"  {h['file']} - {h['jumlah_baris']} baris")
    else:
        print("\n✅ Tidak ada mojibake")
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        file = sys.argv[2] if len(sys.argv) > 2 else "E:/Project Software/Orion/orion_learn.py"
        
        if cmd == "cek":
            h = cek_mojibake(file)
            print(f"File: {h.get('file')}")
            print(f"Ada mojibake: {h.get('ada_mojibake')}")
            print(f"Baris: {h.get('jumlah_baris')}")
        elif cmd == "fix":
            h = fix_mojibake(file)
            print(f"File: {h.get('file')}")
            print(f"Sukses: {h.get('sukses')}")
            print(f"Diperbaiki: {h.get('diperbaiki')}")
        elif cmd == "laporan":
            laporan()
        elif cmd == "fix-folder":
            folder = sys.argv[2] if len(sys.argv) > 2 else "E:/Project Software/Orion"
            hasil = fix_folder(folder)
            total = sum(h.get("diperbaiki", 0) for h in hasil)
            print(f"File: {len(hasil)}")
            print(f"Diperbaiki: {total}")
    else:
        laporan()
