def _extract_nama_file(pesan):
    import re
    m = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', pesan)
    return m.group(1) if m else 'output_discord.py'


"""
discord_voice_orion_v2.py - Discord bot Orion dengan suara.
"""
import discord
import os
import asyncio
import io
import traceback


# ============ FUNGSI KIRIM PANJANG (CHUNKING) ============
async def kirim_panjang(channel, teks: str, prefix: str = ""):
    """Kirim pesan panjang — pecah jadi 2000 char per pesan."""
    MAX_LEN = 1900  # Sisakan ruang untuk prefix
    
    if len(teks) <= MAX_LEN:
        await channel.send(prefix + teks)
        return
    
    # Pecah per 1900 char, usahakan potong di newline
    bagian = []
    sisa = teks
    
    while len(sisa) > MAX_LEN:
        # Cari newline terdekat sebelum MAX_LEN
        potong = sisa.rfind("\n", 0, MAX_LEN)
        if potong == -1:
            potong = sisa.rfind(" ", 0, MAX_LEN)
        if potong == -1:
            potong = MAX_LEN
        
        bagian.append(sisa[:potong])
        sisa = sisa[potong:].lstrip()
    
    if sisa:
        bagian.append(sisa)
    
    # Kirim
    total = len(bagian)
    for i, b in enumerate(bagian, 1):
        header = f"{prefix}({i}/{total})\n" if total > 1 else prefix
        await channel.send(header + b)



# TOOL_HUB_IMPORT
try:
    import tool_hub
    TOOL_HUB_AVAILABLE = True
except ImportError:
    TOOL_HUB_AVAILABLE = False


# TOOL_EKSEKUSI_IMPORT
try:
    import tool_eksekusi as te
    TOOL_AVAILABLE = True
except ImportError:
    TOOL_AVAILABLE = False


