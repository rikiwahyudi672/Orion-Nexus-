"""
dashboard_orion.py - Dashboard utama ORION.
Simple, modern, warna + emoji. Bisa ketik & voice.
"""
import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

import core
try:
    import version_orion
except Exception:
    version_orion = None
try:
    import sapaan_orion
    import sapaan_dashboard
except Exception:
    sapaan_orion = None

try:
    import voice_lines
except Exception:
    voice_lines = None

try:
    import inisiatif_orion
except Exception:
    inisiatif_orion = None

try:
    import otak_orion
    
    # Import tool loop
    try:
        from orion_tool_loop import chat as tool_loop_chat
        HAS_TOOL_LOOP = True
        print("[Dashboard] Tool loop loaded")
    except ImportError as e:
        HAS_TOOL_LOOP = False
        print(f"[Dashboard] Tool loop error: {e}")
except Exception:
    otak_orion = None

try:
    import monitor_orion
except Exception:
    monitor_orion = None

try:
    import cron_orion
except Exception:
    cron_orion = None

try:
    import voice_stream
except Exception:
    voice_stream = None

# === SUARA ORION (colok_suara.py) ===
_SUARA_ON = True  # default: ORION bersuara via Supertonic F1; ketik 'suara off' di chat untuk bisu

def _bersihkan_untuk_suara(teks):
    """Bersihkan emoji & markdown biar enak diucapkan TTS. Fail-safe."""
    try:
        import re
        teks = re.sub(r'\*+', '', str(teks))
        teks = re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]', '', teks)
        teks = re.sub(r'\s+', ' ', teks).strip()
        return teks
    except Exception:
        return teks

