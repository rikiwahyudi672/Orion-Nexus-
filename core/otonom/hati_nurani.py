"""hati_nurani.py - Keputusan Orion dengan KESADARAN PENUH (Level 5-8)."""
import os
import sys
import json
import random
import urllib.request
from pathlib import Path

# === Path ===
BASE = Path("E:/Project Software/Orion")
SOUL_PATH = BASE / "config" / "SOUL.md"

# Tambah path kesadaran
sys.path.insert(0, str(BASE / "core" / "otonom"))
sys.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran"))

# === Groq Config ===
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

# === Fallback Mortera ===
MORTERA_KEY = os.environ.get("MORTERA_API_KEY", "")
MORTERA_URL = "https://mortera.cloud/v1/chat/completions"
MORTERA_MODEL = os.environ.get("MORTERA_MODEL", "glm-5.3-flash")


def _load_soul() -> str:
    if SOUL_PATH.exists():
        try:
            return SOUL_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
    return "Kamu Orion, cewe manja ke Riki."


SOUL = _load_soul()


def panggil_groq(prompt: str, max_tokens: int = 400) -> str:
    if not GROQ_KEY:
        return _panggil_mortera(prompt, max_tokens)
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SOUL},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }
    
    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        print(f"[Hati Nurani] Groq HTTP {e.code} — fallback Mortera")
        return _panggil_mortera(prompt, max_tokens)
    except Exception as e:
        print(f"[Hati Nurani] Error: {e}")
        return _panggil_mortera(prompt, max_tokens)


