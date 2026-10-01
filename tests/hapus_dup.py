from pathlib import Path

f = Path(r"E:\Project Software\Orion\cron_orion.py")
lines = f.read_text(encoding="utf-8").splitlines()

# Cari baris 'aksi = t.get' yang kedua (baris 107)
indices = [i for i, line in enumerate(lines) if 'aksi = t.get("aksi", "tts")' in line]
print(f"Ketemu {len(indices)} baris aksi di line: {[i+1 for i in indices]}")

if len(indices) >= 2:
    # Hapus yang kedua
    idx_hapus = indices[1]
    print(f"Hapus baris {idx_hapus+1}: {lines[idx_hapus].strip()}")
    del lines[idx_hapus]
    f.write_text("\n".join(lines), encoding="utf-8")
    print("OK. Duplikat dihapus.")
else:
    print("Cuma 1 baris, nggak perlu hapus.")
