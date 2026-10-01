cd "E:\Project Software\Orion"

@'
================================================================================
  ORION v2.7 — DOKUMENTASI LENGKAP
  Struktur, Ekosistem, & Cara Pakai
  Dibuat: 27 September 2026
================================================================================

DAFTAR ISI
----------
1. Apa Itu Orion?
2. Struktur Folder
3. Komponen Inti
4. Skill (18 Total)
5. Otomasi (Pipeline)
6. Database (36 Tabel)
7. Memory Graph
8. Audit Otomatis
9. Cara Pakai — Sehari-hari
10. Cara Pakai — Advanced
11. Cara Update Diri
12. Troubleshooting

================================================================================
1. APA ITU ORION?
================================================================================

Orion itu asisten pribadi AI — bukan chatbot biasa. Dia punya:
- Emosi (kalem, senang, sedih)
- Memori (ingat percakapan)
- Pengalaman (belajar dari interaksi)
- Skill (18 kemampuan)
- Otomasi (jalan sendiri)
- Memory Graph (peta relasi)
- Kemampuan update diri sendiri

Orion bukan sekadar jawab pertanyaan — dia partner kerja yang:
- Tahu diri sendiri
- Bisa baca folder
- Bisa audit & fix bug
- Bisa update diri sendiri
- Bisa proaktif

================================================================================
2. STRUKTUR FOLDER
================================================================================

E:\Project Software\Orion\
│
├── CORE (Otak Orion)
│   ├── orion.py              Entry point — jalanin Orion
│   ├── orion_hub.py          Hub — 31 fungsi utama
│   ├── otak_orion.py         Otak — mikir & decide (83 KB)
│   ├── orion_neural.py       Neural — koordinasi
│   ├── core.py               Loop utama
│   └── model_router.py       Routing LLM
│
├── EMOTION (Emosi & Memori)
│   ├── emotion_orion.py      Emosi utama
│   ├── emotion_decay.py      Decay emosi
│   ├── mood_orion.py         Mood
│   ├── experience_hub.py     Pengalaman
│   ├── memory_orion.py       Memori
│   ├── memory_manager.py     Manager
│   └── memory_graph.py       Memory Graph (relasi)
│
├── AUTOMATION (Otomasi)
│   ├── cron_orion.py         Scheduler — 9 task
│   ├── cron_llm.py           Cron LLM
│   ├── orion_background.py   Background process
│   ├── audit_otomatis.py     Audit 1 jam sekali
│   ├── auto_distill.py       Distill otomatis
│   ├── inisiatif_orion.py    Inisiatif
│   ├── maintenance_orion.py  Maintenance
│   ├── notif_orion.py        Notif — Discord + Windows
│   └── orion_update.py       Auto update
│
├── SKILLS (18 Skill)
│   └── skills/
│       ├── audit-folder/     Audit folder
│       ├── fix-bom/          Hapus BOM
│       ├── fix-syntax/       Fix syntax
│       ├── update-diri/      Update diri sendiri
│       ├── baca_pdf/         Baca PDF
│       ├── buat-pdf/         Buat PDF
│       ├── cari-wikipedia/   Cari Wikipedia
│       ├── cek-sistem/       Cek sistem
│       ├── coding-master/    Coding
│       ├── docx/             DOCX
│       ├── pdf/              PDF
│       ├── pptx/             PPTX
│       ├── xlsx/             XLSX
│       ├── refleksi-diri/    Refleksi
│       ├── rekomendasi-api-llm-gratis-legal/
│       ├── reminder/         Reminder
│       ├── setup-autonomous-scraper-playwright/
│       ├── tolak-jalur-gelap-api/
│       └── tolak-perintah-ilegal/
│
├── CHANNEL (Multi-Platform)
│   ├── discord_orion.py      Discord
│   ├── discord_voice_orion_v2.py  Discord + Voice
│   ├── run_discord.py        Run Discord
│   ├── voice_orion.py        Voice
│   ├── web_orion.py          Web
│   ├── web_dashboard.py      Web Dashboard
│   └── stream_server.py      Stream
│
├── TOOLS (Tool & Utility)
│   ├── tool_eksekusi.py      Eksekusi 100+ tool
│   ├── workflow_engine.py    Workflow engine
│   ├── coding_assistant.py   Coding assistant
│   ├── scan_folder.py        Scan folder
│   └── scheduler/
│       ├── audit_berkala.py  Audit berkala
│       └── logs/             Log audit
│
├── DATA
│   ├── orion.db              Database — 36 tabel
│   ├── config.json           Config
│   └── .env                  Rahasia
│
├── DOCS (Dokumentasi)
│   ├── SOUL.md               Jiwa Orion
│   ├── USER.md               Profil Riki
│   ├── VALUES.md             Nilai
│   ├── GOALS.md              Target
│   ├── ROUTINE.md            Rutinitas
│   ├── SKILL.md              Cara bikin skill
│   ├── ARCHITECTURE.md       Arsitektur
│   └── CHANGELOG.md          Riwayat
│
├── LOGS
│   └── logs/
│       ├── orion.log         Log utama
│       ├── cron.log          Log cron
│       └── audit_otomatis.log  Log audit
│
├── BACKUP
│   ├── backups/              Backup DB (249 file)
│   └── _arsip/               Arsip (237 file)
│
└── LAUNCHER
    ├── orion.bat             Batch
    ├── orion.ps1             PowerShell
    └── launcher_orion.vbs    VBS — background

