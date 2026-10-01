"""orion_auto.py - Generate + Jalankan + Test. Auto-deteksi jenis app."""
import os, sys, time, subprocess, socket, re
from coding_assistant import coding_loop

def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def deteksi_jenis(kode):
    """Deteksi jenis aplikasi dari kode."""
    if "app.run(" in kode or "flask" in kode.lower():
        return "flask"
    if "tkinter" in kode or "Tk()" in kode:
        return "gui"
    if "uvicorn" in kode or "fastapi" in kode.lower():
        return "fastapi"
    return "script"

def main():
    goal = input("Goal: ").strip() or "Buat REST API Flask sederhana dengan endpoint /hello"

    print("\n[1/3] Generate kode...")
    hasil = coding_loop(goal, max_iterasi=3, nama_file="output_orion.py")
    if not hasil.get("sukses"):
        print("GAGAL:", hasil)
        return

    # Baca kode hasil
    with open("output_orion.py", "r", encoding="utf-8") as f:
        kode = f.read()

    jenis = deteksi_jenis(kode)
    print(f"\n[2/3] Jenis aplikasi terdeteksi: {jenis.upper()}")

    if jenis == "gui":
        print("  → Tkinter GUI - buka window, tidak bisa di-test otomatis")
        print("  → Jalankan manual: python output_orion.py")
        return

    if jenis not in ("flask", "fastapi"):
        print("  → Script biasa - jalankan untuk lihat output")
        subprocess.run([sys.executable, "output_orion.py"], timeout=10)
        return

    # Flask / FastAPI - jalankan server
    print("  Jalankan server...")
    proc = subprocess.Popen([sys.executable, "output_orion.py"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for _ in range(20):
        time.sleep(0.5)
        if port_open(5000):
            print("  Server jalan di http://127.0.0.1:5000")
            break
    else:
        print("  GAGAL start server")
        proc.terminate()
        return

    print("\n[3/3] Test endpoint...")
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:5000/hello", timeout=5) as r:
            print("  Status:", r.status)
            print("  Body:", r.read().decode()[:200])
    except Exception as e:
        print("  Test gagal:", e)

    print("\nTekan Enter untuk stop server...")
    input()
    proc.terminate()
    print("Server dihentikan.")

if __name__ == "__main__":
    main()
