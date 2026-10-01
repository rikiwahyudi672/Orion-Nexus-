# ============================================================
#  ORION LAUNCHER - Windows Terminal
#  Logo Discord + Menu + Warna
# ============================================================

# Warna ANSI
$C = @{
    Reset    = "`e[0m"
    Bold     = "`e[1m"
    Dim      = "`e[2m"
    Cyan     = "`e[96m"
    Blue     = "`e[94m"
    Green    = "`e[92m"
    Yellow   = "`e[93m"
    Red      = "`e[91m"
    Gray     = "`e[90m"
    White    = "`e[97m"
    Magenta  = "`e[95m"
    Discord  = "`e[38;5;99m"
    DiscordB = "`e[38;5;105m"
}

function Clear-Screen {
    Clear-Host
}

function Show-Logo {
    Write-Host ""
    Write-Host "$($C.Discord)$($C.Bold)     ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗$($C.Reset)"
    Write-Host "$($C.Discord)$($C.Bold)     ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗$($C.Reset)"
    Write-Host "$($C.Discord)$($C.Bold)     ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║$($C.Reset)"
    Write-Host "$($C.Discord)$($C.Bold)     ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║$($C.Reset)"
    Write-Host "$($C.Discord)$($C.Bold)     ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝$($C.Reset)"
    Write-Host "$($C.Discord)$($C.Bold)     ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝$($C.Reset)"
    Write-Host ""
    Write-Host "$($C.Discord)$($C.Bold)              ◢◤  ORION TERMINAL  ◢◤$($C.Reset)"
    Write-Host ""
}

function Show-Info {
    $waktu = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host "$($C.White)   Personal AI Assistant   $($C.Gray)│$($C.White)   Windows Terminal   $($C.Gray)│$($C.Cyan)   v2.0$($C.Reset)"
    Write-Host "$($C.Discord)  ─────────────────────────────────────────────────$($C.Reset)"
    Write-Host "$($C.Gray)   Owner   : $($C.White)Riki Wahyudi$($C.Reset)"
    Write-Host "$($C.Gray)   Waktu   : $($C.White)$waktu$($C.Reset)"
    Write-Host "$($C.Gray)   Voice   : $($C.Green)Supertonic (F1)$($C.Reset)"
    Write-Host "$($C.Gray)   LLM     : $($C.Green)Groq (gpt-oss-120b)$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
}

function Show-Menu {
    Write-Host "$($C.Cyan)$($C.Bold)  📋 MENU:$($C.Reset)"
    Write-Host ""
    Write-Host "$($C.White)   [1]$($C.Gray) 🎮 Discord Bot       $($C.Dim)│ Bot Discord dengan suara Orion$($C.Reset)"
    Write-Host "$($C.White)   [2]$($C.Gray) 🖥️  Dashboard CLI     $($C.Dim)│ Dashboard utama Orion$($C.Reset)"
    Write-Host "$($C.White)   [3]$($C.Gray) 💻 Coding Skill      $($C.Dim)│ Generate kode dari goal$($C.Reset)"
    Write-Host "$($C.White)   [4]$($C.Gray) 🎤 Voice Test        $($C.Dim)│ Test suara Orion$($C.Reset)"
    Write-Host "$($C.White)   [5]$($C.Gray) 🔍 Scan Folder       $($C.Dim)│ Scan folder Orion$($C.Reset)"
    Write-Host "$($C.White)   [6]$($C.Gray) ⚙️  Terminal          $($C.Dim)│ Buka PowerShell baru$($C.Reset)"
    Write-Host "$($C.White)   [7]$($C.Gray) 📊 Status Sistem     $($C.Dim)│ Cek status Orion$($C.Reset)"
    Write-Host "$($C.White)   [8]$($C.Gray) 📂 Buka Folder       $($C.Dim)│ Buka folder Orion$($C.Reset)"
    Write-Host "$($C.White)   [9]$($C.Gray) 📖 Bantuan           $($C.Dim)│ Cara pakai Orion$($C.Reset)"
    Write-Host "$($C.White)   [0]$($C.Gray) 🚪 Keluar$($C.Reset)"
    Write-Host ""
}

function Pause-Menu {
    Write-Host ""
    Write-Host "$($C.Gray)  [Enter] kembali ke menu...$($C.Reset)" -NoNewline
    Read-Host
}

function Jalankan-Discord {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  🎮 Start Discord Bot...$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    
    # Set working dir
    Set-Location "E:\Project Software\Orion"
    
    # Jalankan
    python run_discord.py
}

function Jalankan-Dashboard {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  🖥️  Start Dashboard Orion...$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    Set-Location "E:\Project Software\Orion"
    python orion.py
}

