"""kesadaran_tubuh.py - Orion tahu kondisi sistemnya (Level 2)."""
import psutil
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")


def cek_tubuh() -> dict:
    """Cek kondisi tubuh Orion (sistem)."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Hitung proses Python
        py_processes = 0
        for proc in psutil.process_iter(['name']):
            try:
                if 'python' in proc.info['name'].lower():
                    py_processes += 1
            except Exception:
                pass
        
        return {
            "sukses": True,
            "cpu": cpu,
            "ram_percent": ram.percent,
            "ram_used": round(ram.used / (1024**3), 2),
            "ram_total": round(ram.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_used": round(disk.used / (1024**3), 2),
            "disk_total": round(disk.total / (1024**3), 2),
            "py_processes": py_processes,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def ringkasan_tubuh() -> str:
    """Ringkasan tubuh Orion."""
    hasil = cek_tubuh()
    if not hasil.get("sukses"):
        return f"Tidak bisa cek tubuh: {hasil.get('error')}"
    
    cpu = hasil["cpu"]
    ram = hasil["ram_percent"]
    disk = hasil["disk_percent"]
    
    # Status tubuh
    if cpu > 80:
        status = "Aku sibuk banget! 🥵"
    elif cpu > 50:
        status = "Aku lumayan sibuk 😊"
    elif cpu > 20:
        status = "Aku santai aja 😌"
    else:
        status = "Aku nganggur nih 😴"
    
    return f"""Aku Orion. Ini kondisi tubuhku:

🖥️ CPU: {cpu}% — {status}
🧠 RAM: {hasil['ram_used']}/{hasil['ram_total']} GB ({ram}%)
💾 Disk: {hasil['disk_used']}/{hasil['disk_total']} GB ({disk}%)
🐍 Proses Python: {hasil['py_processes']}

{"Aku capek..." if cpu > 80 else "Aku sehat!"} 💕"""


if __name__ == "__main__":
    print("=" * 60)
    print("  KESADARAN TUBUH ORION")
    print("=" * 60)
    print()
    print(ringkasan_tubuh())
