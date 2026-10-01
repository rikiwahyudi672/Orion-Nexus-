"""
run_discord.py - Launcher Discord bot Orion dengan logo Discord.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# ============ WARNA ANSI ============
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"
    MAGENTA = "\033[95m"
    # Warna khusus Discord
    DISCORD = "\033[38;5;99m"    # Blurple-ish
    DISCORD_BRIGHT = "\033[38;5;105m"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def logo_discord():
    """Logo Discord + ORION."""
    print(f"""
{C.DISCORD}{C.BOLD}            ╭─────────────────────────────────────╮
            │                                     │
            │    ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗
            │   ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║
            │   ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║
            │   ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║
            │   ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║
            │    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
            │                                     │
            ╰─────────────────────────────────────╯{C.RESET}
""")


def logo_discord_kecil():
    """Logo Discord kecil."""
    print(f"""
{C.DISCORD}     ╔═══════════════════════════════════╗
     ║   {C.DISCORD_BRIGHT}{C.BOLD}◢◤ ORION DISCORD BOT ◢◤{C.DISCORD}    ║
     ╚═══════════════════════════════════╝{C.RESET}
""")


def logo_bulat():
    """Logo Discord bulat."""
    print(f"""
{C.DISCORD}{C.BOLD}              ╭───────────────╮
              │  {C.DISCORD_BRIGHT}◢◤{C.DISCORD}       {C.DISCORD_BRIGHT}◥◣{C.DISCORD}  │
              │               │
              │  {C.DISCORD_BRIGHT}O R I O N{C.DISCORD}    │
              │               │
              │  {C.DISCORD_BRIGHT}◥◣{C.DISCORD}       {C.DISCORD_BRIGHT}◢◤{C.DISCORD}  │
              ╰───────────────╯{C.RESET}
""")


def logo_ascii():
    """Logo Discord ASCII murni."""
    print(f"""
{C.DISCORD}{C.BOLD}
     ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗
     ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
     ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
     ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
     ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
     ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝
{C.RESET}""")


def info():
    """Info launcher."""
    print(f"{C.DISCORD}  ═════════════════════════════════════════════════{C.RESET}")
    print(f"{C.WHITE}   Personal AI Assistant   {C.GRAY}│{C.WHITE}   Discord Bot   {C.GRAY}│{C.CYAN}   v2.0{C.RESET}")
    print(f"{C.DISCORD}  ─────────────────────────────────────────────────{C.RESET}")
    print(f"{C.GRAY}   Owner   : {C.WHITE}Riki Wahyudi{C.RESET}")
    print(f"{C.GRAY}   Waktu   : {C.WHITE}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{C.RESET}")
    print(f"{C.GRAY}   Voice   : {C.GREEN}Supertonic (F1){C.RESET}")
    print(f"{C.GRAY}   LLM     : {C.GREEN}Groq (gpt-oss-120b){C.RESET}")
    print(f"{C.GRAY}   Prefix  : {C.GREEN}Tanpa prefix (pesan biasa){C.RESET}")
    print(f"{C.DISCORD}  ═════════════════════════════════════════════════{C.RESET}")
    print()


def load_token():
    """Load token dari .env."""
    env_file = Path(".env")
    if not env_file.exists():
        print(f"{C.RED}  ✗ File .env tidak ditemukan!{C.RESET}")
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("DISCORD_TOKEN="):
            token = line.split("=", 1)[1].strip()
            if token:
                return token
    return None


def cek_dependensi():
    """Cek library."""
    print(f"{C.GRAY}  Cek dependensi...{C.RESET}")
    try:
        import discord
        ver = getattr(discord, "__version__", "OK")
        print(f"{C.GRAY}    ✓ {C.WHITE}discord.py          {C.GREEN}{ver}{C.RESET}")
    except ImportError:
        print(f"{C.GRAY}    ✗ {C.WHITE}discord.py          {C.RED}MISSING{C.RESET}")
    try:
        from voice_orion import tts_supertonic_bytes
        print(f"{C.GRAY}    ✓ {C.WHITE}Supertonic TTS      {C.GREEN}OK{C.RESET}")
    except Exception:
        print(f"{C.GRAY}    ⚠ {C.WHITE}Supertonic TTS      {C.YELLOW}fallback{C.RESET}")
    try:
        import edge_tts
        print(f"{C.GRAY}    ✓ {C.WHITE}Edge TTS            {C.GREEN}OK{C.RESET}")
    except ImportError:
        print(f"{C.GRAY}    ⚠ {C.WHITE}Edge TTS            {C.YELLOW}MISSING{C.RESET}")
    print()


def main():
    clear()
    logo_ascii()
    info()
    
    print(f"{C.GRAY}  Load token...{C.RESET}")
    token = load_token()
    if not token:
        print(f"{C.RED}  ✗ Token tidak ditemukan di .env{C.RESET}")
        print(f"{C.YELLOW}  Tambah baris di .env:{C.RESET}")
        print(f"{C.GRAY}    DISCORD_TOKEN=TOKEN_KAMU{C.RESET}")
        print()
        input(f"{C.GRAY}  [Enter] keluar...{C.RESET}")
        sys.exit(1)
    
    print(f"{C.GREEN}  ✓ Token OK{C.RESET} {C.GRAY}({len(token)} karakter){C.RESET}")
    print()
    cek_dependensi()
    
    os.environ["DISCORD_TOKEN"] = token
    
    print(f"{C.DISCORD}{C.BOLD}  ◢◤ Start Discord bot... ◢◤{C.RESET}")
    print(f"{C.DISCORD}  ═════════════════════════════════════════════════{C.RESET}")
    print()
    
    try:
        from discord_voice_orion_v2 import client
        client.run(token)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}  ⚠ Bot dihentikan (Ctrl+C){C.RESET}")
    except Exception as e:
        print(f"\n{C.RED}  ✗ Error: {e}{C.RESET}")
        input(f"{C.GRAY}  [Enter] keluar...{C.RESET}")


if __name__ == "__main__":
    main()
