import otak_orion

print("=" * 60)
print("TEST COMMANDER MODE")
print("=" * 60)
print()

perintah = "Cari 3 fakta unik tentang Indonesia, lalu tulis puisi pendek tentang Riki"
print(f"Perintah: {perintah}")
print()
print("Orion bagi tugas...")
print()

try:
    jawaban = otak_orion.commander(perintah)
    print("=" * 60)
    print("HASIL:")
    print("=" * 60)
    print(jawaban)
except Exception as e:
    import traceback
    traceback.print_exc()