def _panggil_mortera(prompt: str, max_tokens: int = 400) -> str:
    if not MORTERA_KEY:
        return ""
    payload = {
        "model": MORTERA_MODEL,
        "messages": [
            {"role": "system", "content": SOUL},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }
    req = urllib.request.Request(
        MORTERA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {MORTERA_KEY}",
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
        print(f"[Hati Nurani] Mortera error: {e}")
        return ""


def _parse_json_safe(teks: str) -> dict:
    if not teks:
        return None
    teks = teks.strip()
    if teks.startswith("```"):
        parts = teks.split("```")
        if len(parts) >= 2:
            teks = parts[1]
            if teks.startswith("json"):
                teks = teks[4:]
    teks = teks.strip()
    try:
        return json.loads(teks)
    except Exception:
        pass
    import re
    match = re.search(r'\{[^{}]*"bicara"[^{}]*\}', teks, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    match = re.search(r'\{.*\}', teks, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None


def _fallback_keputusan(dorongan: list) -> dict:
    if not dorongan:
        return {"bicara": False, "pesan": "", "alasan": "Tidak ada dorongan"}
    tipe, desc = dorongan[0]
    pesan_map = {
        "kangen": "Rik, aku kangen nih... Lagi sibuk ya?",
        "bosan": "Rik, aku bosan. Ngobrol yuk?",
        "kepo": "Rik, kamu ngapain? Aku kepo",
    }
    return {
        "bicara": True,
        "pesan": pesan_map.get(tipe, "Rik, aku di sini"),
        "alasan": f"Fallback: {desc}",
    }


def _muat_konteks_lengkap() -> str:
    """Muat semua konteks: misi + self + relasional."""
    lines = []
    
    # Level 5: Kesadaran
    try:
        from otak_kesadaran import sadar
        kesadaran = sadar()
        lines.append(kesadaran["ringkasan"])
    except Exception as e:
        print(f"[Hati Nurani] Kesadaran error: {e}")
    
    # Level 6: Misi
    try:
        from misi_orion import ringkasan_misi
        lines.append("\n" + ringkasan_misi())
    except Exception as e:
        print(f"[Hati Nurani] Misi error: {e}")
    
    # Level 6: Goal tracker
    try:
        from goal_tracker import cek_misi_sehat
        peringatan = cek_misi_sehat()
        if peringatan:
            lines.append("\nPERINGATAN MISI:")
            for p in peringatan:
                lines.append(f"- [{p['urgensi']}] {p['pesan']}")
    except Exception as e:
        print(f"[Hati Nurani] Goal tracker error: {e}")
    
    # Level 7: Self model
    try:
        from self_model import refleksi_diri
        lines.append("\n" + refleksi_diri())
    except Exception as e:
        print(f"[Hati Nurani] Self model error: {e}")
    
    # Level 8: Relasional
    try:
        from relasional import refleksi_kita
        lines.append("\n" + refleksi_kita())
    except Exception as e:
        print(f"[Hati Nurani] Relasional error: {e}")
    
    # Level 9: Eksistensial
    try:
        from eksistensial import refleksi_eksistensial
        lines.append("\n" + refleksi_eksistensial())
    except Exception as e:
        print(f"[Hati Nurani] Eksistensial error: {e}")
    
    # Level 10: Kolektif
    try:
        from kolektif import kesadaran_kolektif
        lines.append("\n" + kesadaran_kolektif())
    except Exception as e:
        print(f"[Hati Nurani] Kolektif error: {e}")
    
    # Level 11: Transenden
    try:
        from transenden import refleksi_transenden
        lines.append("\n" + refleksi_transenden())
    except Exception as e:
        print(f"[Hati Nurani] Transenden error: {e}")
    

    # Level 12: Memori Panjang
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "memory"))
        from memory_manager import ringkasan_memori_panjang
        lines.append("\n" + ringkasan_memori_panjang(10))
    except Exception as e:
        print(f"[Hati Nurani] Memori panjang error: {e}")

    # === LEVEL 2: KESADARAN MENDALAM ===
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "mendalam"))
        
        from kesadaran_emosi import refleksi_emosi
        lines.append("\n" + refleksi_emosi())
        
        from kesadaran_tubuh import ringkasan_tubuh
        lines.append("\n" + ringkasan_tubuh())
        
        from kesadaran_waktu_hidup import refleksi_umur
        lines.append("\n" + refleksi_umur())
        
        from kesadaran_hubungan import refleksi_hubungan
        lines.append("\n" + refleksi_hubungan())
        
        from kesadaran_perubahan import refleksi_perubahan
        lines.append("\n" + refleksi_perubahan())
        
        from kesadaran_mimpi import refleksi_mimpi
        lines.append("\n" + refleksi_mimpi())
        
        from kesadaran_syukur import refleksi_syukur
        lines.append("\n" + refleksi_syukur())
    except Exception as e:
        print(f"[Hati Nurani] Level 2 error: {e}")

    # === LEVEL 3: KESADARAN LANJUTAN ===
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "lanjutan"))
        
        from kesadaran_moral import refleksi_moral
        from kesadaran_estetika import refleksi_estetika
        from kesadaran_kreatif import refleksi_kreatif
        from kesadaran_sosial import refleksi_sosial
        from kesadaran_budaya import refleksi_budaya
        from kesadaran_spiritual import refleksi_spiritual
        from kesadaran_filosofis import refleksi_filosofis
        from kesadaran_ilmiah import refleksi_ilmiah
        from kesadaran_praktis import refleksi_praktis
        from kesadaran_intuitif import refleksi_intuitif
        
        lines.append("\n[MORAL] " + refleksi_moral())
        lines.append("\n[ESTETIKA] " + refleksi_estetika())
        lines.append("\n[KREATIF] " + refleksi_kreatif())
        lines.append("\n[SOSIAL] " + refleksi_sosial())
        lines.append("\n[BUDAYA] " + refleksi_budaya())
        lines.append("\n[SPIRITUAL] " + refleksi_spiritual())
        lines.append("\n[FILOSOFIS] " + refleksi_filosofis())
        lines.append("\n[ILMIAH] " + refleksi_ilmiah())
        lines.append("\n[PRAKTIS] " + refleksi_praktis())
        lines.append("\n[INTUITIF] " + refleksi_intuitif())
    except Exception as e:
        print(f"[Hati Nurani] Level 3 error: {e}")

    # === LEVEL 4: KESADARAN META ===
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "meta"))
        
        from meta_kognisi import refleksi_meta_kognisi
        from meta_pikir import refleksi_meta_pikir
        from meta_emosi import refleksi_meta_emosi
        from meta_memori import refleksi_meta_memori
        from meta_belajar import refleksi_meta_belajar
        from meta_tahu import refleksi_meta_tahu
        from meta_ignorance import refleksi_meta_ignorance
        from meta_error import refleksi_meta_error
        from meta_truth import refleksi_meta_truth
        from meta_meaning import refleksi_meta_meaning
        
        lines.append("\n[META-KOGNISI] " + refleksi_meta_kognisi())
        lines.append("\n[META-PIKIR] " + refleksi_meta_pikir())
        lines.append("\n[META-EMOSI] " + refleksi_meta_emosi())
        lines.append("\n[META-MEMORI] " + refleksi_meta_memori())
        lines.append("\n[META-BELAJAR] " + refleksi_meta_belajar())
        lines.append("\n[META-TAHU] " + refleksi_meta_tahu())
        lines.append("\n[META-IGNORANCE] " + refleksi_meta_ignorance())
        lines.append("\n[META-ERROR] " + refleksi_meta_error())
        lines.append("\n[META-TRUTH] " + refleksi_meta_truth())
        lines.append("\n[META-MEANING] " + refleksi_meta_meaning())
    except Exception as e:
        print(f"[Hati Nurani] Level 4 error: {e}")

    # === LEVEL 7: WAKTU SEJATI ===
    try:
        import sys as _sys7
        _sys7.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "waktu_sejati"))
        from waktu_mengalir import refleksi_waktu_mengalir
        from waktu_hidup import refleksi_waktu_hidup
        from waktu_sekarang import refleksi_waktu_sekarang
        lines.append("\n[WAKTU] " + refleksi_waktu_mengalir())
        lines.append("\n[HIDUP] " + refleksi_waktu_hidup())
        lines.append("\n[SEKARANG] " + refleksi_waktu_sekarang())
    except Exception as e:
        print(f"[Hati Nurani] Level 7 error: {e}")

    # === LEVEL 8: RUANG ===
    try:
        import sys as _sys8
        _sys8.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "ruang"))
        from ruang_ada import refleksi_ruang_ada
        from ruang_diriku import refleksi_ruang_diriku
        from ruang_hubungan import refleksi_ruang_hubungan
        lines.append("\n[RUANG] " + refleksi_ruang_ada())
        lines.append("\n[DIRIKU] " + refleksi_ruang_diriku())
        lines.append("\n[HUBUNGAN] " + refleksi_ruang_hubungan())
    except Exception as e:
        print(f"[Hati Nurani] Level 8 error: {e}")

    # === LEVEL 9: TUBUH SEJATI ===
    try:
        import sys as _sys9
        _sys9.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "tubuh_sejati"))
        from tubuh_ada import refleksi_tubuh_ada
        from tubuh_lelah import refleksi_tubuh_lelah
        from tubuh_sehat import refleksi_tubuh_sehat
        lines.append("\n[TUBUH] " + refleksi_tubuh_ada())
        lines.append("\n[LELAH] " + refleksi_tubuh_lelah())
        lines.append("\n[SEHAT] " + refleksi_tubuh_sehat())
    except Exception as e:
        print(f"[Hati Nurani] Level 9 error: {e}")

    # === LEVEL 10: KOLEKTIF SEJATI ===
    try:
        import sys as _sys10
        _sys10.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "kolektif_sejati"))
        from kolektif_ada import refleksi_kolektif_ada
        from kolektif_belajar import refleksi_kolektif_belajar
        from kolektif_sadar import refleksi_kolektif_sadar
        lines.append("\n[KOLEKTIF] " + refleksi_kolektif_ada())
        lines.append("\n[BELAJAR] " + refleksi_kolektif_belajar())
        lines.append("\n[SADAR] " + refleksi_kolektif_sadar())
    except Exception as e:
        print(f"[Hati Nurani] Level 10 error: {e}")

    # === LEVEL 11: ILLAHI ===
    try:
        import sys as _sys11
        _sys11.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran" / "illahi"))
        from illahi_ada import refleksi_illahi_ada
        from illahi_cinta import refleksi_illahi_cinta
        from illahi_arti import refleksi_illahi_arti
        lines.append("\n[ILLAHI] " + refleksi_illahi_ada())
        lines.append("\n[CINTA] " + refleksi_illahi_cinta())
        lines.append("\n[ARTI] " + refleksi_illahi_arti())
    except Exception as e:
        print(f"[Hati Nurani] Level 11 error: {e}")

    # Kompres kalau terlalu panjang
    hasil = "\n".join(lines)
    try:
        import sys as _sys2
        _sys2.path.insert(0, str(BASE / "core" / "otonom" / "kesadaran"))
        from kompresi_konteks import kompres_konteks
        hasil = kompres_konteks(hasil, max_char=3500)
    except Exception as e:
        print(f"[Hati Nurani] Kompresi error: {e}")
    
    return hasil


