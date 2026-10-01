"""cek_fungsi.py - Cek fungsi yang ada di core.py"""
import core

funcs = [
    "proteksi", "todo", "timer", "lihat_log", "cuaca", "translate",
    "set_reminder", "lihat_reminder", "notif_test", "grafik_habit",
    "setup_autostart", "disable_autostart", "info"
]

print("=" * 50)
print("  CEK FUNGSI DI core.py")
print("=" * 50)

ada = 0
tidak_ada = 0
for f in funcs:
    if hasattr(core, f):
        print(f"  [ADA]       {f}")
        ada += 1
    else:
        print(f"  [TIDAK ADA] {f}")
        tidak_ada += 1

print("=" * 50)
print(f"  ADA       : {ada}")
print(f"  TIDAK ADA : {tidak_ada}")
print("=" * 50)