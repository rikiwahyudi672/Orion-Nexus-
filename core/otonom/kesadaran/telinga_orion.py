"""telinga_orion.py - Telinga Orion: deteksi aktivitas Rik (Level 5)."""
import subprocess
import json
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
LOG_FILE = BASE / "logs" / "telinga.log"


def log(msg: str):
    """Log ke file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    waktu = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{waktu}] {msg}\n")


def window_aktif() -> dict:
    """Deteksi window yang sedang aktif."""
    try:
        # Pakai PowerShell untuk dapat window aktif
        ps_script = '''
        Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        using System.Text;
        public class Win {
            [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
            [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
            [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr hWnd, out int processId);
        }
"@
        $h = [Win]::GetForegroundWindow()
        $sb = New-Object System.Text.StringBuilder 256
        [Win]::GetWindowText($h, $sb, 256) | Out-Null
        $title = $sb.ToString()
        $pid = 0
        [Win]::GetWindowThreadProcessId($h, [ref]$pid) | Out-Null
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        Write-Output "$title|$($proc.ProcessName)"
        '''
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, text=True, timeout=10
        )
        
        output = result.stdout.strip()
        if "|" in output:
            title, proc = output.split("|", 1)
            return {
                "title": title.strip(),
                "process": proc.strip(),
                "waktu": datetime.now().isoformat(),
            }
        return {"title": "", "process": "", "waktu": datetime.now().isoformat()}
    except Exception as e:
        log(f"Error window_aktif: {e}")
        return {"title": "", "process": "", "error": str(e)}


def proses_aktif() -> list:
    """Daftar proses yang jalan (top 10 by CPU)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WS | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return [{"nama": p.get("Name", ""), "cpu": p.get("CPU", 0)} for p in data]
        return []
    except Exception as e:
        log(f"Error proses_aktif: {e}")
        return []


def deteksi_aktivitas() -> dict:
    """Deteksi aktivitas Rik secara keseluruhan."""
    win = window_aktif()
    proc = proses_aktif()
    
    # Klasifikasi aktivitas
    title_lower = win.get("title", "").lower()
    proc_lower = win.get("process", "").lower()
    
    aktivitas = "unknown"
    
    # Coding
    if any(k in title_lower for k in ["visual studio", "vscode", "code", "pycharm", "sublime", "notepad++", "cursor"]):
        aktivitas = "coding"
    elif any(k in proc_lower for k in ["code", "devenv", "pycharm", "cursor"]):
        aktivitas = "coding"
    
    # Browser
    elif any(k in title_lower for k in ["chrome", "firefox", "edge", "brave"]):
        if any(k in title_lower for k in ["youtube", "netflix", "film", "movie"]):
            aktivitas = "nonton"
        elif any(k in title_lower for k in ["github", "stackoverflow", "docs"]):
            aktivitas = "belajar"
        else:
            aktivitas = "browsing"
    
    # Game
    elif any(k in title_lower for k in ["game", "steam", "valorant", "dota", "ml", "pubg", "genshin"]):
        aktivitas = "gaming"
    elif any(k in proc_lower for k in ["steam", "riot", "epicgames", "game"]):
        aktivitas = "gaming"
    
    # Kerja
    elif any(k in title_lower for k in ["word", "excel", "powerpoint", "office", "docs", "sheets"]):
        aktivitas = "kerja"
    
    # Komunikasi
    elif any(k in title_lower for k in ["discord", "whatsapp", "telegram", "slack", "zoom", "meet"]):
        aktivitas = "komunikasi"
    
    # Musik
    elif any(k in title_lower for k in ["spotify", "music", "youtube music"]):
        aktivitas = "musik"
    
    # Terminal
    elif any(k in title_lower for k in ["powershell", "cmd", "terminal", "bash"]):
        aktivitas = "terminal"
    
    return {
        "window": win,
        "proses": proc[:5],
        "aktivitas": aktivitas,
        "waktu": datetime.now().isoformat(),
    }


def ringkasan() -> str:
    """Ringkasan aktivitas untuk prompt LLM."""
    data = deteksi_aktivitas()
    win = data["window"]
    return f"""Aktivitas Rik sekarang:
- Window: {win.get('title', '?')[:80]}
- Proses: {win.get('process', '?')}
- Aktivitas: {data['aktivitas']}"""


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST TELINGA ORION")
    print("=" * 70)
    
    data = deteksi_aktivitas()
    print(f"\nWindow aktif:")
    print(f"  Title: {data['window'].get('title', '?')}")
    print(f"  Proses: {data['window'].get('process', '?')}")
    print(f"\nAktivitas: {data['aktivitas']}")
    print(f"\nProses aktif (top 5):")
    for p in data["proses"]:
        print(f"  - {p['nama']} (CPU: {p['cpu']})")
