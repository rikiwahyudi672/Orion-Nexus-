# ===PATCH===
# TYPE: append
# TARGET: core.py
# DESC: Tambah 13 fungsi yang hilang (proteksi, todo, timer, dll)
# ===END===

# ============ 31. PROTEKSI FOLDER ============
def proteksi():
    """Cek folder terlarang & aman."""
    print("\n" + "=" * 55)
    print("  PROTEKSI FOLDER - ORION")
    print("=" * 55)
    terlarang = CFG["proteksi"]["folder_terlarang"]
    aman = CFG["proteksi"]["folder_aman"]

    print("\n  [FOLDER TERLARANG]")
    for f in terlarang:
        status = "ADA" if Path(f).exists() else "TIDAK ADA"
        print(f"    - {f} [{status}]")

    print("\n  [FOLDER AMAN]")
    for f in aman:
        status = "ADA" if Path(f).exists() else "TIDAK ADA"
        print(f"    - {f} [{status}]")

    print("\n" + "=" * 55)
    catat("Cek proteksi")


# ============ 32. TO-DO LIST ============
def todo():
    """To-Do list sederhana."""
    while True:
        print("\n" + "=" * 55)
        print("  TO-DO LIST - ORION")
        print("=" * 55)

        rows = db_exec("SELECT id, tugas, selesai FROM todo ORDER BY selesai, id")
        if not rows:
            print("\n  (belum ada tugas)")
        else:
            print()
            for id_t, tugas, selesai in rows:
                mark = "[x]" if selesai else "[ ]"
                print(f"  {mark} #{id_t} {tugas}")

        print("\n  [1] Tambah  [2] Selesai  [3] Hapus  [0] Kembali")
        p = input("  Pilih: ").strip()

        if p == "1":
            tugas = input("  Tugas baru: ").strip()
            if tugas:
                db_exec("INSERT INTO todo (tugas, dibuat) VALUES (?, ?)",
                        (tugas, datetime.now().isoformat()))
                print(f"  Ditambah: {tugas}")
        elif p == "2":
            try:
                id_t = int(input("  ID yang selesai: "))
                db_exec("UPDATE todo SET selesai = 1 WHERE id = ?", (id_t,))
                print(f"  #{id_t} selesai")
            except:
                print("  ID tidak valid")
        elif p == "3":
            try:
                id_t = int(input("  ID yang dihapus: "))
                db_exec("DELETE FROM todo WHERE id = ?", (id_t,))
                print(f"  #{id_t} dihapus")
            except:
                print("  ID tidak valid")
        elif p == "0":
            return


# ============ 33. TIMER ============
def timer():
    """Timer countdown."""
    try:
        menit = float(input("  Timer (menit): ").strip())
    except:
        print("  Input tidak valid")
        return

    total = int(menit * 60)
    print(f"  Timer {menit} menit dimulai...")

    try:
        for sisa in range(total, -1, -1):
            m, s = divmod(sisa, 60)
            print(f"\r  [{m:02d}:{s:02d}] tersisa", end="", flush=True)
            time.sleep(1)
        print("\n  WAKTU HABIS!")
        try:
            tts_bicara(f"Timer {menit} menit selesai")
        except:
            pass
        catat(f"Timer {menit} menit")
    except KeyboardInterrupt:
        print("\n  Timer dibatalkan")


