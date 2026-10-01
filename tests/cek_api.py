from pathlib import Path

env = Path(".env")
if not env.exists():
    print("File .env tidak ada!")
else:
    print("=" * 50)
    print("STATUS API KEY DI .env")
    print("=" * 50)
    print()
    for line in env.read_text(encoding="utf-8").splitlines():
        if "API_KEY" in line or "TOKEN" in line:
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if v and v not in ("", "xxxxx", "isi_key_kamu", "isi_api_key_kamu_di_sini"):
                    status = "OK"
                    preview = v[:12] + "..." if len(v) > 12 else v
                else:
                    status = "KOSONG"
                    preview = "(kosong)"
                print(f"  {k:25} : {status:7} {preview}")
    print()
