"""code_generator.py - Orion tulis kode (Level 3)."""
import os
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
sys.path.insert(0, str(BASE / "core" / "otonom" / "evolusi"))

from safety import cek_kode_aman, cek_path_aman

# === Groq Config ===
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

# === Output folder ===
OUTPUT_DIR = BASE / "core" / "otonom" / "evolusi" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def panggil_llm(prompt: str, max_tokens: int = 2000) -> str:
    """Panggil LLM untuk generate kode."""
    if not GROQ_KEY:
        return ""
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu programmer Python expert. Tulis kode bersih, aman, dan efisien. Selalu sertakan docstring."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    
    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[CodeGen] Error: {e}")
        return ""


def extract_code(teks: str) -> str:
    """Extract kode dari markdown."""
    # Cari code block
    import re
    
    # Pattern ```python ... ```
    match = re.search(r'```python\s*\n(.*?)```', teks, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Pattern ``` ... ```
    match = re.search(r'```\s*\n(.*?)```', teks, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Kalau tidak ada code block, return teks
    return teks.strip()


def generate_fungsi(deskripsi: str, nama_fungsi: str = None) -> dict:
    """
    Generate fungsi Python dari deskripsi.
    
    Args:
        deskripsi: Deskripsi fungsi
        nama_fungsi: Nama fungsi (opsional)
    
    Returns:
        {
            "sukses": bool,
            "kode": str,
            "path": str,
            "alasan": str,
        }
    """
    if not nama_fungsi:
        # Generate nama dari deskripsi
        nama_fungsi = "fungsi_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    
    prompt = f"""Tulis fungsi Python dengan spesifikasi:

Nama: {nama_fungsi}
Deskripsi: {deskripsi}

Aturan:
- Sertakan docstring
- Sertakan type hints
- Sertakan error handling
- Jangan pakai import berbahaya (os.system, subprocess, eval, exec)
- Maksimal 200 baris
- Kode harus bisa jalan standalone

Tulis HANYA kode (dalam code block ```python):"""
    
    print(f"[CodeGen] Generate: {nama_fungsi}")
    hasil = panggil_llm(prompt)
    
    if not hasil:
        return {"sukses": False, "kode": "", "path": "", "alasan": "LLM gagal"}
    
    kode = extract_code(hasil)
    
    # Cek keamanan kode
    aman, alasan = cek_kode_aman(kode)
    if not aman:
        return {"sukses": False, "kode": kode, "path": "", "alasan": f"Kode tidak aman: {alasan}"}
    
    # Simpan ke file
    file_path = OUTPUT_DIR / f"{nama_fungsi}.py"
    
    # Cek path aman
    aman, alasan = cek_path_aman(str(file_path))
    if not aman:
        return {"sukses": False, "kode": kode, "path": "", "alasan": f"Path tidak aman: {alasan}"}
    
    # Tulis file
    file_path.write_text(kode, encoding="utf-8")
    
    print(f"[CodeGen] OK: {file_path.name} ({len(kode)} char)")
    
    return {
        "sukses": True,
        "kode": kode,
        "path": str(file_path),
        "alasan": "Berhasil",
    }


def generate_kelas(deskripsi: str, nama_kelas: str) -> dict:
    """Generate kelas Python dari deskripsi."""
    prompt = f"""Tulis kelas Python dengan spesifikasi:

Nama: {nama_kelas}
Deskripsi: {deskripsi}

Aturan:
- Sertakan docstring
- Sertakan __init__
- Sertakan method yang relevan
- Jangan pakai import berbahaya
- Maksimal 200 baris
- Sertakan contoh penggunaan di __main__

Tulis HANYA kode (dalam code block ```python):"""
    
    print(f"[CodeGen] Generate kelas: {nama_kelas}")
    hasil = panggil_llm(prompt)
    
    if not hasil:
        return {"sukses": False, "kode": "", "path": "", "alasan": "LLM gagal"}
    
    kode = extract_code(hasil)
    
    aman, alasan = cek_kode_aman(kode)
    if not aman:
        return {"sukses": False, "kode": kode, "path": "", "alasan": f"Kode tidak aman: {alasan}"}
    
    file_path = OUTPUT_DIR / f"{nama_kelas}.py"
    
    aman, alasan = cek_path_aman(str(file_path))
    if not aman:
        return {"sukses": False, "kode": kode, "path": "", "alasan": f"Path tidak aman: {alasan}"}
    
    file_path.write_text(kode, encoding="utf-8")
    print(f"[CodeGen] OK: {file_path.name}")
    
    return {
        "sukses": True,
        "kode": kode,
        "path": str(file_path),
        "alasan": "Berhasil",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST CODE GENERATOR")
    print("=" * 60)
    
    # Test generate fungsi
    print("\n=== Test Generate Fungsi ===")
    hasil = generate_fungsi(
        "Fungsi untuk menghitung faktorial dari angka n",
        "hitung_faktorial"
    )
    
    if hasil["sukses"]:
        print(f"  OK: {hasil['path']}")
        print(f"  Kode preview:")
        print("  " + "\n  ".join(hasil["kode"].split("\n")[:10]))
    else:
        print(f"  X: {hasil['alasan']}")