# ============ 34. LIHAT LOG ============
def lihat_log(limit=20):
    """Lihat log aktivitas."""
    rows = db_exec(
        "SELECT aksi, waktu FROM log_aksi ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    print("\n" + "=" * 55)
    print(f"  LOG AKTIVITAS ({len(rows)} terakhir)")
    print("=" * 55)
    if not rows:
        print("  (belum ada log)")
    else:
        for aksi, waktu in rows:
            print(f"  [{waktu[:19]}] {aksi}")
    print("=" * 55)


# ============ 35. CUACA (alias) ============
def cuaca():
    """Alias cuaca_plus()."""
    return cuaca_plus()


# ============ 36. TRANSLATE ============
def translate():
    """Buka Google Translate di browser."""
    print("  [1] Indonesia -> Inggris")
    print("  [2] Inggris -> Indonesia")
    print("  [3] Custom")
    p = input("  Pilih: ").strip()

    teks = input("  Teks yang mau diterjemah: ").strip()
    if not teks:
        return

    from urllib.parse import quote
    if p == "1":
        url = f"https://translate.google.com/?sl=id&tl=en&text={quote(teks)}"
    elif p == "2":
        url = f"https://translate.google.com/?sl=en&tl=id&text={quote(teks)}"
    else:
        url = f"https://translate.google.com/?text={quote(teks)}"

    webbrowser.open(url)
    print("  Google Translate dibuka di browser")
    catat(f"Translate: {teks[:30]}")


# ============ 37. SET REMINDER ============
def set_reminder():
    """Set reminder ke database."""
    con = sqlite3.connect(P["db"])
    con.execute("""CREATE TABLE IF NOT EXISTS reminder (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jam TEXT, pesan TEXT, aktif INTEGER DEFAULT 1,
        dibuat TEXT
    )""")
    con.commit()
    con.close()

    jam = input("  Jam (HH:MM): ").strip()
    pesan = input("  Pesan: ").strip()
    if not jam or not pesan:
        print("  Jam & pesan wajib")
        return

    db_exec(
        "INSERT INTO reminder (jam, pesan, dibuat) VALUES (?, ?, ?)",
        (jam, pesan, datetime.now().isoformat())
    )
    print(f"  Reminder set: {jam} - {pesan}")
    catat(f"Reminder: {jam}")


# ============ 38. LIHAT REMINDER ============
def lihat_reminder():
    """Lihat reminder aktif."""
    rows = db_exec("SELECT id, jam, pesan FROM reminder WHERE aktif = 1 ORDER BY jam")
    print("\n" + "=" * 55)
    print("  REMINDER AKTIF")
    print("=" * 55)
    if not rows:
        print("  (belum ada reminder)")
    else:
        for id_r, jam, pesan in rows:
            print(f"  #{id_r} [{jam}] {pesan}")
    print("=" * 55)


# ============ 39. NOTIF TEST ============
def notif_test():
    """Test notifikasi Windows."""
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(
            "ORION",
            "Test notifikasi berhasil!",
            duration=5,
            threaded=True
        )
        print("  Notifikasi dikirim")
    except ImportError:
        print("  Install dulu: pip install win10toast")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 40. GRAFIK HABIT ============
def grafik_habit():
    """Grafik aktivitas dari log."""
    try:
        rows = db_exec(
            "SELECT substr(waktu, 1, 13) as jam, COUNT(*) FROM log_aksi GROUP BY jam ORDER BY jam DESC LIMIT 10"
        )
        print("\n" + "=" * 55)
        print("  GRAFIK AKTIVITAS (10 jam terakhir)")
        print("=" * 55)
        if not rows:
            print("  (belum ada data)")
        else:
            for jam, count in rows:
                bar = "#" * min(count, 40)
                print(f"  {jam}  {bar} ({count})")
        print("=" * 55)
    except Exception as e:
        print(f"  Error: {e}")


# ============ 41. SETUP AUTOSTART ============
def setup_autostart():
    """Set ORION auto-start pas Windows nyala."""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        exe = f'pythonw "{Path(P["base"]) / "orion.py"}"'
        winreg.SetValueEx(key, "ORION", 0, winreg.REG_SZ, exe)
        winreg.CloseKey(key)
        print("  Auto-start AKTIF")
        catat("Auto-start ON")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 42. DISABLE AUTOSTART ============
def disable_autostart():
    """Matikan auto-start."""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "ORION")
            print("  Auto-start DIMATIKAN")
        except FileNotFoundError:
            print("  Auto-start belum aktif")
        winreg.CloseKey(key)
        catat("Auto-start OFF")
    except Exception as e:
        print(f"  Error: {e}")


# ============ 43. INFO ORION ============
def info():
    """Info tentang ORION."""
    print("\n" + "=" * 55)
    print("  INFO ORION")
    print("=" * 55)
    print(f"  Nama     : {CFG.get('project', 'ORION')}")
    print(f"  Versi    : {CFG.get('version', '2.0')}")
    print(f"  Owner    : {CFG.get('owner', 'Riki Wahyudi')}")
    print(f"  Tagline  : {CFG.get('tagline', 'Personal AI Assistant')}")
    print()
    print(f"  Base     : {P['base']}")
    print(f"  Model    : {P['model']}")
    print(f"  DB       : {P['db']}")
    print()
    model = Path(P["model"])
    if model.exists():
        size = model.stat().st_size
        print(f"  Model    : ADA ({size} bytes)")
    else:
        print(f"  Model    : BELUM ADA (latih dulu)")
    print()
    print(f"  Aktivitas: {CFG['model']['aktivitas']}")
    print("=" * 55)