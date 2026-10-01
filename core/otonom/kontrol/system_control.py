"""system_control.py - Kontrol sistem Orion (JARVIS style)."""
import subprocess
import os
import platform
from pathlib import Path


def info_sistem() -> dict:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "sukses": True,
            "cpu": cpu,
            "ram_total": round(ram.total / (1024**3), 2),
            "ram_used": round(ram.used / (1024**3), 2),
            "ram_percent": ram.percent,
            "disk_total": round(disk.total / (1024**3), 2),
            "disk_used": round(disk.used / (1024**3), 2),
            "disk_percent": disk.percent,
            "os": platform.system(),
            "hostname": platform.node(),
        }
    except ImportError:
        return {"sukses": False, "pesan": "psutil tidak ada — pip install psutil"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def shutdown(delay: int = 60) -> dict:
    try:
        os.system(f"shutdown /s /t {delay}")
        return {"sukses": True, "pesan": f"Shutdown dalam {delay}s"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def restart(delay: int = 60) -> dict:
    try:
        os.system(f"shutdown /r /t {delay}")
        return {"sukses": True, "pesan": f"Restart dalam {delay}s"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def batalkan_shutdown() -> dict:
    try:
        os.system("shutdown /a")
        return {"sukses": True, "pesan": "Shutdown dibatalkan"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def lock() -> dict:
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return {"sukses": True, "pesan": "Lock"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def cek_network() -> dict:
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "8.8.8.8"],
            capture_output=True, text=True, timeout=5,
        )
        online = result.returncode == 0
        
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
        return {"sukses": True, "online": online, "hostname": hostname, "ip": ip}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST SYSTEM CONTROL")
    print("=" * 60)
    
    print("\n=== Info Sistem ===")
    hasil = info_sistem()
    if hasil["sukses"]:
        print(f"  CPU: {hasil['cpu']}%")
        print(f"  RAM: {hasil['ram_used']}/{hasil['ram_total']} GB ({hasil['ram_percent']}%)")
        print(f"  Disk: {hasil['disk_used']}/{hasil['disk_total']} GB ({hasil['disk_percent']}%)")
        print(f"  OS: {hasil['os']}")
        print(f"  Hostname: {hasil['hostname']}")
    
    print("\n=== Network ===")
    print(f"  {cek_network()}")
