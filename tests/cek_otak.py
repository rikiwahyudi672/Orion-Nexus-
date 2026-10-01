"""cek_otak.py - Test akurasi otak ORION"""
import core

ekspektasi = {
    0: "tidur", 1: "tidur", 2: "tidur", 3: "tidur", 4: "tidur",
    5: "tidur", 6: "makan", 7: "kerja", 8: "kerja", 9: "kerja",
    10: "kerja", 11: "kerja", 12: "makan", 13: "kerja", 14: "kerja",
    15: "kerja", 16: "kerja", 17: "kerja", 18: "santai", 19: "santai",
    20: "santai", 21: "santai", 22: "tidur", 23: "tidur",
}

otak = core.Otak()
print("=" * 60)
print("  TEST OTAK ORION SEKARANG")
print("=" * 60)
print(f"{'Jam':<8} {'Prediksi':<10} {'Conf':<8} {'Harusnya':<10} {'Status'}")
print("-" * 60)

benar = 0
total = 0
for jam in range(24):
    akt, conf = otak.prediksi(jam)
    harus = ekspektasi[jam]
    status = "OK" if akt == harus else "SALAH"
    if akt == harus:
        benar += 1
    total += 1
    print(f"{jam:02d}:00    {akt:<10} {conf*100:>5.1f}%   {harus:<10} {status}")

print()
print("=" * 60)
akurasi = (benar / total) * 100
print(f"  AKURASI: {benar}/{total} ({akurasi:.1f}%)")
print("=" * 60)