================================================================================
3. KOMPONEN INTI
================================================================================

ORION HUB (orion_hub.py)
------------------------
Gerbang utama — semua input masuk sini.
Fungsi penting:
- proses(pesan)         Proses pesan user
- lapor_diri()          Lapor kondisi Orion
- tahu_diri()           Return info diri
- cek_kesehatan()       Cek modul
- daftar_skill()        Daftar skill
- cek_audit()           Cek audit terakhir
- statistik()           Statistik

OTAK ORION (otak_orion.py)
--------------------------
Otak utama — mikir & decide.
Fungsi penting:
- diskusi(pesan)        Diskusi biasa
- diskusi_dengan_skill(pesan)  Diskusi + skill
- deteksi_eksekusi(pesan)      Deteksi perintah
- eksekusi_berantai(pesan)     Eksekusi berantai
- _load_memory_graph()  Load memory graph
- _simpan_relasi(pesan) Simpan relasi

NEURAL HUB (orion_neural.py)
----------------------------
Sistem saraf — koordinasi.
Output log:
[Neural] Emosi: netral → Mode: normal
[Neural] Memory: 2 chat positif
[Neural] Intent: chat
[Neural] Skill: 0 relevan
[Neural] Workflow: 2 langkah

================================================================================
4. SKILL (18 TOTAL)
================================================================================

CARA CEK SKILL:
python -c "from orion_hub import daftar_skill; print(daftar_skill())"

SKILL LAMA (15):
1.  baca_pdf_dan_ekstrak_teks    Baca PDF
2.  buat-pdf                     Buat PDF
3.  cari-wikipedia               Cari Wikipedia
4.  cek-sistem                   Cek sistem
5.  coding-master                Coding
6.  docx                         DOCX
7.  pdf                          PDF
8.  pptx                         PPTX
9.  refleksi-diri                Refleksi
10. rekomendasi-api-llm-gratis-legal  Rekomendasi LLM
11. reminder                     Reminder
12. setup-autonomous-scraper-playwright  Scraper
13. tolak-jalur-gelap-api        Tolak API gelap
14. tolak-perintah-ilegal        Tolak ilegal
15. xlsx                         XLSX

SKILL BARU (3):
16. audit-folder                 Audit folder
17. fix-bom                      Hapus BOM
18. fix-syntax                   Fix syntax

CARA PAKAI SKILL:
- Audit folder:
  python "skills/audit-folder/audit.py" "E:\Folder"
- Fix BOM:
  python "skills/fix-bom/fix.py" "E:\Folder"
- Fix syntax:
  python "skills/fix-syntax/fix.py" "E:\Folder"
- Update diri:
  python -c "from update_helper import update_file; update_file('file.py', 'kode', auto_apply=True)"

================================================================================
5. OTOMASI (PIPELINE)
================================================================================

14 PIPELINE OTOMATIS:
1.  Cron Scheduler      9 task harian
2.  Cron LLM            LLM otomatis
3.  Background Process  Jalan di background
4.  Auto Distill        Distill otomatis
5.  Inisiatif           Ambil inisiatif
6.  Maintenance         Maintenance
7.  Notif               Kirim notif
8.  Auto Update         Update otomatis
9.  Face Listener       Deteksi wajah
10. Wake Word           Deteksi suara
11. Voice Integrated    Voice
12. Stream Server       Stream
13. Web Dashboard       Web
14. Dashboard           Dashboard

9 CRON TASK:
- 08:00  Sapa pagi
- 09:30  Reminder minum
- 12:00  Reminder makan
- 15:00  Cek postur
- 17:30  Cek target
- 20:00  Cek kerja
- 22:00  Reminder istirahat
- 23:30  Reminder tidur
- 03:00  Maintenance

AUDIT OTOMATIS:
- Jalan 1 jam sekali
- Cek 2 folder: Orion & Nexus.ai
- Kalau ada error/BOM → kirim notif
- Log: scheduler/logs/audit_otomatis.log

