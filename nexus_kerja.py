"""Bridge ORION -> worker Nexus.ai.

Cara pakai (dari folder mana aja):
    python nexus_kerja.py arya "buatkan 3 ide konten"
    python nexus_kerja.py --list

Bisa juga diimport langsung:
    from nexus_kerja import nexus_kerja
    print(nexus_kerja("arya", "buatkan ide konten"))

Sengaja 1 file, tanpa dependensi baru.
"""
import importlib
import os
import sys

NEXUS_DIR = os.environ.get("NEXUS_DIR", r"E:\Project Software\Nexus.ai")

AGENTS = {
    "arya": ("agents.arya", "arya_node"),
    "tony": ("agents.tony", "tony_node"),
    "juan": ("agents.juan", "juan_node"),
    "zulia": ("agents.zulia", "zulia_node"),
    "insan": ("agents.insan", "insan_node"),
    "raka": ("agents.raka", "raka_node"),
    "syifaa": ("agents.syifaa", "syifaa_node"),
    "jarvis": ("agents.jarvis", "jarvis_node"),
}

# alias nama (disamain kayak jarvis.py)
ALIAS = {
    "toni": "tony",
    "arie": "arya",
    "zul": "zulia",
    "sifa": "syifaa",
    "supervisor": "syifaa",
}


def daftar_agent():
    return sorted(AGENTS)


def nexus_kerja(agent, perintah, data_riset=""):
    """Lempar perintah ke worker Nexus.ai, balikin teks hasilnya."""
    nama = ALIAS.get(agent.strip().lower(), agent.strip().lower())
    if nama not in AGENTS:
        return "Agent '%s' tidak dikenal. Pilihan: %s" % (agent, ", ".join(daftar_agent()))
    if not perintah or not perintah.strip():
        return "Perintahnya kosong."

    mod_name, func_name = AGENTS[nama]
    cwd_lama = os.getcwd()
    try:
        os.chdir(NEXUS_DIR)  # worker baca path relatif (prompts/, .env)
        if NEXUS_DIR not in sys.path:
            sys.path.insert(0, NEXUS_DIR)
        # maksimal 2x percobaan kalau error/kosong
        _err_terakhir = None
        for _coba in range(2):
            try:
                mod = importlib.import_module(mod_name)
                func = getattr(mod, func_name)
                state = {"perintah": perintah, "data_riset": data_riset, "riwayat": []}
                hasil = func(state) or {}
                _cek = (hasil.get("konten") or hasil.get("output")
                        or hasil.get("data_riset") or "").strip()
                if _cek:
                    _err_terakhir = None
                    break
                _err_terakhir = "kosong"
            except Exception as _e:
                _err_terakhir = "%s: %s" % (type(_e).__name__, _e)
        else:
            hasil = {}
        if _err_terakhir == "kosong":
            hasil = {}
        elif _err_terakhir:
            return "Bridge error setelah 2x coba: %s" % _err_terakhir
    finally:
        os.chdir(cwd_lama)

    konten = (
        hasil.get("konten")
        or hasil.get("output")
        or hasil.get("data_riset")
        or "Agen tidak kasih hasil."
    )
    return konten


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print('Pakai: python nexus_kerja.py <agent> "<perintah>"')
        print("Agent:", ", ".join(daftar_agent()))
        return 0
    if argv[1] == "--list":
        print(", ".join(daftar_agent()))
        return 0
    if len(argv) < 3:
        print('Kurang perintah. Contoh: python nexus_kerja.py arya "buatkan ide konten"')
        return 1
    print(nexus_kerja(argv[1], argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