TOKEN = os.getenv("DISCORD_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)


def log(msg):
    print(f"[Orion] {msg}", flush=True)


def deteksi_intent(pesan: str):
    p = pesan.lower().strip()
    for pola in ["coding ", "buatkan kode", "buat program", "buat script"]:
        if pola in p:
            idx = p.find(pola)
            return ("coding", pesan[idx + len(pola):].strip().split(",")[0].strip())
    for pola in ["scan folder", "scan "]:
        if pola in p:
            idx = p.find(pola)
            return ("scan", pesan[idx + len(pola):].strip().split(" simpan ")[0].strip() or None)
    for pola in ["jalankan ", "eksekusi "]:
        if pola in p:
            idx = p.find(pola)
            return ("terminal", pesan[idx + len(pola):].strip())
    # 8_SKILL_DISCORD
    # FASE3_DISCORD
    if p in ["shutdown", "matikan pc", "matikan komputer"]: return ("shutdown", None)
    if p in ["restart", "restart pc", "ulang pc"]: return ("restart", None)
    if p in ["lihat chat", "history chat", "riwayat chat"]: return ("lihat_chat", None)
    if p in ["hapus chat", "clear chat", "reset chat"]: return ("hapus_chat", None)
    if p.startswith("menu "): return ("menu", p.replace("menu ", "").strip())
    if p == "menu": return ("menu", "default")
    if p.startswith("ingetin "): return ("ingetin", p.replace("ingetin ", "").strip())
    if p.startswith("ingatkan "): return ("ingetin", p.replace("ingatkan ", "").strip())
    
    # FASE2_DISCORD
    if p in ["browser", "buka browser"]: return ("browser", None)
    if p.startswith("cari berita "): return ("cari_berita", p.replace("cari berita ", "").strip())
    if p.startswith("saham "): return ("saham", p.replace("saham ", "").strip())
    if p == "saham": return ("saham", "BBCA")
    if p.startswith("kurs "): return ("kurs", p.replace("kurs ", "").strip())
    if p == "kurs": return ("kurs", "USD")
    if p in ["jadwal", "jadwal hari ini", "kalender hari ini"]: return ("jadwal_hari_ini", None)
    if p.startswith("buat event "): return ("buat_event", p.replace("buat event ", "").strip())
    if p in ["buka kalender", "buka gcal"]: return ("buka_kalender", None)
    
    if p in ["screenshot", "ss", "ss layar"]: return ("screenshot", None)
    if p.startswith("volume "): return ("volume", p.replace("volume ", "").strip())
    if p == "volume": return ("volume", "50")
    if p.startswith("brightness "): return ("brightness", p.replace("brightness ", "").strip())
    # DISCORD_TERMINAL
    if p.startswith("buka vs 2022") or p.startswith("buka vs2022") or p.startswith("buka visual studio"):
        return ("buka_vs2022", p.split(" ", 3)[-1] if len(p.split()) > 3 else None)
    if p.startswith("buka vscode") or p.startswith("buka vs code"):
        return ("buka_vscode", p.split(" ", 2)[-1] if len(p.split()) > 2 else None)
    if p.startswith("buka cmd") or p.startswith("buka command"):
        return ("buka_cmd", p.split(" ", 2)[-1] if len(p.split()) > 2 else None)
    if p.startswith("buka powershell") or p.startswith("buka ps"):
        return ("buka_powershell", p.split(" ", 2)[-1] if len(p.split()) > 2 else None)
    if p.startswith("buka windows terminal") or p.startswith("buka wt"):
        return ("buka_wt", p.split(" ", 3)[-1] if len(p.split()) > 3 else None)
    if p.startswith("buka notepad"):
        return ("buka_notepad", p.split(" ", 2)[-1] if len(p.split()) > 2 else None)
    if p.startswith("analisis file "):
        return ("analisis_file", p.replace("analisis file ", "").strip())
    if p.startswith("fix file "):
        return ("fix_file", p.replace("fix file ", "").strip())
    
    # FITUR_LOG_DISCORD
    # DETEKSI_FLEKSIBEL
    # Baca file - cari "baca file X" di mana saja
    import re as _re_bf
    m_bf = _re_bf.search(r'(?:baca|lihat|tampilkan|bacain|bacakan)\s+file\s+([\w\-\.\\/:]+)', pesan, _re_bf.IGNORECASE)
    if m_bf:
        return ("baca_file", m_bf.group(1).strip())
    
    if p.startswith("baca log ") or p.startswith("cek log "):
        return ("baca_log", p.replace("baca log ", "").replace("cek log ", "").strip())
    if p.startswith("analisis error "):
        return ("analisis_error", p.replace("analisis error ", "").strip())
    if p.startswith("analisis multi "):
        return ("analisis_multi", p.replace("analisis multi ", "").strip())
    if p.startswith("fix sampai jalan "):
        return ("fix_sampai_jalan", p.replace("fix sampai jalan ", "").strip())
    
    # UNIVERSAL_DISCORD
    import re as _re_u
    m = _re_u.search(r'cari\s+(?:string|kata)\s+["\']?(.+?)["\']?\s+(?:di|dalam)\s+(.+)', pesan, _re_u.IGNORECASE)
    if m:
        return ("cari_string", m.group(1).strip() + "|" + m.group(2).strip())
    if p.startswith("analisis dependency ") or p.startswith("cek dependency "):
        return ("analisis_dependency", p.replace("analisis dependency ", "").replace("cek dependency ", "").strip())
    if p.startswith("git init ") or p.startswith("init git "):
        return ("git_init", p.replace("git init ", "").replace("init git ", "").strip())
    if p.startswith("git status ") or p.startswith("git cek "):
        return ("git_status", p.replace("git status ", "").replace("git cek ", "").strip())
    if p.startswith("git commit "):
        return ("git_commit", p.replace("git commit ", "").strip())
    if p.startswith("jalankan test ") or p.startswith("test folder "):
        return ("jalankan_test", p.replace("jalankan test ", "").replace("test folder ", "").strip())
    if p.startswith("fix folder ") or p.startswith("fix proyek "):
        return ("fix_folder", p.replace("fix folder ", "").replace("fix proyek ", "").strip())
    
    # 13_HANDLER_DISCORD
    if p.startswith("hapus file "):
        return ("hapus_file", p.replace("hapus file ", "").strip())
    if p.startswith("restore file "):
        return ("restore_file", p.replace("restore file ", "").strip())
    if p.startswith("copy file "):
        return ("copy_file", p.replace("copy file ", "").strip())
    if p.startswith("buat folder ") or p.startswith("bikin folder "):
        return ("buat_folder", p.replace("buat folder ", "").replace("bikin folder ", "").strip())
    if p.startswith("list file ") or p.startswith("lihat file "):
        return ("list_file", p.replace("list file ", "").replace("lihat file ", "").strip())
    if p.startswith("workflow "):
        return ("workflow", p.replace("workflow ", "").strip())
    if p == "daftar workflow" or p == "list workflow":
        return ("list_workflow", None)
    if p.startswith("buka cmd ") or p == "buka cmd":
        return ("buka_cmd", p.replace("buka cmd ", "").strip() if len(p.split()) > 2 else None)
    if p.startswith("buka windows terminal ") or p == "buka windows terminal":
        return ("buka_wt", p.replace("buka windows terminal ", "").strip() if len(p.split()) > 3 else None)
    if p.startswith("buka file "):
        return ("buka_file", p.replace("buka file ", "").strip())
    if p.startswith("analisis folder ") or p.startswith("analisa folder "):
        return ("analisis_folder", p.replace("analisis folder ", "").replace("analisa folder ", "").strip())
    if p.startswith("trace error "):
        return ("trace_error", p.replace("trace error ", "").strip())
    if p.startswith("tulis file "):
        return ("tulis_file", p.replace("tulis file ", "").strip())
    
    # SELF_SKILL_DISCORD
    if p.startswith("fix baris "):
        return ("fix_baris", pesan.replace("fix baris ", "").strip())
    if p.startswith("fix fungsi "):
        return ("fix_fungsi", pesan.replace("fix fungsi ", "").strip())
    if p.startswith("tambah skill "):
        return ("tambah_skill", pesan.replace("tambah skill ", "").strip())
    
    if p.startswith("buka "): return ("buka_app", p.replace("buka ", "").strip())
    if p.startswith("kill "): return ("kill", p.replace("kill ", "").strip())
    if p in ["status", "status sistem"]: return ("status", None)
    if p.startswith("cuaca "): return ("cuaca", p.replace("cuaca ", "").strip())
    if p == "cuaca": return ("cuaca", "Jakarta")
    if p in ["berita", "berita detik"]: return ("berita", "detik")
    if p.startswith("berita "): return ("berita", p.replace("berita ", "").strip())
    if p.startswith("yt ") or p.startswith("youtube "): 
        url = p.replace("yt ", "").replace("youtube ", "").strip()
        return ("yt", url)
    
    if p in ["ping", "test", "tes"]: return ("ping", None)
    if p in ["halo", "hai", "hi"]: return ("halo", None)
    if p in ["join", "masuk voice"]: return ("join", None)
    if p in ["leave", "keluar voice"]: return ("leave", None)
    if p in ["help", "bantuan"]: return ("help", None)
    return ("chat", pesan)


async def balas_suara_orion(message, teks):
    """Balas pakai suara Orion."""
    log(f"balas_suara_orion: {teks[:50]}")
    
    if not message.guild:
        log("Tidak ada guild")
        return
    if not message.guild.voice_client:
        log("Bot tidak di voice")
        return
    
    vc = message.guild.voice_client
    log(f"Voice client connected: {vc.is_connected()}")
    
    try:
        log("Import voice_orion...")
        from voice_orion import tts_supertonic_bytes
        log("Import OK")
        
        loop = asyncio.get_event_loop()
        log(f"Generate TTS: {teks[:50]}")
        audio_bytes = await loop.run_in_executor(None, lambda: tts_supertonic_bytes(teks))
        log(f"TTS result: type={type(audio_bytes)}, len={len(audio_bytes) if audio_bytes else 0}")
        
        if not audio_bytes:
            log("TTS return None/kosong")
            return
        if not isinstance(audio_bytes, bytes):
            log(f"Bukan bytes: {type(audio_bytes)}")
            return
        
        log(f"Play {len(audio_bytes)} bytes")
        if vc.is_playing():
            vc.stop()
            await asyncio.sleep(0.3)
        
        source = discord.FFmpegPCMAudio(io.BytesIO(audio_bytes), pipe=True)
        vc.play(source)
        log("Play OK")
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()


@client.event
async def on_ready():
    log(f"Bot online: {client.user}")
    log(f"Server: {[g.name for g in client.guilds]}")
    await client.change_presence(activity=discord.Game(name="Orion"))

    # Pre-warm TTS di background biar user pertama tidak nunggu 3.5s
    import threading
    def _warm():
        try:
            log("[Warm] Loading TTS model...")
            from voice_orion import _get_tts, _get_style
            tts = _get_tts()
            _get_style("F1")
            log("[Warm] TTS siap! User pertama langsung responsif.")
        except Exception as e:
            log(f"[Warm] Error: {e}")
    threading.Thread(target=_warm, daemon=True).start()


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    pesan = message.content.strip()
    if not pesan:
        return
    
    tipe, arg = deteksi_intent(pesan)
    log(f"Pesan: '{pesan}' → {tipe}")
    
    if tipe == "join":
        if message.author.voice:
            channel = message.author.voice.channel
            await channel.connect()
            await message.channel.send(f"🎤 Join: **{channel.name}**")
            log("Bot join voice")
        else:
            await message.channel.send("❌ Kamu harus di voice channel dulu")
        return
    
    if tipe == "leave":
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send("👋 Keluar voice")
        return
    
    if tipe == "ping":
        await message.channel.send("🏓 Pong!")
        return
    
    if tipe == "halo":
        await message.channel.send(f"👋 Halo {message.author.name}!")
        await balas_suara_orion(message, f"Halo {message.author.name}, gue Orion")
        return
    
    if tipe == "help":
        await message.channel.send("📖 **Orion Bot**\n\nVoice: `join`, `leave`\nCoding: `coding Flask`\nScan: `scan folder X`\nTerminal: `jalankan dir`\nChat: `halo`")
        return
    
    if tipe == "coding":
        await message.channel.send(f"🤔 Coding: `{arg}`...")
        await balas_suara_orion(message, "Oke gue coding")
        try:
            from coding_assistant import coding_loop
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: coding_loop(arg, max_iterasi=3, nama_file=_extract_nama_file(arg)))
            if hasil.get("sukses"):
                await message.channel.send(f"✅ Selesai: `{hasil.get('file')}`")
                await balas_suara_orion(message, "Selesai Rik")
            else:
                await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "scan":
        folder = arg or r"E:\Project Software\Orion"
        await message.channel.send(f"🔍 Scan: `{folder}`...")
        try:
            from tool_eksekusi import scan_folder
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: scan_folder(folder=folder))
            if hasil.get("sukses"):
                await message.channel.send(f"✅ {hasil.get('total_file')} file")
                await balas_suara_orion(message, f"Selesai, {hasil.get('total_file')} file")
            else:
                await message.channel.send(f"❌ Gagal")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "terminal":
        await message.channel.send(f"⚙️ `{arg}`...")
        try:
            from tool_eksekusi import jalankan_terminal
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: jalankan_terminal(arg))
            if hasil.get("sukses"):
                await kirim_panjang(message.channel, f"✅ Exit {hasil.get('exit_code')}:\n```\n{hasil.get('output', '')}\n```")
            else:
                await message.channel.send(f"❌ Gagal")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === FASE3_DISCORD HANDLERS ===
    if tipe == "shutdown":
        await message.channel.send("⚠️ **Konfirmasi**: Shutdown PC? Ketik `yakin shutdown` dalam 10 detik")
        # Simple: tunggu 10 detik, kalau ada pesan "yakin shutdown" → eksekusi
        try:
            def check(m):
                return m.author == message.author and m.content.lower() == "yakin shutdown"
            await client.wait_for("message", check=check, timeout=10.0)
            from core import power
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: power("shutdown"))
            await message.channel.send("💤 Shutdown...")
        except asyncio.TimeoutError:
            await message.channel.send("❌ Dibatalkan")
        return
    
    if tipe == "restart":
        await message.channel.send("⚠️ **Konfirmasi**: Restart PC? Ketik `yakin restart` dalam 10 detik")
        try:
            def check(m):
                return m.author == message.author and m.content.lower() == "yakin restart"
            await client.wait_for("message", check=check, timeout=10.0)
            from core import power
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: power("restart"))
            await message.channel.send("🔄 Restart...")
        except asyncio.TimeoutError:
            await message.channel.send("❌ Dibatalkan")
        return
    
    if tipe == "lihat_chat":
        try:
            from core import chat_lihat
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: chat_lihat())
            await message.channel.send(f"📜 Chat history:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "hapus_chat":
        try:
            from core import chat_hapus
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: chat_hapus())
            await message.channel.send("🗑️ Chat dihapus")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "menu":
        try:
            from core import scraper_menu
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: scraper_menu(arg))
            await message.channel.send(f"🍽️ Menu {arg}:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "ingetin":
        try:
            from core import auto_notif_mulai
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: auto_notif_mulai(arg))
            await message.channel.send(f"🔔 Reminder: {arg}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === FASE2_DISCORD HANDLERS ===
    if tipe == "browser":
        try:
            from core import browser
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: browser())
            await message.channel.send("🌐 Browser dibuka")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "cari_berita":
        try:
            from core import cari_berita
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: cari_berita(arg))
            await message.channel.send(f"📰 Cari: {arg}\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "saham":
        try:
            from core import harga_saham
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: harga_saham(arg))
            await message.channel.send(f"📈 Saham {arg}:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "kurs":
        try:
            from core import kurs_mata_uang
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: kurs_mata_uang(arg))
            await message.channel.send(f"💱 Kurs {arg}:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "jadwal_hari_ini":
        try:
            from core import gcal_hari_ini
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: gcal_hari_ini())
            await message.channel.send(f"📅 Jadwal hari ini:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buat_event":
        try:
            from core import gcal_buat_event
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: gcal_buat_event(arg))
            await message.channel.send(f"📅 Event dibuat:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_kalender":
        try:
            from core import gcal_buka
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: gcal_buka())
            await message.channel.send("📅 Kalender dibuka")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === 8_SKILL_DISCORD HANDLERS ===
    if tipe == "screenshot":
        try:
            from core import screenshot
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: screenshot())
            if hasil and os.path.exists(hasil):
                await message.channel.send("📸 Screenshot:", file=discord.File(hasil))
            else:
                await message.channel.send(f"❌ Gagal screenshot: {hasil}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "volume":
        try:
            from core import volume
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: volume(arg))
            await message.channel.send(f"🔊 Volume: {arg}%")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "brightness":
        try:
            from core import brightness
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: brightness(arg))
            await message.channel.send(f"💡 Brightness: {arg}%")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # DISCORD_TERMINAL HANDLERS
    if tipe == "buka_vs2022":
        try:
            from tool_eksekusi import buka_vs2022
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_vs2022(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_vscode":
        try:
            from tool_eksekusi import buka_vscode
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_vscode(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_cmd":
        try:
            from tool_eksekusi import buka_cmd
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_cmd(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_powershell":
        try:
            from tool_eksekusi import buka_powershell
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_powershell(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_wt":
        try:
            from tool_eksekusi import buka_windows_terminal
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_windows_terminal(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_notepad":
        try:
            from tool_eksekusi import buka_notepad
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: buka_notepad(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', 'OK')}" if hasil.get('sukses') else f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "analisis_file":
        await message.channel.send(f"🔍 Analisis: `{arg}`...")
        try:
            from tool_eksekusi import analisis_file
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: analisis_file(arg))
            if hasil.get("sukses"):
                await message.channel.send(f"📄 {hasil.get('analisis', '?')}")
            else:
                await message.channel.send(f"❌ {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "fix_file":
        await message.channel.send(f"🔧 Fix: `{arg}`...")
        try:
            from tool_eksekusi import fix_file
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: fix_file(arg))
            if hasil.get("sukses"):
                await message.channel.send("OK Fixed: " + str(hasil.get("file", "?")) + " | backup: " + str(hasil.get("backup", "?")))
            else:
                await message.channel.send(f"❌ {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # FITUR_LOG_DISCORD HANDLERS
    # DISCORD_BACA_FILE HANDLER
    if tipe == "baca_file":
        await message.channel.send(f"📖 Baca file: `{arg}`...")
        try:
            from tool_eksekusi import baca_file
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: baca_file(arg))
            if hasil.get("sukses"):
                isi = hasil.get("isi", "")
                path = hasil.get("path", hasil.get("file", arg))
                # Discord limit 2000 char - potong
                await kirim_panjang(message.channel, f"📄 **{path}** ({len(isi)} char):\n```\n{isi}\n```")
            else:
                await message.channel.send(f"❌ {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "baca_log":
        await message.channel.send(f"📖 Baca log: `{arg}`...")
        try:
            from tool_eksekusi import baca_log
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: baca_log(arg))
            if hasil.get("sukses"):
                await kirim_panjang(message.channel, f"📄 Log ({hasil.get('total')} baris):\n```\n{hasil.get('isi', '')}\n```")
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "analisis_error":
        await message.channel.send(f"🔍 Analisis error...")
        try:
            from tool_eksekusi import analisis_error
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: analisis_error(arg))
            if hasil.get("sukses"):
                fe = hasil.get("file_utama", {})
                await message.channel.send(f"📄 File: `{fe.get('file', '?')}` line {fe.get('line', '?')}\n❌ Error: {hasil.get('error', '?')}")
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "analisis_multi":
        files = [f.strip() for f in arg.split(",") if f.strip()]
        await message.channel.send(f"🔍 Analisis {len(files)} file...")
        try:
            from tool_eksekusi import analisis_multi
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: analisis_multi(files))
            teks = f"📄 Hasil ({hasil.get('total')} file):\n"
            for item in hasil.get("hasil", []):
                teks += f"\n📁 {item.get('file', '?')}:\n{item.get('analisis', '?')}\n"
            for i in range(0, len(teks), 1900):
                await message.channel.send(teks[i:i+1900])
                if i + 1900 < len(teks):
                    await asyncio.sleep(0.5)
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "fix_sampai_jalan":
        await message.channel.send(f"🔧 Fix sampai jalan: `{arg}`...")
        try:
            from tool_eksekusi import fix_sampai_jalan
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: fix_sampai_jalan(arg))
            if hasil.get("sukses"):
                await message.channel.send(f"✅ Sukses - loop {hasil.get('loop', '?')}")
            else:
                await message.channel.send(f"❌ {hasil.get('error', '?')} (loop {hasil.get('loop', '?')})")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # UNIVERSAL_DISCORD HANDLERS
    if tipe == "cari_string":
        parts = arg.split("|", 1)
        if len(parts) != 2:
            await message.channel.send("❌ Format: cari string <pattern> di <folder>")
            return
        pattern, folder = parts
        await message.channel.send(f"🔍 Cari '{pattern}' di `{folder}`...")
        try:
            from tool_eksekusi import cari_string
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: cari_string(folder, pattern))
            if hasil.get("sukses"):
                teks = f"📄 {hasil.get('total_match')} match di {hasil.get('scanned')} file:\n"
                for item in hasil.get("hasil", []):
                    teks += f"\n📁 `{item.get('file')}:{item.get('line')}`\n   {item.get('isi', '')}\n"
                for i in range(0, len(teks), 1900):
                    await message.channel.send(teks[i:i+1900])
                    if i + 1900 < len(teks):
                        await asyncio.sleep(0.5)
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "analisis_dependency":
        await message.channel.send(f"🔍 Analisis dependency: `{arg}`...")
        try:
            from tool_eksekusi import analisis_dependency
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: analisis_dependency(arg))
            if hasil.get("sukses"):
                teks = f"📄 {hasil.get('total_file')} file, {len(hasil.get('masalah', []))} masalah:\n"
                for m in hasil.get("masalah", []):
                    teks += f"\n⚠️ `{m.get('file')}` → `{m.get('import')}` ({m.get('masalah')})"
                for i in range(0, len(teks), 1900):
                    await message.channel.send(teks[i:i+1900])
                    if i + 1900 < len(teks):
                        await asyncio.sleep(0.5)
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "git_init":
        try:
            from tool_eksekusi import git_init
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: git_init(arg))
            await message.channel.send(f"✅ {hasil.get('pesan', hasil.get('error'))}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "git_status":
        try:
            from tool_eksekusi import git_status
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: git_status(arg))
            await kirim_panjang(message.channel, f"📊 Git status:\n```\n{hasil.get('output', '')}\n```")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "git_commit":
        # Parse: <folder> atau <msg> di <folder>
        import re as _re_c
        m = _re_c.search(r'["\']?(.+?)["\']?\s+(?:di|dalam)\s+(.+)', arg)
        if m:
            msg, folder = m.group(1).strip(), m.group(2).strip()
        else:
            msg, folder = "Auto-commit by Orion", arg
        try:
            from tool_eksekusi import git_commit
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: git_commit(folder, msg))
            await message.channel.send(f"✅ {hasil.get('pesan', hasil.get('error'))}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "jalankan_test":
        await message.channel.send(f"🧪 Test: `{arg}`...")
        try:
            from tool_eksekusi import jalankan_test
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: jalankan_test(arg))
            status = "✅" if hasil.get("sukses") else "❌"
            await kirim_panjang(message.channel, f"{status} Exit {hasil.get('exit_code')}:\n```\n{hasil.get('output', '')}\n```")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "fix_folder":
        await message.channel.send(f"🔧 Fix folder: `{arg}`... (bisa lama, tunggu)")
        try:
            from tool_eksekusi import fix_folder
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: fix_folder(arg, max_file=5))
            if hasil.get("sukses"):
                teks = f"✅ {hasil.get('sukses_fix')}/{hasil.get('total_fix')} file berhasil difix:\n"
                for item in hasil.get("hasil", []):
                    status = "✅" if item.get("fix_sukses") else "❌"
                    teks += f"\n{status} `{item.get('file')}`"
                    if item.get("error"):
                        teks += f" - {item.get('error')}"
                for i in range(0, len(teks), 1900):
                    await message.channel.send(teks[i:i+1900])
                    if i + 1900 < len(teks):
                        await asyncio.sleep(0.5)
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # 13_HANDLER_DISCORD HANDLERS
    if tipe == "hapus_file":
        try:
            from tool_eksekusi import hapus_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: hapus_file(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "restore_file":
        try:
            from tool_eksekusi import restore_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: restore_file(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "copy_file":
        import re as _re_c
        parts = _re_c.split(r'\s+ke\s+', arg)
        if len(parts) != 2:
            await message.channel.send("❌ Format: copy file <sumber> ke <tujuan>")
            return
        try:
            from tool_eksekusi import copy_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: copy_file(parts[0].strip(), parts[1].strip()))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "buat_folder":
        try:
            from tool_eksekusi import buat_folder
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: buat_folder(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "list_file":
        try:
            from tool_eksekusi import list_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: list_file(arg))
            if r.get("sukses"):
                items = r.get("items", [])
                teks = f"📁 {arg} ({len(items)} item):\n"
                for item in items:
                    teks += f"  {item.get('tipe', '?')}: {item.get('nama', '?')}\n"
                await message.channel.send(f"```\n{teks}\n```")
            else:
                await message.channel.send(f"❌ {r.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "workflow":
        await message.channel.send(f"▶️ Workflow: `{arg}`...")
        try:
            import workflow_engine
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: workflow_engine.jalankan_workflow(arg, verbose=False))
            if r.get("sukses"):
                await message.channel.send(f"✅ Workflow selesai ({r.get('total_langkah')} langkah)")
            else:
                await message.channel.send(f"❌ {r.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "list_workflow":
        try:
            import workflow_engine
            wfs = workflow_engine.daftar_workflow()
            teks = "📋 Workflow:\n"
            for wf in wfs:
                teks += f"  • `{wf.get('nama')}` ({wf.get('langkah', '?')} langkah)\n"
            await message.channel.send(teks)
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "buka_cmd":
        try:
            from tool_eksekusi import buka_cmd
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: buka_cmd(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "buka_wt":
        try:
            from tool_eksekusi import buka_windows_terminal
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: buka_windows_terminal(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "buka_file":
        try:
            from tool_eksekusi import buka_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: buka_file(arg))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "analisis_folder":
        await message.channel.send(f"🔍 Analisis folder: `{arg}`...")
        try:
            from tool_eksekusi import analisis_folder
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: analisis_folder(arg, max_file=5))
            if r.get("sukses"):
                teks = f"📄 {r.get('total_py')} file .py, {r.get('bug_ditemukan')} bug:\n"
                for item in r.get("hasil", []):
                    teks += f"\n📁 `{item.get('file')}`:\n{item.get('analisis', '')}"
                for i in range(0, len(teks), 1900):
                    await message.channel.send(teks[i:i+1900])
                    if i + 1900 < len(teks):
                        await asyncio.sleep(0.5)
            else:
                await message.channel.send(f"❌ {r.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "trace_error":
        await message.channel.send(f"🔍 Trace: `{arg}`...")
        try:
            from tool_eksekusi import trace_error
            loop = asyncio.get_event_loop()
            # Parse: folder cmd: cmd
            import re as _re_t
            m = _re_t.search(r'(.+?)\s+cmd:\s*(.+)', arg)
            if not m:
                await message.channel.send("❌ Format: trace error <folder> cmd: <cmd>")
                return
            folder, cmd = m.group(1).strip(), m.group(2).strip()
            r = await loop.run_in_executor(None, lambda: trace_error(folder, cmd))
            if r.get("sukses"):
                await message.channel.send(f"✅ Trace sukses - loop {r.get('loop')}")
            else:
                await message.channel.send(f"❌ {r.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    if tipe == "tulis_file":
        import re as _re_w
        parts = _re_w.split(r'\s+isi:\s+', arg, maxsplit=1)
        if len(parts) != 2:
            await message.channel.send("❌ Format: tulis file <path> isi: <teks>")
            return
        try:
            from tool_eksekusi import tulis_file
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: tulis_file(parts[0].strip(), parts[1].strip()))
            await message.channel.send(f"✅ {r.get('pesan', r.get('error', 'OK'))}")
        except Exception as e:
            await message.channel.send(f"❌ {e}")
        return
    
    # SELF_SKILL_DISCORD HANDLERS
    if tipe == "fix_baris":
        import re as _re
        m = _re.search(r'(.+?)\s+(\d+)\s+["\'](.+?)["\']\s+["\'](.+?)["\']', arg)
        if not m:
            await message.channel.send("❌ Format: fix baris <file> <baris> \"lama\" \"baru\"")
            return
        fp, br, lama, baru = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        try:
            from tool_eksekusi import fix_baris
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: fix_baris(fp, br, lama, baru))
            if hasil.get("sukses"):
                await message.channel.send(f"✅ Fix baris {hasil.get('baris')}:\nLama: `{hasil.get('lama')}`\nBaru: `{hasil.get('baru')}`\nBackup: `{hasil.get('backup')}`")
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "fix_fungsi":
        import re as _re
        # Coba format: <file> <nama> "instruksi"
        m = _re.search(r'(.+?)\s+(\w+)\s+["\'](.+?)["\']', arg)
        if m:
            fp, nama, ins = m.group(1), m.group(2), m.group(3)
        else:
            m2 = _re.search(r'(.+?)\s+(\w+)', arg)
            if not m2:
                await message.channel.send("❌ Format: fix fungsi <file> <nama> \"instruksi\"")
                return
            fp, nama, ins = m2.group(1), m2.group(2), "perbaiki bug"
        try:
            from tool_eksekusi import fix_fungsi
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: fix_fungsi(fp, nama, ins))
            if hasil.get("sukses"):
                await message.channel.send(f"✅ Fix fungsi `{hasil.get('fungsi')}`\nBackup: `{hasil.get('backup')}`")
            else:
                await message.channel.send(f"❌ {hasil.get('error')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "tambah_skill":
        import re as _re
        m = _re.search(r'["\'](.+?)["\']', arg)
        if not m:
            await message.channel.send("❌ Format: tambah skill \"deskripsi\"")
            return
        deskripsi = m.group(1)
        try:
            from pathlib import Path
            from datetime import datetime
            skills_dir = Path(r"E:\Project Software\Orion\skills")
            skills_dir.mkdir(exist_ok=True)
            slug = deskripsi.lower().replace(" ", "_")[:30]
            skill_file = skills_dir / f"{slug}.md"
            skill_file.write_text(f"# SKILL: {slug}\n\n{deskripsi}\n\nDibuat: {datetime.now()}\n", encoding="utf-8")
            await message.channel.send(f"✅ Skill ditambah: `{skill_file.name}`")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "buka_app":
        try:
            from core import buka_app
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: buka_app(arg))
            await message.channel.send(f"🚀 Buka: {arg}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "kill":
        try:
            from core import kill_proses
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: kill_proses(arg))
            await message.channel.send(f"💀 Kill: {arg}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "status":
        try:
            from core import status_sistem
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: status_sistem())
            await message.channel.send(f"📊 Status:\n```\n{str(hasil)}\n```")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "cuaca":
        try:
            from core import cuaca_plus
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: cuaca_plus(arg))
            await message.channel.send(f"🌤️ Cuaca {arg}:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "berita":
        try:
            from core import berita_detik, berita_kompas, berita_cnn, berita_tempo
            sumber = arg.lower() if arg else "detik"
            fn = {"detik": berita_detik, "kompas": berita_kompas, "cnn": berita_cnn, "tempo": berita_tempo}.get(sumber, berita_detik)
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, fn)
            await message.channel.send(f"📰 Berita {sumber}:\n{str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    if tipe == "yt":
        try:
            from core import yt_download
            loop = asyncio.get_event_loop()
            await message.channel.send(f"⏬ Download: `{arg}`...")
            hasil = await loop.run_in_executor(None, lambda: yt_download(arg))
            await message.channel.send(f"✅ {str(hasil)}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === OCR GAMBAR ===
    if message.attachments:
        for att in message.attachments:
            if att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                try:
                    await message.channel.send("📸 OCR gambar...")
                    # Download gambar
                    img_path = f"temp_ocr_{att.filename}"
                    await att.save(img_path)
                    from core import ocr_file
                    loop = asyncio.get_event_loop()
                    hasil = await loop.run_in_executor(None, lambda: ocr_file(img_path))
                    await message.channel.send(f"📝 Hasil OCR:\n{str(hasil)}")
                    import os
                    os.remove(img_path)
                except Exception as e:
                    await message.channel.send(f"❌ OCR Error: {e}")
                return
    
    if tipe == "chat":
        # EKSEKUSI_DULU_DISCORD
        # Cek dulu apakah pesan butuh eksekusi
        try:
            from otak_orion import deteksi_eksekusi, eksekusi_dari_pesan
            loop = asyncio.get_event_loop()
            det = await loop.run_in_executor(None, lambda: deteksi_eksekusi(pesan))
            
            if det.get("butuh_eksekusi"):
                tipe_eksekusi = det.get("tipe", "?")
                await message.channel.send(f"⚙️ Eksekusi: `{tipe_eksekusi}`...")
                
                hasil = await loop.run_in_executor(None, lambda: eksekusi_dari_pesan(pesan))
                
                if hasil.get("sukses"):
                    h = hasil.get("hasil", {})
                    if isinstance(h, dict):
                        f = h.get("file", "?")
                        tf = h.get("total_file", "?")
                        ts = h.get("total_size", 0)
                        await message.channel.send(f"✅ Selesai\n📁 `{f}`\n📊 {tf} file, {ts:,} B")
                    else:
                        await message.channel.send(f"✅ {str(h)}")
                    await balas_suara_orion(message, "Selesai Rik")
                else:
                    await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
                return
        except Exception as e:
            print(f"[Discord] Deteksi error: {e}")
        
        # Kalau bukan eksekusi - LLM chat
        await message.channel.send("🤔...")
        try:
            from otak_orion import diskusi_orion
            loop = asyncio.get_event_loop()
            jawab = await loop.run_in_executor(None, lambda: diskusi_orion(pesan))
            teks = f"🤖 {jawab}"
            for i in range(0, len(teks), 1900):
                await message.channel.send(teks[i:i+1900])
                if i + 1900 < len(teks):
                    await asyncio.sleep(0.5)
            await balas_suara_orion(message, jawab)
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    if not TOKEN:
        log("ERROR: DISCORD_TOKEN belum di-set!")
    else:
        log("Start bot...")
        client.run(TOKEN)
