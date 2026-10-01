"""
orion_hub.py - Pusat Saraf Orion.
Pintu masuk semua modul + health check + registry skill.
"""
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))


# ============ HEALTH CHECK ============
def cek_kesehatan(verbose=True):
    """Cek semua modul hidup."""
    modul = [
        # Core
        ("orion_neural", "Neural Hub"),
        ("otak_orion", "Otak Utama"),
        ("tool_eksekusi", "Tool Eksekusi"),
        ("core", "Core System"),
        # Saraf
        ("thinker_orion", "Thinker"),
        ("memory_manager", "Memory"),
        ("experience_hub", "Experience"),
        ("emotion_orion", "Emotion"),
        ("emotion_decay", "Emotion Decay"),
        ("mood_orion", "Mood"),
        # Coding
        ("coding_assistant", "Coding Assistant"),
        ("model_router", "LLM Router"),
        # Workflow
        ("workflow_engine", "Workflow Engine"),
        # Voice
        ("voice_orion", "Voice"),
        ("tts_orion", "TTS"),
    ]
    
    hasil = {"hidup": [], "error": []}
    
    for nama, label in modul:
        try:
            __import__(nama)
            hasil["hidup"].append((nama, label))
            if verbose:
                print(f"  ✅ {label:20} ({nama})")
        except Exception as e:
            hasil["error"].append((nama, label, str(e)))
            if verbose:
                print(f"  ❌ {label:20} ({nama}): {e}")
    
    if verbose:
        print()
        print(f"  Total: {len(hasil['hidup'])} hidup, {len(hasil['error'])} error")
    
    return hasil


# ============ REGISTRY SKILL ============
def daftar_skill():
    """Daftar semua skill dari folder skills/."""
    skills_dir = BASE / "skills"
    if not skills_dir.exists():
        return []
    
    hasil = []
    for f in skills_dir.glob("*.md"):
        hasil.append(f.stem)
    for d in skills_dir.iterdir():
        if d.is_dir():
            sk = d / "SKILL.md"
            if sk.exists():
                hasil.append(d.name)
    
    return sorted(set(hasil))


# ============ PINTU MASUK ============
def proses(pesan, mode="auto"):
    """
    Pintu masuk utama Orion.
    Panggil dari semua jalur: chat, Discord, voice.
    
    Args:
        pesan: pesan user
        mode: "auto" (default), "chat", "voice"
    
    Returns:
        dict {sukses, jawaban, intent, ...}
    """
    hasil = {
        "sukses": False,
        "pesan": pesan,
        "mode": mode,
        "neural": None,
        "intent": None,
        "jawaban": "",
    }
    
    # 1. Neural hub - sudah dipanggil di otak_orion
    # (tidak dipanggil di sini biar tidak duplikat)
    
    
    # 2. Panggil otak_orion
    try:
        from otak_orion import diskusi_orion
        jawaban = diskusi_orion(pesan)
        hasil["sukses"] = True
        hasil["jawaban"] = jawaban
    except Exception as e:
        hasil["error"] = str(e)
        print(f"[Hub] Otak error: {e}")
    
    return hasil


def proses_voice(teks):
    """Pintu masuk khusus voice - panggil otak_orion."""
    return proses(teks, mode="voice")


# ============ INFO ============
def info():
    """Info Orion - versi, modul, skill."""
    print("=" * 60)
    print("  ORION HUB - INFO")
    print("=" * 60)
    print()
    
    # Versi
    print("📌 Versi: 3.0 (Neural Hub Edition)")
    print(f"📁 Base: {BASE}")
    print()
    
    # Health
    print("🩺 Health Check:")
    hasil = cek_kesehatan(verbose=False)
    print(f"  ✅ Hidup: {len(hasil['hidup'])} modul")
    print(f"  ❌ Error: {len(hasil['error'])} modul")
    print()
    
    # Skill
    skills = daftar_skill()
    print(f"🎯 Skill: {len(skills)}")
    for s in skills[:10]:
        print(f"  - {s}")
    if len(skills) > 10:
        print(f"  ... dan {len(skills) - 10} lainnya")
    print()
    
    # File
    print("📄 File Utama:")
    utama = ["orion.py", "otak_orion.py", "orion_neural.py", 
             "tool_eksekusi.py", "experience_hub.py", "emotion_decay.py"]
    for f in utama:
        p = BASE / f
        if p.exists():
            size = p.stat().st_size
            print(f"  ✅ {f:25} ({size:,} B)")
        else:
            print(f"  ❌ {f:25} (tidak ada)")


# ============ TEST ============
if __name__ == "__main__":
    info()