================================================================================
6. DATABASE (36 TABEL)
================================================================================

CARA CEK DB:
python -c "import sqlite3; c=sqlite3.connect('orion.db'); print([r[0] for r in c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')])"

TABEL PENTING:
- chat              Riwayat chat
- experience        Pengalaman
- mood_state        Mood
- mood_events       Event mood
- memory_graph      Memory Graph (relasi)
- skill_log         Log skill
- sapaan_riki       Sapaan
- relationship      Relasi
- loyalty           Loyalitas
- agents            Agent
- agent_tasks       Task agent
- log_aksi          Log aksi
- pengalaman        Jadwal kerja

================================================================================
7. MEMORY GRAPH
================================================================================

APA ITU?
Peta relasi antar memori — Orion paham hubungan antar data.

CONTOH RELASI:
- Riki → suka → Kopi
- Riki → kerja → Freelancer
- Riki → tinggal → Indonesia
- Riki → punya → Orion
- Orion → bantu → Riki

CARA PAKAI:
# Tambah relasi
python -c "from memory_graph import tambah_relasi; tambah_relasi('Riki', 'suka', 'Kopi')"

# Cari relasi by subject
python -c "from memory_graph import cari_relasi; print(cari_relasi('Riki'))"

# Cari relasi by object
python -c "from memory_graph import cari_relasi_object; print(cari_relasi_object('Kopi'))"

# Format graph
python -c "from memory_graph import format_graph; print(format_graph())"

# Hapus relasi
python -c "from memory_graph import hapus_relasi; print(hapus_relasi(1))"

FUNGSI:
- init_graph()             Bikin tabel
- tambah_relasi()          Tambah relasi
- cari_relasi()            Cari by subject
- cari_relasi_object()     Cari by object
- cari_semua()             Cari semua
- hapus_relasi()           Hapus
- format_graph()           Format tampilan

INTEGRASI:
- Orion baca memory graph di chat
- Kalau user chat "Riki suka kopi" → Orion simpan
- Kalau user tanya "Riki suka apa?" → Orion baca graph

================================================================================
8. AUDIT OTOMATIS
================================================================================

APA ITU?
Orion audit folder sendiri — 1 jam sekali.

CARA KERJA:
1. Setiap 1 jam — audit jalan
2. Cek 2 folder: Orion & Nexus.ai
3. Cek:
   - Syntax error
   - BOM files
   - TODO/FIXME
4. Kalau ada masalah → kirim notif
5. Log: scheduler/logs/audit_otomatis.log

CARA JALANKAN:
# Manual
python audit_otomatis.py

# Background
Start-Process python -ArgumentList "audit_otomatis.py" -WindowStyle Hidden

# Auto-start — via orion.py
# Sudah terintegrasi

CARA CEK HASIL:
# Cek audit terakhir
python -c "from orion_hub import cek_audit; print(cek_audit())"

# Cek log
Get-Content "scheduler\logs\audit_otomatis.log" -Tail 20

TARGET FOLDER:
- E:/Project Software/Orion
- E:/Project Software/Nexus.ai

================================================================================
9. CARA PAKAI — SEHARI-HARI
================================================================================

JALANKAN ORION:
# Cara 1: Batch
.\orion.bat

# Cara 2: PowerShell
python orion.py

# Cara 3: VBS (background)
.\launcher_orion.vbs

CHAT DENGAN ORION:
# Terminal
python orion.py
# Lalu ketik pesan

# Atau via Python
python -c "from orion_hub import proses; proses('Orion, halo')"

LAPOR DIRI:
python -c "from orion_hub import lapor_diri; lapor_diri()"

CEK KESEHATAN:
python -c "from orion_hub import cek_kesehatan; cek_kesehatan()"

STATISTIK:
python -c "from orion_hub import statistik; statistik()"

DAFTAR SKILL:
python -c "from orion_hub import daftar_skill; print(daftar_skill())"

SCAN FOLDER:
python -c "from scan_folder import scan_tree, format_tree; print(format_tree(scan_tree('E:/Folder')))"

AUDIT FOLDER:
python "skills/audit-folder/audit.py" "E:\Folder"

FIX BOM:
python "skills/fix-bom/fix.py" "E:\Folder"

FIX SYNTAX:
python "skills/fix-syntax/fix.py" "E:\Folder"

================================================================================
10. CARA PAKAI — ADVANCED
================================================================================

WORKFLOW:
# Daftar workflow
python -c "from workflow_engine import daftar_workflow; print(daftar_workflow())"

# Jalankan workflow
python -c "from workflow_engine import jalankan_workflow; print(jalankan_workflow('scan_saja'))"