function Jalankan-Coding {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  💻 Coding Skill$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    $goal = Read-Host "$($C.Gray)  Goal coding$($C.Reset)"
    if ([string]::IsNullOrWhiteSpace($goal)) {
        Write-Host "$($C.Red)  ✗ Goal kosong$($C.Reset)"
        Pause-Menu
        return
    }
    Set-Location "E:\Project Software\Orion"
    python -c "from coding_assistant import coding_loop; hasil = coding_loop('$goal', max_iterasi=3, nama_file='output_orion.py'); print('HASIL:', hasil)"
    Pause-Menu
}

function Test-Voice {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  🎤 Test Voice Orion$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    $teks = Read-Host "$($C.Gray)  Teks yang diucapkan$($C.Reset)"
    if ([string]::IsNullOrWhiteSpace($teks)) { $teks = "Halo Rik, gue Orion" }
    Write-Host ""
    Write-Host "$($C.Gray)  Generate suara Orion...$($C.Reset)"
    Set-Location "E:\Project Software\Orion"
    python -c "from voice_orion import tts_supertonic_bytes; r = tts_supertonic_bytes('$teks'); open('test_voice.wav', 'wb').write(r) if r else None; print('OK' if r else 'GAGAL')"
    if (Test-Path "test_voice.wav") {
        Write-Host "$($C.Green)  ✓ Suara dibuat: test_voice.wav$($C.Reset)"
        Start-Process "test_voice.wav"
    }
    Pause-Menu
}

function Scan-Folder {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  🔍 Scan Folder$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    $folder = Read-Host "$($C.Gray)  Folder (Enter = Orion)$($C.Reset)"
    if ([string]::IsNullOrWhiteSpace($folder)) { $folder = "E:\Project Software\Orion" }
    Set-Location "E:\Project Software\Orion"
    python -c "from tool_eksekusi import scan_folder; r = scan_folder(folder=r'$folder'); print('OK:', r.get('total_file'), 'file' if r.get('sukses') else r.get('error'))"
    Pause-Menu
}

function Buka-Terminal {
    Start-Process "wt.exe" -ArgumentList "-d `"E:\Project Software\Orion`""
}

function Status-Sistem {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  📊 Status Sistem$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    Set-Location "E:\Project Software\Orion"
    python -c "from tool_eksekusi import cek_status; print(cek_status())"
    Pause-Menu
}

function Buka-Folder {
    Start-Process "explorer.exe" "E:\Project Software\Orion"
}

function Bantuan {
    Clear-Screen
    Show-Logo
    Write-Host "$($C.Cyan)$($C.Bold)  📖 Bantuan Orion$($C.Reset)"
    Write-Host "$($C.Discord)  ═════════════════════════════════════════════════$($C.Reset)"
    Write-Host ""
    Write-Host "$($C.White)  Discord Bot:$($C.Reset)"
    Write-Host "$($C.Gray)    join          - Bot masuk voice$($C.Reset)"
    Write-Host "$($C.Gray)    halo          - Sapaan$($C.Reset)"
    Write-Host "$($C.Gray)    coding X      - Generate kode$($C.Reset)"
    Write-Host "$($C.Gray)    scan folder X - Scan folder$($C.Reset)"
    Write-Host "$($C.Gray)    jalankan X    - Terminal$($C.Reset)"
    Write-Host ""
    Write-Host "$($C.White)  Terminal:$($C.Reset)"
    Write-Host "$($C.Gray)    python run_discord.py       - Discord bot$($C.Reset)"
    Write-Host "$($C.Gray)    python orion.py             - Dashboard$($C.Reset)"
    Write-Host "$($C.Gray)    python jalankan_skill_coding.py - Coding$($C.Reset)"
    Write-Host ""
    Pause-Menu
}

# ============ MAIN LOOP ============
function Main {
    while ($true) {
        Clear-Screen
        Show-Logo
        Show-Info
        Show-Menu
        
        Write-Host "$($C.Cyan)  Pilih$($C.Reset) $($C.Gray)[0-9]$($C.Reset) $($C.Gray)>$($C.Reset) " -NoNewline
        $pilihan = Read-Host
        
        switch ($pilihan) {
            "1" { Jalankan-Discord }
            "2" { Jalankan-Dashboard }
            "3" { Jalankan-Coding }
            "4" { Test-Voice }
            "5" { Scan-Folder }
            "6" { Buka-Terminal }
            "7" { Status-Sistem }
            "8" { Buka-Folder }
            "9" { Bantuan }
            "0" { 
                Clear-Screen
                Write-Host ""
                Write-Host "$($C.Discord)  👋 Sampai jumpa, Rik!$($C.Reset)"
                Write-Host ""
                exit
            }
            default {
                Write-Host "$($C.Red)  ✗ Pilihan tidak valid$($C.Reset)"
                Start-Sleep -Seconds 1
            }
        }
    }
}

# Start
Main
