"""app_control.py - Kontrol aplikasi Orion (JARVIS style)."""
import subprocess
import os
from pathlib import Path

APPS = {
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "brave": "brave.exe",
    "vscode": "code.exe",
    "code": "code.exe",
    "cursor": "cursor.exe",
    "pycharm": "pycharm64.exe",
    "notepad": "notepad.exe",
    "notepadpp": "notepad++.exe",
    "discord": "discord.exe",
    "telegram": "telegram.exe",
    "whatsapp": "whatsapp.exe",
    "zoom": "zoom.exe",
    "slack": "slack.exe",
    "spotify": "spotify.exe",
    "vlc": "vlc.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "explorer": "explorer.exe",
    "taskmgr": "taskmgr.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "snipping": "snippingtool.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "steam": "steam.exe",
    "obs": "obs64.exe",
}


def buka_app(nama: str) -> dict:
    """Buka aplikasi."""
    nama_lower = nama.lower().strip()
    
    if nama_lower.startswith(("http://", "https://", "www.")):
        return buka_url(nama)
    
    exe = APPS.get(nama_lower, nama)
    
    if exe.startswith(("http://", "https://")):
        return buka_url(exe)
    
    try:
        if exe.startswith("http"):
            os.startfile(exe)
        else:
            subprocess.Popen(
                exe,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return {"sukses": True, "pesan": f"Membuka {nama}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Gagal buka {nama}: {e}"}


def buka_url(url: str) -> dict:
    """Buka URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        os.startfile(url)
        return {"sukses": True, "pesan": f"Membuka {url}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Gagal buka URL: {e}"}


def tutup_app(nama: str) -> dict:
    """Tutup aplikasi."""
    nama_lower = nama.lower().strip()
    exe = APPS.get(nama_lower, nama)
    
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", exe],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return {"sukses": True, "pesan": f"Menutup {nama}"}
        return {"sukses": False, "pesan": f"Gagal tutup {nama}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def list_app_aktif() -> dict:
    """List aplikasi yang jalan."""
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV"],
            capture_output=True, text=True, timeout=10,
        )
        lines = result.stdout.strip().split("\n")[1:]
        apps = []
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                apps.append(parts[0].strip('"'))
        return {"sukses": True, "apps": apps, "total": len(apps)}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST APP CONTROL")
    print("=" * 60)
    
    print("\n=== Test buka notepad ===")
    print(f"  {buka_app('notepad')}")
    
    print("\n=== Test list app ===")
    hasil = list_app_aktif()
    if hasil["sukses"]:
        print(f"  Total: {hasil['total']} app")
        for app in hasil["apps"][:5]:
            print(f"  - {app}")
