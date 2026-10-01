"""orion_report.py - Laporan mingguan Orion."""
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path("E:/Project Software/Orion")
REPORT_DIR = BASE / "arsip" / "reports"


def generate_report():
    """Generate laporan mingguan."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # === Load logs ===
    evolve_logs = []
    for folder in (BASE / "arsip").glob("evolve_*"):
        laporan = folder / "laporan.json"
        if laporan.exists():
            try:
                data = json.loads(laporan.read_text(encoding="utf-8"))
                evolve_logs.append(data)
            except Exception:
                pass
    
    # === Filter 7 hari terakhir ===
    seminggu_lalu = datetime.now() - timedelta(days=7)
    recent = []
    
    for log in evolve_logs:
        try:
            waktu = datetime.strptime(log["waktu"], "%Y-%m-%d %H:%M:%S")
            if waktu >= seminggu_lalu:
                recent.append(log)
        except Exception:
            pass
    
    # === Statistik ===
    total_error = sum(l.get("error_awal", 0) for l in recent)
    total_fix = sum(l.get("auto_fix", 0) for l in recent)
    total_manual = sum(l.get("manual", 0) for l in recent)
    
    # === Modul error ===
    from collections import Counter
    modules = Counter()
    for log in recent:
        for d in log.get("details", []):
            modules[d.get("mod", "unknown")] += 1
    
    # === Laporan ===
    laporan = {
        "periode": {
            "dari": seminggu_lalu.strftime("%Y-%m-%d"),
            "sampai": datetime.now().strftime("%Y-%m-%d"),
        },
        "total_evolve": len(recent),
        "total_error": total_error,
        "total_fix": total_fix,
        "total_manual": total_manual,
        "success_rate": round(total_fix / total_error * 100, 1) if total_error > 0 else 100,
        "top_modules": dict(modules.most_common(5)),
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # === Simpan ===
    filename = f"report_{datetime.now().strftime('%Y%m%d')}.json"
    REPORT_DIR.joinpath(filename).write_text(
        json.dumps(laporan, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    # === Tampilkan ===
    print("=" * 70)
    print("  ORION REPORT - LAPORAN MINGGUAN")
    print("=" * 70)
    print(f"\n  Periode: {laporan['periode']['dari']} - {laporan['periode']['sampai']}")
    print(f"  Total evolve: {laporan['total_evolve']}")
    print(f"  Total error: {laporan['total_error']}")
    print(f"  Auto-fix: {laporan['total_fix']}")
    print(f"  Manual: {laporan['total_manual']}")
    print(f"  Success rate: {laporan['success_rate']}%")
    
    if laporan["top_modules"]:
        print(f"\n  Modul paling sering error:")
        for m, c in laporan["top_modules"].items():
            print(f"    {m}: {c}")
    
    print("=" * 70)
    print(f"  Laporan: {REPORT_DIR.relative_to(BASE)}/{filename}")


if __name__ == "__main__":
    generate_report()
