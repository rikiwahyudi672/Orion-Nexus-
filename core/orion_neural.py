import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
orion_neural.py - Saraf Pusat Orion.
Semua modul terhubung: emosi, memory, intent, skill, tool, workflow.
"""
import os
import re
from pathlib import Path

# ============ EMOTION CHECK ============
def cek_emosi(pesan):
    """Deteksi emosi user dari pesan."""
    p = pesan.lower()
    
    # Emosi negatif
    if any(k in p for k in ["capek", "lelah", "pusing", "sedih", "galau", "bete", "badmood"]):
        return "capek"
    if any(k in p for k in ["marah", "kesal", "jengkel", "muak", "benci"]):
        return "marah"
    if any(k in p for k in ["takut", "cemas", "khawatir", "panik"]):
        return "cemas"
    
    # Emosi positif
    if any(k in p for k in ["senang", "seneng", "happy", "bahagia", "syukur", "alhamdulillah"]):
        return "senang"
    if any(k in p for k in ["semangat", "gas", "ayo", "yuk"]):
        return "semangat"
    
    return "netral"


def mode_respond(emosi):
    """Pilih mode respond berdasarkan emosi."""
    if emosi in ("capek", "sedih", "cemas"):
        return "calm"     # Santai, empati, tidak ambisius
    if emosi == "marah":
        return "tenang"   # Tenang, jangan bikin makin marah
    if emosi in ("senang", "semangat"):
        return "antusias" # Antusias, support
    return "normal"


# ============ MEMORY CHECK ============
def cek_memory_positif(jumlah=3):
    """Ambil memory positif (filter negatif)."""
    try:
        import memory_manager
        konteks = memory_manager.ambil_konteks(jumlah)
        if not konteks:
            return []
        
        kata_negatif = ["dimaki", "maki", "sedih", "marah", "kesal", 
                        "capek", "bete", "badmood", "benci", "nyerah"]
        
        hasil = []
        for k in konteks:
            user_msg = k.get("user", "").lower()
            orion_msg = k.get("orion", "").lower()
            if any(kn in user_msg or kn in orion_msg for kn in kata_negatif):
                continue
            hasil.append(k)
        return hasil
    except Exception:
        return []


# ============ INTENT DETECT ============
def deteksi_intent(pesan):
    """Deteksi intent utama."""
    p = pesan.lower().strip()
    
    # Coding
    for pola in ["coding ", "buatkan kode", "buat program", "bikin aplikasi", "generate code"]:
        if p.startswith(pola):
            return "coding"
    
    # Analisis
    if p.startswith("analisis ") or p.startswith("analisa "):
        return "analisis"
    
    # Fix
    if p.startswith("fix ") or p.startswith("perbaiki "):
        return "fix"
    
    # Terminal
    for pola in ["jalankan ", "buka cmd", "buka powershell", "buka windows terminal", 
                 "buka vs 2022", "buka vscode", "buka notepad", "buka file "]:
        if p.startswith(pola):
            return "terminal"
    
    # File ops
    for pola in ["hapus file ", "copy file ", "buat folder ", "list file ", 
                 "tulis file ", "baca file ", "scan folder "]:
        if p.startswith(pola):
            return "file"
    
    # Git
    if p.startswith("git ") or p.startswith("jalankan test"):
        return "git"
    
    # Search
    if p.startswith("cari string ") or p.startswith("cari kata "):
        return "search"
    
    # Workflow
    if p.startswith("workflow ") or p == "daftar workflow":
        return "workflow"
    
    # System
    if p in ("screenshot", "status") or p.startswith("volume") or p.startswith("brightness"):
        return "system"
    
    # Jarvis
    if p.startswith("suruh jarvis ") or p.startswith("panggil jarvis "):
        return "jarvis"
    
    # Self-skill
    if p.startswith("fix baris ") or p.startswith("fix fungsi ") or p.startswith("tambah skill "):
        return "self_skill"
    
    # Default: chat
    return "chat"


# ============ SKILL SELECT ============
def cari_skill_relevan(pesan, max_hasil=2):
    """Cari skill relevan dari folder skill/ (sub-folder + SKILL.md)."""
    from pathlib import Path
    skills_dir = Path(__file__).parent.parent / "skill"
    if not skills_dir.exists():
        return []
    
    p = pesan.lower()
    hasil = []
    
    # Scan sub-folder skill
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith(("__", ".")):
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            
            # Ambil nama & deskripsi dari SKILL.md
            nama = skill_dir.name.replace("-", " ").replace("_", " ")
            deskripsi = ""
            
            for line in content.split(chr(10)):
                line = line.strip()
                if line.startswith("name:"):
                    nama = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("description:"):
                    deskripsi = line.split(":", 1)[1].strip().strip('"').strip("'")
            
            # Hitung skor - dari nama + deskripsi
            teks_skill = (nama + " " + deskripsi).lower()
            kata_kunci = teks_skill.split()
            skor = sum(1 for k in kata_kunci if k in p and len(k) > 2)
            
            if skor > 0:
                hasil.append({
                    "nama": nama,
                    "folder": skill_dir.name,
                    "skor": skor,
                    "file": str(skill_md),
                    "deskripsi": deskripsi,
                })
        except Exception:
            pass
    
    hasil.sort(key=lambda x: x["skor"], reverse=True)
    return hasil[:max_hasil]


# ============ WORKFLOW ============
WORKFLOWS = {
    "coding": [
        ("coding_loop", "Generate + fix kode"),
        ("test", "Test hasil"),
        ("lapor", "Lapor ke user"),
    ],
    "analisis": [
        ("analisis", "Analisis file/folder"),
        ("lapor", "Lapor bug"),
    ],
    "fix": [
        ("backup", "Backup file"),
        ("fix", "Fix bug"),
        ("test", "Test syntax"),
    ],
    "chat": [
        ("cek_emosi", "Cek emosi user"),
        ("jawab", "Jawab natural"),
    ],
}


def buat_workflow(intent):
    """Buat workflow step-by-step."""
    return WORKFLOWS.get(intent, WORKFLOWS["chat"])


# ============ PROSES NEURAL ============
def proses_neural(pesan):
    """
    Proses input lewat semua saraf.
    Return: dict dengan info lengkap.
    """
    hasil = {}
    
    # 1. Emosi
    emosi = cek_emosi(pesan)
    hasil["emosi"] = emosi
    hasil["mode"] = mode_respond(emosi)
    
    # 2. Memory
    memory = cek_memory_positif(jumlah=3)
    hasil["memory"] = memory
    hasil["memory_count"] = len(memory)
    
    # 3. Intent
    intent = deteksi_intent(pesan)
    hasil["intent"] = intent
    
    # 4. Skill
    skill = cari_skill_relevan(pesan)
    hasil["skill"] = skill
    hasil["skill_count"] = len(skill)
    
    # 5. Workflow
    workflow = buat_workflow(intent)
    hasil["workflow"] = workflow
    
    # 6. Print log
    print(f"[Neural] Emosi: {emosi} → Mode: {hasil['mode']}")
    print(f"[Neural] Memory: {len(memory)} chat positif")
    print(f"[Neural] Intent: {intent}")
    print(f"[Neural] Skill: {len(skill)} relevan")
    print(f"[Neural] Workflow: {len(workflow)} langkah")
    
    return hasil


# ============ TEST ============
if __name__ == "__main__":
    print("=== TEST ORION NEURAL ===")
    print()
    
    tests = [
        "halo Orion",
        "coding buat Flask app",
        "gue capek banget hari ini",
        "analisis folder E:\\proyek",
        "buat folder test",
        "apa realistis buat program?",
    ]
    
    for t in tests:
        print(f"Pesan: {t}")
        hasil = proses_neural(t)
        print()