# ============ WARNA ============
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[38;5;75m"
    BLUE = "\033[38;5;117m"
    YELLOW = "\033[38;5;220m"
    GREEN = "\033[38;5;114m"
    RED = "\033[38;5;203m"
    GRAY = "\033[38;5;245m"
    WHITE = "\033[97m"
    PROMPT = "\033[38;5;80m"


def c(t, color):
    return f"{color}{t}{C.RESET}"


def lebar_terminal():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def garis(kiri, isi, kanan, warna=C.CYAN):
    print(c(f"{kiri}{isi}{kanan}", warna))


def logo_animasi():
    """Wordmark ORION ramping. (rapihin_cli 30/09)"""
    try:
        _ver = version_orion.__version__ if version_orion else "2.7"
    except Exception:
        _ver = "2.7"
    print(c("      ✦", C.CYAN))  # tambah_logo 30/09
    print(c("    ✦   ✦", C.CYAN))
    print(c("  ✦  ", C.CYAN) + c("O", C.CYAN + C.BOLD) + c("  ✦", C.CYAN))
    print(c("    ✦   ✦", C.CYAN))
    print(c("      ✦", C.CYAN))
    print(c("  ORION", C.CYAN + C.BOLD)
          + c(f"   ·   personal ai assistant   ·   v{_ver}   ·   unified edition", C.GRAY))


def mood_emoji(mood):
    mapping = {
        "semangat": "🔥", "kalem": "😌", "perhatian": "🥺",
        "bosen": "😑", "kesepian": "😔", "frustasi": "😤",
        "seneng": "😄", "sedih": "😢", "kesel": "😠",
        "marah": "🤬", "takut": "😰", "kaget": "😱",
        "lelah": "😪", "cuek": "😐", "bangga": "😎",
    }
    return mapping.get(mood, "🙂")


def mood_warna(mood):
    mapping = {
        "semangat": C.YELLOW, "kalem": C.CYAN, "perhatian": C.BLUE,
        "bosen": C.GRAY, "kesepian": C.GRAY, "frustasi": C.RED,
        "seneng": C.GREEN, "sedih": C.BLUE, "kesel": C.RED,
        "marah": C.RED, "takut": C.YELLOW, "kaget": C.YELLOW,
        "lelah": C.GRAY, "cuek": C.GRAY, "bangga": C.GREEN,
    }
    return mapping.get(mood, C.WHITE)


def info_mood_loyalty():
    """Tampilkan mood + loyalty + trust di header, satu baris kompak. (rapihin_cli 30/09)"""
    _parts = []
    try:
        import emotion_orion
        emo = emotion_orion.get_emotion()
        _parts.append(f"mood {emo['primary']} ({emo['primary_intensity']}/10)")
    except Exception:
        pass
    try:
        import loyalty_orion
        loy = loyalty_orion.get_loyalty()
        _parts.append(f"loyalty {loy['skor']}/100")
    except Exception:
        pass
    try:
        import emotion_orion
        rel = emotion_orion.get_relationship()
        _parts.append(f"trust {rel['trust']}/100 · intimacy {rel['intimacy']}/100")
    except Exception:
        pass
    if _parts:
        print(c("  " + "  ·  ".join(_parts), C.GRAY))


def header():
    """Header ramping tanpa ASCII raksasa. (rapihin_cli 30/09)"""
    os.system("cls" if os.name == "nt" else "clear")
    w = lebar_terminal()
    jam = datetime.now().strftime("%H:%M")
    tgl = datetime.now().strftime("%d/%m/%Y")

    print()
    logo_animasi()
    print(c(f"  {CFG_OWNER}  ·  {tgl} {jam}", C.GRAY))
    info_mood_loyalty()
    if sapaan_orion:
        print()
        try:
            print(c(f"  {sapaan_dashboard.sapaan()}", C.GRAY))
        except Exception:
            pass

    # Garis pemisah
    print(c("  " + "─" * (min(w - 4, 64)), C.GRAY))


def status_bar():
    """Bar status CPU/RAM/Disk."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("E:\\").percent if Path("E:\\").exists() else 0
        print(c(f"  cpu {cpu}%  ·  mem {ram}%  ·  disk e: {disk}%", C.GRAY))  # rapihin_cli
    except Exception:
        print(c("  (psutil tidak tersedia)", C.GRAY))


def menu_cepat():
    """Menu grid 3 kolom. (rapihin_cli 30/09)"""
    _menu = [
        ("1", "sistem"), ("2", "cari"), ("3", "memori"),
        ("4", "notif"), ("v", "voice"), ("i", "inisiatif"),
        ("c", "chat"), ("a", "aktivitas"), ("m", "model"),
        ("k", "cron"), ("0", "keluar"),
    ]
    print()
    for _i in range(0, len(_menu), 3):
        _sel = []
        for _k, _n in _menu[_i:_i + 3]:
            _w = C.RED if _k == "0" else C.GREEN
            _sel.append(c(f"[{_k}]", _w) + f" {_n:<10}")
        print("  " + "  ".join(_sel))
    print()


def input_prompt():
    """Ambil input dari user."""
    try:
        return input(c("  › ", C.PROMPT)).strip()  # rapihin_cli
    except (EOFError, KeyboardInterrupt):
        return "0"


# ============ SUBMENU ============

def submenu_sistem():
    print()
    print(c("  ── SISTEM ──", C.CYAN))
    print(c("  [1] 📊 Status lengkap", C.WHITE))
    print(c("  [2] 🔊 Volume", C.WHITE))
    print(c("  [3] ☀️  Brightness", C.WHITE))
    print(c("  [4] 🔌 Power", C.WHITE))
    print(c("  [0] ↩️  Kembali", C.GRAY))
    p = input_prompt()
    try:
        if p == "1": core.status_sistem()
        elif p == "2": core.volume()
        elif p == "3": core.brightness()
        elif p == "4": core.power()
    except Exception as e:
        print(c(f"  ⚠️  Error: {e}", C.RED))
    input(c("\n  [Enter] lanjut...", C.GRAY))


def submenu_cari():
    print()
    print(c("  ── CARI (Wikipedia) ──", C.CYAN))
    q = input(c("  Query: ", C.PROMPT)).strip()
    if not q:
        return
    print(c(f"  🔍 Mencari '{q}'...", C.GRAY))
    try:
        hasil = core.orion_cari(q, limit=5)
        print()
        for i, h in enumerate(hasil, 1):
            if "error" in h:
                print(c(f"  ⚠️  {h['error']}", C.RED))
                continue
            print(c(f"  [{i}] {h.get('judul','?')}", C.WHITE))
            print(c(f"      {h.get('ringkas','')[:120]}", C.GRAY))
            print(c(f"      {h.get('url','')}", C.BLUE))
            print()
    except Exception as e:
        print(c(f"  ⚠️  Error: {e}", C.RED))
    input(c("  [Enter] lanjut...", C.GRAY))


def submenu_memori():
    print()
    print(c("  ── MEMORI ──", C.CYAN))
    print(c("  [1] Lihat semua memori", C.WHITE))
    print(c("  [2] Cari memori", C.WHITE))
    print(c("  [3] Simpan memori baru", C.WHITE))
    print(c("  [0] ↩️  Kembali", C.GRAY))
    p = input_prompt()
    try:
        if p == "1":
            hasil = core.orion_recall(limit=20)
            for topik, isi in hasil:
                print(c(f"  • [{topik}] {isi}", C.WHITE))
        elif p == "2":
            q = input(c("  Kata kunci: ", C.PROMPT)).strip()
            for topik, isi in core.orion_recall(q, limit=10):
                print(c(f"  • [{topik}] {isi}", C.WHITE))
        elif p == "3":
            topik = input(c("  Topik: ", C.PROMPT)).strip()
            isi = input(c("  Isi: ", C.PROMPT)).strip()
            penting = input(c("  Penting? (0/1): ", C.PROMPT)).strip() or "0"
            core.orion_ingat(topik, isi, int(penting))
            print(c("  ✅ Tersimpan.", C.GREEN))
    except Exception as e:
        print(c(f"  ⚠️  Error: {e}", C.RED))
    input(c("\n  [Enter] lanjut...", C.GRAY))


def submenu_notif():
    print()
    print(c("  ── NOTIFIKASI ──", C.CYAN))
    judul = input(c("  Judul: ", C.PROMPT)).strip() or "Test"
    pesan = input(c("  Pesan: ", C.PROMPT)).strip() or "Halo dari Orion"
    penting = input(c("  Penting? (0/1): ", C.PROMPT)).strip() or "0"
    try:
        core.orion_notif(judul, pesan, int(penting))
        print(c("  ✅ Terkirim.", C.GREEN))
    except Exception as e:
        print(c(f"  ⚠️  Error: {e}", C.RED))
    input(c("\n  [Enter] lanjut...", C.GRAY))


def mode_voice():
    """Mode voice: rekam, transkrip, proses, jawab TTS."""
    print()
    print(c("  ── VOICE MODE ──", C.CYAN))
    print()

    # Cek modul
    try:
        import voice_orion
        import voice_lines as VL
    except Exception as e:
        print(c(f"  ⚠️  Voice modul error: {e}", C.RED))
        print(c("  Install: pip install faster-whisper edge-tts pygame-ce", C.GRAY))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    # Pembuka - pakai dinamis
    try:
        import voice_lines_dinamis
        kalimat_buka = voice_lines_dinamis.pembuka()
    except Exception:
        kalimat_buka = "Gue siap dengerin, Rik."
    print(c(f"  🎤 {kalimat_buka}", C.YELLOW))
    try:
        voice_orion.tts_bicara(kalimat_buka)
    except Exception:
        pass

    # Loop voice
    while True:
        print()
        print(c("  [R] Rekam (Right Ctrl)  [T] Ketik  [0] Kembali", C.GRAY))
        p = input(c("  Voice > ", C.PROMPT)).strip().lower()

        if p == "0":
            kalimat_tutup = VL.penutup() if VL else "Voice mode selesai."
            print(c(f"  👋 {kalimat_tutup}", C.CYAN))
            try:
                voice_orion.tts_bicara(kalimat_tutup)
            except Exception:
                pass
            return

        elif p == "t":
            teks = input(c("  Ketik: ", C.PROMPT)).strip()
            if not teks:
                continue
            _proses_voice(teks, voice_orion, VL)

        else:  # default: rekam
            print(c("  🎤 Tekan & tahan RIGHT CTRL untuk rekam...", C.YELLOW))
            try:
                teks = _rekam_dan_transkrip(voice_orion)
                if not teks:
                    kalimat = VL.bingung() if VL else "Gue nggak denger."
                    print(c(f"  ❓ {kalimat}", C.YELLOW))
                    try:
                        voice_orion.tts_bicara(kalimat)
                    except Exception:
                        pass
                    continue
                print(c(f"  📝 Lo: {teks}", C.WHITE))
                _proses_voice(teks, voice_orion, VL)
            except Exception as e:
                kalimat = VL.error() if VL else "Error."
                print(c(f"  ⚠️  {kalimat} ({e})", C.RED))


def _rekam_vad(min_detik=5, max_detik=20, silence_detik=1.5):
    """Rekam pakai VAD: minimal 5 detik, maksimal 20 detik, stop kalau silence.
    
    Returns:
        numpy array audio
    """
    import sounddevice as sd
    import numpy as np
    import webrtcvad
    import time
    
    sr = 16000
    frame_ms = 30
    frame_size = int(sr * frame_ms / 1000)
    
    vad = webrtcvad.Vad(2)  # 0-3, makin tinggi makin strict
    
    print(c(f"  🎤 Rekam (min {min_detik}s, max {max_detik}s)...", C.YELLOW))
    print(c("     Bicara sekarang. Berhenti ngomong = auto stop.", C.GRAY))
    
    # Stream rekam
    audio_chunks = []
    silence_frames = 0
    silence_frames_max = int(silence_detik * 1000 / frame_ms)
    min_frames = int(min_detik * 1000 / frame_ms)
    max_frames = int(max_detik * 1000 / frame_ms)
    total_frames = 0
    sudah_ngomong = False
    
    def callback(indata, frames, time_info, status):
        audio_chunks.append(indata.copy())
    
    try:
        with sd.InputStream(
            samplerate=sr,
            channels=1,
            dtype="int16",
            blocksize=frame_size,
            callback=callback,
        ):
            start_time = time.time()
            while total_frames < max_frames:
                time.sleep(frame_ms / 1000)
                total_frames += 1
                
                # Cek frame terakhir
                if len(audio_chunks) == 0:
                    continue
                
                # Ambil frame terakhir
                chunk = audio_chunks[-1].tobytes()
                if len(chunk) < frame_size * 2:
                    continue
                
                # Deteksi suara
                try:
                    is_speech = vad.is_speech(chunk[:frame_size * 2], sr)
                except Exception:
                    is_speech = False
                
                if is_speech:
                    sudah_ngomong = True
                    silence_frames = 0
                else:
                    silence_frames += 1
                
                # Progress
                elapsed = total_frames * frame_ms / 1000
                if total_frames % 10 == 0:
                    print(c(f"     ⏺️  {elapsed:.0f}s...", C.GRAY))
                
                # Stop condition
                if total_frames >= min_frames and sudah_ngomong:
                    if silence_frames >= silence_frames_max:
                        print(c(f"     ⏹️  Stop di {elapsed:.1f}s (silence)", C.GRAY))
                        break
    except Exception as e:
        print(c(f"  ⚠️  VAD error: {e}", C.RED))
        print(c("     Fallback ke rekam biasa...", C.GRAY))
        audio = sd.rec(int(min_detik * sr), samplerate=sr, channels=1, dtype="int16")
        sd.wait()
        return audio
    
    # Gabungin
    if audio_chunks:
        audio = np.concatenate(audio_chunks, axis=0)
    else:
        audio = np.zeros((sr, 1), dtype="int16")
    
    durasi_aktual = len(audio) / sr
    print(c(f"  ✅ Rekam selesai: {durasi_aktual:.1f}s", C.GREEN))
    return audio


def _rekam_dan_transkrip(voice_orion, durasi=10):
    """Rekam pakai PTT (tekan & lepas Right Ctrl)."""
    try:
        import voice_input_ptt
        print(c("  🎤 Tekan & tahan RIGHT CTRL untuk rekam", C.YELLOW))
        print(c("  🎤 Lepas RIGHT CTRL untuk stop", C.GRAY))
        teks = voice_input_ptt.rekam_dan_transkrip("tiny")
        return teks
    except Exception as e:
        print(c(f"  ⚠️  PTT error: {e}", C.RED))
        return ""


def _proses_voice(teks, voice_orion, VL):
    """Proses teks dari voice: pakai LLM Orion."""
    kalimat_dengar = VL.dengar() if VL else "Oke."
    print(c(f"  🤖 {kalimat_dengar}", C.GRAY))

    # Pakai otak Orion (LLM + skill + emotion + konteks)
    try:
        import otak_orion
        jawaban = otak_orion.diskusi_orion(teks)
        print(c(f"  🤖 {jawaban}", C.WHITE))
        # TTS streaming PAKAI jawaban yang sama (bukan generate ulang)
        try:
            import voice_stream
            # Potong per kalimat, TTS
            voice_stream.stream_dan_tts(
                teks,
                lambda p, history=None: iter([jawaban]),  # pakai jawaban yang sama
                lambda t: voice_orion.tts_bicara(t),
                history=None,
            )
        except Exception as e:
            print(c(f"  ⚠️  Streaming error: {e}", C.GRAY))
            try:
                voice_orion.tts_bicara(jawaban)
            except Exception:
                pass
    except Exception as e:
        kalimat = VL.error() if VL else "Error."
        print(c(f"  ⚠️  {kalimat} ({e})", C.RED))
        try:
            voice_orion.tts_bicara(kalimat)
        except Exception:
            pass


def submenu_inisiatif():
    """Atur inisiatif Orion (ngomong sendiri)."""
    print()
    print(c("  ── INISIATIF ORION ──", C.CYAN))
    if not inisiatif_orion:
        print(c("  ⚠️  Modul inisiatif tidak tersedia.", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    st = inisiatif_orion.status()
    status_txt = "AKTIF" if st["aktif"] else "MATI"
    warna = C.GREEN if st["aktif"] else C.RED
    print(c(f"  Status: {status_txt}", warna))
    print(c(f"  Interval: {st['interval_min']}-{st['interval_max']} menit", C.GRAY))
    print()
    print(c("  [1] Nyalakan (5-15 menit)", C.WHITE))
    print(c("  [2] Matikan", C.WHITE))
    print(c("  [3] Test cepat (10 detik sekali)", C.WHITE))
    print(c("  [4] Ngomong sekarang (paksa)", C.WHITE))
    print(c("  [0] ↩️  Kembali", C.GRAY))
    p = input_prompt()

    try:
        import voice_orion as VO
        tts = VO.tts_bicara
    except Exception:
        tts = None

    if p == "1":
        inisiatif_orion.stop()
        inisiatif_orion.mulai(tts_func=tts, min_menit=5, max_menit=15)
        print(c("  ✅ Inisiatif aktif. Orion bakal ngomong sendiri.", C.GREEN))
    elif p == "2":
        inisiatif_orion.stop()
        print(c("  🔇 Inisiatif dimatikan.", C.YELLOW))
    elif p == "3":
        inisiatif_orion.stop()
        inisiatif_orion.mulai(tts_func=tts, min_menit=0, max_menit=0)
        inisiatif_orion._interval_min = 0
        inisiatif_orion._interval_max = 0
        print(c("  🧪 Mode test. Orion ngomong tiap ~10 detik.", C.YELLOW))
    elif p == "4":
        k = inisiatif_orion._pilih_kalimat()
        print(c(f"  🤖 {k}", C.YELLOW))
        if tts:
            try:
                tts(k)
            except Exception:
                pass
    input(c("\n  [Enter] lanjut...", C.GRAY))


def submenu_chat():
    """Chat AI dengan Orion."""
    global _SUARA_ON  # colok_suara.py
    print()
    print(c("  ── chat ──", C.CYAN))  # rapihin_cli
    if not otak_orion:
        print(c("  ⚠️  otak_orion tidak tersedia.", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    # === MEMORI TAHAP 1: konsolidasi berkala (fail-safe) ===
    try:
        import konsolidasi_memory as _km
        if hasattr(_km, "konsolidasi_jika_perlu"):
            _km.konsolidasi_jika_perlu(hari=7)
    except Exception:
        pass

    prov = otak_orion.daftar_provider()
    if not prov:
        print(c("  ⚠️  Provider LLM tidak ada. Cek .env", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    print(c(f"  Provider: {', '.join(f'{k}={v}' for k,v in prov.items())}", C.GRAY))
    print(c("  Ketik 'exit' buat keluar, 'clear' buat reset history.", C.GRAY))
    print()

    history = []
    while True:
        try:
            user = input(c("  riki › ", C.PROMPT)).strip()  # rapihin_cli
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit", "0"):
            break
        if user.lower() == "clear":
            history = []
            print(c("  History direset.", C.GRAY))
            continue

        if user.lower() == "suara on":
            _SUARA_ON = True
            print(c("  🔊 Suara ORION: ON (Supertonic F1)", C.GREEN))
            continue
        if user.lower() == "suara off":
            _SUARA_ON = False
            print(c("  🔇 Suara ORION: OFF", C.GRAY))
            continue

        # === MODE CODING AKTIF ===
        if user.lower().startswith("coding "):
            goal = user[7:].strip()
            if not goal:
                print(c("  ⚠️  Contoh: coding buat REST API Flask", C.RED))
                continue
            print(c("  🚀 Mode coding aktif...", C.CYAN))
            print(c(f"  Goal: {goal}", C.GRAY))
            try:
                from coding_assistant import coding_loop
                hasil = coding_loop(goal, max_iterasi=3, nama_file="output_orion.py")
                if hasil.get("sukses"):
                    print(c(f"  ✅ Sukses - {hasil.get('file', '?')} (iterasi {hasil.get('iterasi', '?')})", C.GREEN))
                    print(c(f"  📁 Cek: output_orion.py", C.GRAY))
                else:
                    print(c(f"  ❌ Gagal: {hasil.get('error', '?')}", C.RED))
            except Exception as e:
                print(c(f"  ❌ Error: {e}", C.RED))
            print()
            continue

        # === MEMORI TAHAP 1: recall (fail-safe) ===
        _konteks_teks = ""
        try:
            import memory_manager as _mm
            _mm.init()
            _ctx = _mm.ambil_konteks(5) or []
            _kata_negatif = ["dimaki", "maki", "sedih", "marah", "kesal",
                             "capek", "bete", "badmood", "benci", "nyerah",
                             "salah", "maaf", "kenapa", "kesalahan", "error"]
            _cf = []
            for _k in _ctx:
                _gab = str(_k.get("user", "")) + " " + str(_k.get("orion", ""))
                if any(_kn in _gab.lower() for _kn in _kata_negatif):
                    continue
                _cf.append(_k)
            if _cf:
                _konteks_teks = "\n\n[KONTEKS PERCAKAPAN SEBELUMNYA]\n"
                for _k in _cf:
                    _konteks_teks += "User: " + str(_k.get("user", ""))[:100] + "\n"
                    _konteks_teks += "Orion: " + str(_k.get("orion", ""))[:100] + "\n"
        except Exception:
            _konteks_teks = ""
        if "[KONTEKS PERCAKAPAN SEBELUMNYA]" in user:  # TAHAP2 30/09: recall sudah ada -> jangan tempel lagi
            _konteks_teks = ""
        _user_full = user + _konteks_teks

        print(c("  orion mengetik…", C.GRAY))  # rapihin_cli
        try:
            # Pakai streaming kalau voice_stream tersedia
            if voice_stream and user.lower().startswith("s "):
                # Mode streaming: "s <pertanyaan>"
                pertanyaan = user[2:].strip()
                jawab = voice_stream.stream_jawab(pertanyaan + _konteks_teks, history=history)
                if not jawab:
                    jawab = "(streaming gagal)"
            else:
                # Pakai tool loop kalau tersedia
                if HAS_TOOL_LOOP:
                    try:
                        jawab = tool_loop_chat(_user_full, riwayat=history)
                    except Exception as e:
                        print(f"[Tool Loop Error] {e}")
                        jawab = otak_orion.diskusi_orion(_user_full, history=history)
                else:
                    jawab = otak_orion.diskusi_orion(_user_full, history=history)
            print(c("  orion › ", C.GREEN) + c(jawab, C.WHITE))  # rapihin_cli
            # === SUARA ORION (colok_suara.py): bacakan jawaban via Supertonic F1 ===
            if _SUARA_ON:
                try:
                    try:
                        from voice_orion import tts_bicara_stream as _bicara_f1
                    except Exception:
                        try:
                            from voice_orion import tts_bicara_natural as _bicara_f1
                        except Exception:
                            from voice_orion import tts_bicara as _bicara_f1
                    _teks_suara = _bersihkan_untuk_suara(jawab)
                    if _teks_suara:
                        _bicara_f1(_teks_suara)
                except Exception:
                    print(c("  (🔇 suara gagal, chat tetap jalan)", C.GRAY))
            print()
            history.append({"role": "user", "content": user})
            history.append({"role": "assistant", "content": jawab})
            # === MEMORI TAHAP 1: simpan (fail-safe) ===
            try:
                import memory_manager as _mm2
                _mm2.simpan_chat(user, jawab)
            except Exception:
                pass

            if len(history) > 20:
                history = history[-20:]
        except Exception as e:
            print(c(f"  ⚠️  Error: {e}", C.RED))


def submenu_aktivitas():
    """Lihat aktivitas laptop sekarang."""
    print()
    print(c("  ── AKTIVITAS LAPTOP ──", C.CYAN))
    if not monitor_orion:
        print(c("  ⚠️  monitor_orion tidak tersedia.", C.RED))
        print(c("  Install: pip install pygetwindow psutil", C.GRAY))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    r = monitor_orion.ringkasan()
    print()
    print(c(f"  🕐 {r['waktu']}", C.GRAY))
    print(c(f"  🖥️  CPU    : {r['cpu']}%", C.WHITE))
    print(c(f"  🧠 RAM    : {r['ram_pakai_gb']}/{r['ram_total_gb']} GB ({r['ram_persen']}%)", C.WHITE))
    print(c(f"  💾 Disk E : {r['disk_persen']}%", C.WHITE))
    if r["window"]:
        print(c(f"  🪟 Window : {r['window'][:60]}", C.YELLOW))
    print()
    if r["proses"]:
        print(c("  🔥 Proses berat:", C.CYAN))
        for p in r["proses"]:
            print(c(f"    - {p['nama']:30} CPU {p['cpu']}%  RAM {p['ram']}%", C.GRAY))

    print()
    opsi = input(c("  [K]omentar pakai AI? (y/n): ", C.PROMPT)).strip().lower()
    if opsi == "y" and otak_orion:
        print(c("  orion mengetik…", C.GRAY))  # rapihin_cli
        try:
            konteks = monitor_orion.teks_konteks()
            prompt = (
                f"Kondisi laptop Riki:\n{konteks}\n\n"
                "Kasih komentar 2-3 kalimat: kocak, sarkas, kadang bantah. "
                "Panggil dia 'bos' atau 'Riki'. Boleh kasih saran."
            )
            jawab = otak_orion.diskusi(prompt)
            print(c("  orion › ", C.GREEN) + c(jawab, C.YELLOW))  # rapihin_cli
        except Exception as e:
            print(c(f"  ⚠️  Error: {e}", C.RED))

    input(c("\n  [Enter] lanjut...", C.GRAY))


def submenu_ganti_model():
    """Ganti model LLM aktif."""
    print()
    print(c("  ── GANTI MODEL ──", C.CYAN))
    if not otak_orion:
        print(c("  ⚠️  otak_orion tidak tersedia.", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    model_aktif = otak_orion.get_model()
    prov_aktif = otak_orion.DEFAULT_PROVIDER
    print(c(f"  Provider: {prov_aktif}", C.GRAY))
    print(c(f"  Model aktif: {model_aktif}", C.YELLOW))
    print()

    pilihan = otak_orion.pilihan_model()
    if not pilihan:
        print(c("  ⚠️  Tidak ada preset model. Edit otak_orion.py bagian MODEL_PRESETS.", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    for i, m in enumerate(pilihan, 1):
        tanda = " ← aktif" if m == model_aktif else ""
        warna = C.GREEN if m == model_aktif else C.WHITE
        print(c(f"  [{i:2}] {m}{tanda}", warna))

    print()
    print(c("  [K] Ketik manual model lain", C.CYAN))
    print(c("  [0] ↩️  Kembali", C.GRAY))
    p = input_prompt()

    if p == "0":
        return
    elif p.lower() == "k":
        manual = input(c("  Nama model: ", C.PROMPT)).strip()
        if manual:
            ok, msg = otak_orion.set_model(manual)
            warna = C.GREEN if ok else C.RED
            print(c(f"  {'✅' if ok else '⚠️'} {msg}", warna))
    elif p.isdigit():
        idx = int(p) - 1
        if 0 <= idx < len(pilihan):
            ok, msg = otak_orion.set_model(pilihan[idx])
            warna = C.GREEN if ok else C.RED
            print(c(f"  {'✅' if ok else '⚠️'} {msg}", warna))
        else:
            print(c("  ⚠️  Nomor tidak valid.", C.RED))
    input(c("\n  [Enter] lanjut...", C.GRAY))


def submenu_cron():
    """Atur cron task."""
    print()
    print(c("  ── CRON SCHEDULER ──", C.CYAN))
    if not cron_orion:
        print(c("  ⚠️  cron_orion tidak tersedia.", C.RED))
        input(c("  [Enter] kembali...", C.GRAY))
        return

    st = cron_orion.status()
    status_txt = "AKTIF" if st["aktif"] else "MATI"
    warna = C.GREEN if st["aktif"] else C.RED
    print(c(f"  Status: {status_txt}", warna))
    print(c(f"  Total task: {st['total_tasks']}", C.GRAY))
    print()

    tasks = cron_orion.load_tasks()
    if tasks:
        for i, t in enumerate(tasks):
            aksi = t.get("aksi", "tts")
            isi = t.get("pesan") or t.get("prompt", "")
            if aksi == "llm":
                tanda = "🤖"
                label = isi[:50] if isi else "(LLM)"
            elif aksi == "maintenance":
                tanda = "🔧"
                label = "Maintenance harian (backup, health check)"
            else:
                tanda = "🔊"
                label = isi[:50] if isi else "(TTS)"
            print(c(f"  [{i:2}] {t['jam']} {tanda} {label}", C.WHITE))
    else:
        print(c("  (belum ada task)", C.GRAY))

    print()
    print(c("  [1] Nyalakan cron", C.GREEN))
    print(c("  [2] Matikan cron", C.RED))
    print(c("  [3] Tambah task", C.WHITE))
    print(c("  [4] Hapus task", C.WHITE))
    print(c("  [5] Edit file JSON manual", C.GRAY))
    print(c("  [0] ↩️  Kembali", C.GRAY))
    p = input_prompt()

    try:
        import voice_orion as VO
        tts = VO.tts_bicara
    except Exception:
        tts = None

    if p == "1":
        cron_orion.mulai(tts_func=tts)
        print(c("  ✅ Cron aktif.", C.GREEN))
    elif p == "2":
        cron_orion.stop()
        print(c("  🔇 Cron dimatikan.", C.YELLOW))
    elif p == "3":
        jam = input(c("  Jam (HH:MM): ", C.PROMPT)).strip()
        pesan = input(c("  Pesan: ", C.PROMPT)).strip()
        if jam and pesan:
            cron_orion.tambah_task(jam, pesan)
            print(c("  ✅ Task ditambahkan.", C.GREEN))
    elif p == "4":
        idx = input(c("  Nomor task: ", C.PROMPT)).strip()
        if idx.isdigit():
            if cron_orion.hapus_task(int(idx)):
                print(c("  ✅ Task dihapus.", C.GREEN))
            else:
                print(c("  ⚠️  Index tidak valid.", C.RED))
    elif p == "5":
        import os
        os.startfile(str(cron_orion.TASKS_FILE))
        print(c("  📝 File dibuka di editor default.", C.GRAY))
    input(c("\n  [Enter] lanjut...", C.GRAY))


# ============ MAIN LOOP ============

CFG_OWNER = "Riki Wahyudi"
try:
    import json
    _cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
    CFG_OWNER = _cfg.get("owner", CFG_OWNER)
except Exception:
    pass


def jalankan():
    """Jalankan dashboard + voice wake di background."""
    # Voice TIDAK auto-start - aktifkan manual dari menu V
    print("[Dashboard] Voice standby - tekan V untuk aktifkan")

    """Loop utama dashboard."""
    while True:
        header()
        status_bar()
        menu_cepat()

        p = input_prompt()

        if p == "0" or p.lower() == "q":
            print(c("\n  Sampai jumpa, Riki!\n", C.CYAN))  # rapihin_cli
            break
        elif p == "1":
            submenu_sistem()
        elif p == "2":
            submenu_cari()
        elif p == "3":
            submenu_memori()
        elif p == "4":
            submenu_notif()
        elif p.lower() == "v":
            # Cek status voice wake
            try:
                import voice_integrated
                status = voice_integrated.status()
                voice_aktif = status.get("aktif", False)
            except Exception:
                voice_aktif = False

            print()
            print(c("  === VOICE ORION ===", C.CYAN + C.BOLD))
            print()
            if voice_aktif:
                print(c("  Status: ", C.GRAY) + c("AKTIF", C.GREEN))
            else:
                print(c("  Status: ", C.GRAY) + c("TIDAK AKTIF", C.YELLOW))
            print()
            print(c("  [1] Aktifkan Voice Wake (background)", C.GREEN))
            print(c("  [2] Mode Voice (rekam PTT)", C.CYAN))
            print(c("  [3] Info Voice", C.CYAN))
            print(c("  [0] Kembali", C.GRAY))
            print()
            pilihan = input(c("  Pilih: ", C.PROMPT)).strip()

            if pilihan == "1":
                if voice_aktif:
                    print(c("  Voice sudah aktif", C.YELLOW))
                else:
                    try:
                        import voice_integrated
                        voice_integrated.start_voice()
                        print(c("  Voice wake aktif di background", C.GREEN))
                        print(c("  Bilang: 'Hai Orion'", C.CYAN))
                    except Exception as e:
                        print(c(f"  Error: {e}", C.RED))
                input(c("  [Enter] kembali...", C.GRAY))

            elif pilihan == "2":
                mode_voice()

            elif pilihan == "3":
                print()
                print(c("  Wake word  : ", C.GRAY) + c('"Hai Orion"', C.GREEN))
                print(c("  Tombol PTT : ", C.GRAY) + c("Right Ctrl", C.GREEN))
                print(c("  STT        : ", C.GRAY) + c("Groq", C.GREEN))
                print()
                input(c("  [Enter] kembali...", C.GRAY))
        elif p.lower() == "i":
            submenu_inisiatif()
        elif p.lower() == "c":
            submenu_chat()
        elif p.lower() == "a":
            submenu_aktivitas()
        elif p.lower() == "m":
            submenu_ganti_model()
        elif p.lower() == "k":
            submenu_cron()
        elif p:
            # Anggap sebagai query pencarian
            print(c(f"  🔍 Mencari '{p}'...", C.GRAY))
            try:
                hasil = core.orion_cari(p, limit=3)
                for h in hasil:
                    if "error" in h:
                        print(c(f"  ⚠️  {h['error']}", C.RED))
                        continue
                    print(c(f"  • {h.get('judul','?')}", C.WHITE))
                    print(c(f"    {h.get('ringkas','')[:100]}", C.GRAY))
            except Exception as e:
                print(c(f"  ⚠️  Error: {e}", C.RED))
            input(c("\n  [Enter] lanjut...", C.GRAY))


if __name__ == "__main__":
    jalankan()

# ============ ALIAS UNTUK KOMPATIBILITAS ============
buat_dashboard = jalankan  # alias dari jalankan

