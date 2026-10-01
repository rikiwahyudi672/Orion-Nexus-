"""test_otak_v2.py - Test semua fitur Otak v2"""
import core

print("=" * 60)
print("  TEST OTAK v2 - ORION")
print("=" * 60)

# Init otak
otak = core.Otak()

# 1. Cek DATA_HABIT
print(f"\n[1] DATA_HABIT: {len(core.DATA_HABIT)} titik")

# 2. Prediksi biasa
print("\n[2] Prediksi biasa:")
for jam in [7.0, 8.5, 12.0, 15.5, 19.0, 23.0]:
    akt, conf = otak.prediksi(jam)
    print(f"    Jam {jam:04.1f} -> {akt} ({conf*100:.1f}%)")

# 3. Top-N prediksi
print("\n[3] Top-N prediksi (n=3):")
for jam in [8.0, 12.0, 19.0]:
    top = otak.prediksi_top_n(jam, n=3)
    print(f"    Jam {jam:04.1f}:")
    for i, (akt, conf) in enumerate(top, 1):
        print(f"      {i}. {akt} ({conf*100:.1f}%)")

# 4. Simpan pengalaman
print("\n[4] Simpan pengalaman:")
ok, msg = otak.simpan_pengalaman(8.0, "kerja", hari="Senin")
print(f"    Jam 8 kerja (Senin): {msg}")
ok, msg = otak.simpan_pengalaman(8.0, "kerja", hari="Selasa")
print(f"    Jam 8 kerja (Selasa): {msg}")

# 5. Hitung pengalaman
n = otak.hitung_pengalaman()
print(f"\n[5] Total pengalaman: {n}")

# 6. Prediksi per hari
print("\n[6] Prediksi per hari:")
akt, conf = otak.prediksi_per_hari(8.0, "Senin")
print(f"    Senin jam 8 -> {akt} ({conf*100:.1f}%)")
akt, conf = otak.prediksi_per_hari(8.0, "Minggu")
print(f"    Minggu jam 8 -> {akt} ({conf*100:.1f}%)")

# 7. Test retrain (verbose)
print("\n[7] Test retrain dari pengalaman:")
ok = otak.retrain_dari_pengalaman(verbose=True)
print(f"    Retrain: {'OK' if ok else 'SKIP'}")

# 8. Test prediksi ulang setelah retrain
print("\n[8] Prediksi setelah retrain:")
akt, conf = otak.prediksi(8.0)
print(f"    Jam 8 -> {akt} ({conf*100:.1f}%)")

print()
print("=" * 60)
print("  TEST SELESAI")
print("=" * 60)