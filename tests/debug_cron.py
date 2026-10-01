import cron_orion
import time

print("=== Test Cron Manual ===")
print()

# Cek task
tasks = cron_orion.load_tasks()
print(f"Total task: {len(tasks)}")
print()

# Cek jam sekarang vs task
from datetime import datetime
now = datetime.now().strftime("%H:%M")
print(f"Jam sekarang: {now}")
print()

# Cek task yang cocok jam ini
cocok = [t for t in tasks if t["jam"] == now]
print(f"Task yang cocok jam {now}: {len(cocok)}")
for t in cocok:
    print(f"  {t}")
print()

# Cek status cron
print("Status cron:", cron_orion.status())
print()

# Test thread
import threading
print(f"Thread aktif: {threading.active_count()}")
for t in threading.enumerate():
    print(f"  - {t.name} (alive={t.is_alive()})")