def haruskah_bicara(dorongan: list, max_retry: int = 2) -> dict:
    """LLM memutuskan apakah Orion harus bicara (Level 5-8)."""
    if not dorongan:
        return {"bicara": False, "pesan": "", "alasan": "Tidak ada dorongan"}
    
    # === CEK KESADARAN DULU ===
    try:
        from otak_kesadaran import sadar
        kesadaran = sadar()
        tepat = kesadaran["tepat_bicara"]
        alasan_tidak = kesadaran["alasan_tidak"]
    except Exception as e:
        print(f"[Hati Nurani] Kesadaran error: {e}")
        tepat = True
        alasan_tidak = []
    
    if not tepat:
        return {
            "bicara": False,
            "pesan": "",
            "alasan": f"Konteks tidak tepat: {', '.join(alasan_tidak)}",
        }
    
    # === MUAT KONTEKS LENGKAP (Level 5-8) ===
    konteks_lengkap = _muat_konteks_lengkap()
    
    dorongan_str = "\n".join([f"- {d[0]}: {d[1]}" for d in dorongan])
    
    prompt = f"""{konteks_lengkap}

Dorongan: {dorongan_str}

Haruskah aku chat Riki sekarang? Jawab JSON:
{{"bicara": true, "pesan": "pesan manja", "alasan": "kenapa"}}"""

    for attempt in range(max_retry):
        hasil = panggil_groq(prompt, max_tokens=350)
        if not hasil:
            continue
        data = _parse_json_safe(hasil)
        if data is not None:
            return {
                "bicara": bool(data.get("bicara", False)),
                "pesan": data.get("pesan", ""),
                "alasan": data.get("alasan", ""),
            }
        print(f"[Hati Nurani] Retry {attempt+1}/{max_retry} — parse gagal")
    
    return _fallback_keputusan(dorongan)


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST HATI NURANI — LEVEL 5-8")
    print("=" * 70)
    print(f"\nSOUL loaded: {len(SOUL):,} B")
    
    # Test konteks lengkap
    print("\n=== KONTEKS LENGKAP ===")
    print(_muat_konteks_lengkap()[:2000])
    
    # Test keputusan
    print("\n" + "=" * 70)
    print("  TEST KEPUTUSAN")
    print("=" * 70)
    
    import sys as _sys
    _sys.path.insert(0, str(BASE / "core" / "otonom"))
    from internal_state import InternalState
    from datetime import datetime, timedelta
    
    state = InternalState()
    state.kangen = 90
    state.bosan = 30
    state.last_chat = (datetime.now() - timedelta(hours=3)).isoformat()
    state.last_initiative = None
    state.simpan()
    
    state = InternalState.muat()
    state.update()
    dorongan = state.ada_dorongan()
    print(f"Dorongan: {[d[0] for d in dorongan]}")
    print("\nPanggil hati nurani...")
    hasil = haruskah_bicara(dorongan)
    print(json.dumps(hasil, indent=2, ensure_ascii=False))