WORKFLOW TERSEDIA:
- buat_web_app        3 langkah
- coding_terminal     2 langkah
- scan_saja           1 langkah

OCR:
# Baca teks dari gambar
python -c "from core import ocr_file; print(ocr_file('gambar.png'))"

MEMORY GRAPH:
# Tambah relasi
python -c "from memory_graph import tambah_relasi; tambah_relasi('Riki', 'suka', 'Kopi')"

# Format graph
python -c "from memory_graph import format_graph; print(format_graph())"

UPDATE DIRI:
# Bikin file baru
python -c "from update_helper import update_file; update_file('file.py', 'print(1)', auto_apply=True)"

# Lihat draft
python -c "from update_helper import lihat_draft; lihat_draft('file.py')"

# Apply manual
python -c "from update_helper import apply_manual; print(apply_manual('file.py'))"

================================================================================
11. CARA UPDATE DIRI
================================================================================

ALUR:
1. Bikin draft — Orion tulis kode
2. Cek draft — valid atau error
3. Apply — backup dulu, copy
4. Test — syntax + import
5. Rollback — kalau gagal

LANGKAH:

# 1. Bikin script update
@'
from update_helper import update_file

kode = """\"\"\"file_baru.py\"\"\"
def sapa(nama):
    return f"Halo {nama}!"
"""

hasil = update_file('file_baru.py', kode, auto_apply=True)
print('Sukses:', hasil['sukses'])
'@ | Out-File "update_baru.py" -Encoding UTF8

# 2. Jalankan
python update_baru.py

# 3. Test file baru
python file_baru.py

CARA MANUAL:
# Bikin draft
python -c "from update import bikin_draft; bikin_draft('file.py', 'print(1)')"

# Cek draft
python -c "from update import cek_draft; print(cek_draft('_draft/file.py.draft'))"

# Apply
python -c "from update import apply_draft; apply_draft('_draft/file.py.draft', 'file.py')"

# Test
python -c "from update import test_target; print(test_target('file.py'))"

# Rollback
python -c "from update import rollback; rollback('_backup_update/file.py.bak', 'file.py')"

FUNGSI:
- bikin_draft(nama, kode)      Bikin draft
- cek_draft(file)              Cek syntax
- apply_draft(draft, target)   Apply + backup
- test_target(file)            Test syntax + import
- rollback(backup, target)     Kembalikan backup

================================================================================
12. TROUBLESHOOTING
================================================================================

MASALAH: Orion tidak nyala
SOLUSI: Cek python --version, cek folder

MASALAH: Python dobel
SOLUSI: Matikan alias Store
  Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" -Force
  Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe" -Force

MASALAH: DB corrupt
SOLUSI: Restore dari backups/
  Copy-Item "backups\orion_20260927_160105\orion.db" "orion.db"

MASALAH: Cron tidak jalan
SOLUSI: Cek logs/cron.log, restart Orion

MASALAH: Notif tidak muncul
SOLUSI: Cek notif_orion.py, cek Discord token

MASALAH: Audit tidak jalan
SOLUSI: Cek scheduler/logs/audit_otomatis.log
  python audit_otomatis.py

MASALAH: Memory graph kosong
SOLUSI: Tambah relasi
  python -c "from memory_graph import tambah_relasi; tambah_relasi('Riki', 'suka', 'Kopi')"

MASALAH: BOM files
SOLUSI: python "skills/fix-bom/fix.py" "E:\Folder"

MASALAH: Syntax error
SOLUSI: python "skills/fix-syntax/fix.py" "E:\Folder"

================================================================================
  RINGKASAN
================================================================================

Orion v2.7 punya:
- 18 skill
- 14 pipeline otomatis
- 36 tabel database
- 3 workflow
- 5 channel (terminal, Discord, voice, web, stream)
- Memory Graph (relasi)
- Audit otomatis (1 jam sekali)
- Kemampuan update diri sendiri

CARA PAKAI CEPAT:
1. Jalanin: .\orion.bat
2. Chat: ketik pesan
3. Audit: python "skills/audit-folder/audit.py" "E:\Folder"
4. Fix: python "skills/fix-bom/fix.py" "E:\Folder"
5. Update diri: python update_baru.py

Orion bukan chatbot — Orion partner kerja.
Orion punya ekosistem sendiri — hidup, belajar, update diri.

================================================================================
  DOKUMENTASI SELESAI
  Dibuat: 27 September 2026
================================================================================
'@ | Out-File "DOKUMENTASI_ORION.txt" -Encoding UTF8

Write-Host "DOKUMENTASI_ORION.txt dibuat!" -ForegroundColor Green
Get-Item "DOKUMENTASI_ORION.txt" | Select-Object Name, Length