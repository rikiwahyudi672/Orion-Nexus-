import sys
from pathlib import Path
_BASE = Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

from dotenv import load_dotenv

# Load .env
load_dotenv()

"""
discord_orion.py - Bot Discord Orion (tanpa prefix).
"""
import discord
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# ============ DETEKSI INTENT ============
def deteksi_intent(pesan: str):
    """
    Deteksi intent dari pesan biasa (tanpa prefix).
    Return: (tipe, argumen)
    """
    p = pesan.lower().strip()
    
    # === CODING ===
    for pola in ["coding ", "buatkan kode", "buat program", "bikin aplikasi", "generate code", "buatkan aplikasi", "buat script"]:
        if p.startswith(pola) or pola in p:
            # Ambil goal
            idx = p.find(pola)
            goal = pesan[idx + len(pola):].strip()
            # Buang kata sambung di akhir
            goal = goal.split(",")[0].split(";")[0].strip()
            return ("coding", goal)
    
    # === SCAN FOLDER ===
    for pola in ["scan folder", "scanning folder", "scan directory", "pindai folder", "scan "]:
        if pola in p:
            idx = p.find(pola)
            folder = pesan[idx + len(pola):].strip()
            # Buang "simpan ke X"
            folder = folder.split(" simpan ")[0].split(" taruh ")[0].strip()
            return ("scan", folder or None)
    
    # === TERMINAL ===
    for pola in ["jalankan ", "eksekusi ", "run ", "terminal "]:
        if pola in p:
            idx = p.find(pola)
            cmd = pesan[idx + len(pola):].strip()
            return ("terminal", cmd)
    
    # === WORKFLOW ===
    for pola in ["jalankan workflow ", "run workflow "]:
        if pola in p:
            idx = p.find(pola)
            nama = pesan[idx + len(pola):].strip()
            return ("workflow", nama)
    
    if "daftar workflow" in p or "list workflow" in p:
        return ("list_workflow", None)
    
    # === HALO ===
    if p in ["halo", "hai", "hi", "hello", "orion"]:
        return ("halo", None)
    
    if p.startswith("halo ") or p.startswith("hai "):
        return ("halo", None)
    
    # === PING ===
    if p in ["ping", "test", "tes"]:
        return ("ping", None)
    
    # === HELP ===
    if p in ["help", "bantuan", "bantu"]:
        return ("help", None)
    
    # === CHAT (default) ===
    return ("chat", pesan)


# ============ HANDLER ============
@client.event
async def on_ready():
    print(f"[Orion] Bot online: {client.user}")
    print(f"[Orion] Server: {[g.name for g in client.guilds]}")
    await client.change_presence(activity=discord.Game(name="ketik 'help' untuk bantuan"))


@client.event
async def on_message(message):
    # Jangan balas bot sendiri
    if message.author == client.user:
        return
    
    # Jangan balas bot lain
    if message.author.bot:
        return
    
    pesan = message.content.strip()
    if not pesan:
        return
    
    tipe, arg = deteksi_intent(pesan)
    
    # === PING ===
    if tipe == "ping":
        await message.channel.send("🏓 Pong! Orion hidup.")
        return
    
    # === HALO ===
    if tipe == "halo":
        await message.channel.send(f"👋 Halo {message.author.name}! Gue Orion, siap bantu.")
        return
    
    # === HELP ===
    if tipe == "help":
        teks = """📖 **Bantuan Orion**

Ketik pesan biasa (tanpa prefix):

**Coding:**
  `coding buat script print hello`
  `buatkan kode REST API Flask`

**Scan folder:**
  `scan folder E:\\Project`
  `scan folder gue`

**Terminal:**
  `jalankan dir`
  `jalankan python script.py`

**Workflow:**
  `daftar workflow`
  `jalankan workflow scan_saja`

**Chat:**
  `halo Orion`
  `apa kabar?`
"""
        await message.channel.send(teks)
        return
    
    # === CODING ===
    if tipe == "coding":
        await message.channel.send(f"🤔 Coding: `{arg}`...")
        try:
            from coding_assistant import coding_loop
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(
                None,
                lambda: coding_loop(arg, max_iterasi=3, nama_file="output_discord.py")
            )
            if hasil.get("sukses"):
                f = hasil.get("file", "?")
                it = hasil.get("iterasi", "?")
                await message.channel.send(f"✅ **Selesai!**\n📁 File: `{f}`\n🔄 Iterasi: {it}")
            else:
                await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === SCAN ===
    if tipe == "scan":
        folder = arg or r"E:\Project Software\Orion"
        await message.channel.send(f"🔍 Scan: `{folder}`...")
        try:
            from tool_eksekusi import scan_folder
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: scan_folder(folder=folder))
            if hasil.get("sukses"):
                f = hasil.get("file", "?")
                tf = hasil.get("total_file", "?")
                ts = hasil.get("total_size", 0)
                await message.channel.send(f"✅ **Selesai!**\n📁 File: `{f}`\n📊 {tf} file, {ts:,} B")
            else:
                await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === TERMINAL ===
    if tipe == "terminal":
        if not arg:
            await message.channel.send("❌ Contoh: `jalankan dir`")
            return
        await message.channel.send(f"⚙️ Jalankan: `{arg}`...")
        try:
            from tool_eksekusi import jalankan_terminal
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: jalankan_terminal(arg))
            if hasil.get("sukses"):
                out = hasil.get("output", "")[:1900]
                ec = hasil.get("exit_code", "?")
                await message.channel.send(f"✅ Exit {ec}:\n```\n{out}\n```")
            else:
                await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === WORKFLOW ===
    if tipe == "workflow":
        if not arg:
            await message.channel.send("❌ Contoh: `jalankan workflow scan_saja`")
            return
        await message.channel.send(f"▶️ Workflow: `{arg}`...")
        try:
            import workflow_engine
            loop = asyncio.get_event_loop()
            hasil = await loop.run_in_executor(None, lambda: workflow_engine.jalankan_workflow(arg, verbose=False))
            if hasil.get("sukses"):
                total = hasil.get("total_langkah", "?")
                await message.channel.send(f"✅ **Workflow selesai** - {total} langkah OK")
            else:
                await message.channel.send(f"❌ Gagal: {hasil.get('error', '?')}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === LIST WORKFLOW ===
    if tipe == "list_workflow":
        try:
            import workflow_engine
            wfs = workflow_engine.daftar_workflow()
            teks = "📋 **Workflow tersedia:**\n"
            for wf in wfs:
                teks += f"  • `{wf.get('nama')}` ({wf.get('langkah', '?')} langkah)\n"
            await message.channel.send(teks)
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return
    
    # === CHAT (default) ===
    if tipe == "chat":
        # Cek apakah pesan panjang - kalau iya, balas "mikir"
        if len(pesan) > 20:
            await message.channel.send("🤔 Orion mikir...")
        try:
            from otak_orion import diskusi_orion
            loop = asyncio.get_event_loop()
            jawab = await loop.run_in_executor(None, lambda: diskusi_orion(pesan))
            await message.channel.send(f"🤖 {jawab[:1900]}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN belum di-set!")
        print("Jalankan: $env:DISCORD_TOKEN = 'TOKEN_KAMU'")
    else:
        print("[Orion] Start bot...")
        client.run(TOKEN)
