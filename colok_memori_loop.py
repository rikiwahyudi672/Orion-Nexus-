#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""colok_memori_loop.py -- Colok memori jangka panjang ke JALUR CHAT LIVE ORION.

Beda dengan colok_memori.py (versi lama, nempel di dashboard): versi ini
nempel LANGSUNG di orion_tool_loop.chat(), jadi berlaku untuk SEMUA pemanggil
(chat dashboard, Discord, web) — bukan cuma submenu_chat.

Yang dikerjakan di orion_tool_loop.py:
  P1: recall  -> 5 chat terakhir ditempel ke system prompt, HANYA kalau
                  riwayat RAM kosong/pendek (<4). Fail-safe.
  P2: save    -> tiap jawaban final disimpan ke orion.db. Fail-safe.
  P3: konsolidasi throttled (max 1x/7 hari) tiap sesi chat baru. Fail-safe.
Bonus di konsolidasi_memory.py (kalau ada):
  P4: betulkan path DB yang ngaco + _conn defensif (sekarang bikin DB hantu).

JANGAN jalankan colok_memori.py versi lama setelah ini (dobel memori).

Aman: backup .bak | --kering simulasi | idempoten | compile-check.
Gagal compile -> backup dipulihkan otomatis.

Pakai:
    python colok_memori_loop.py [--kering] [path_folder_orion]
    python colok_memori_loop.py --tes [path_folder_orion]  -> uji wiring
"""
import subprocess
import shutil
import sys
from datetime import datetime
from pathlib import Path

KERING = "--kering" in sys.argv
TES = "--tes" in sys.argv
sisa = [a for a in sys.argv[1:] if not a.startswith("-")]
ROOT = Path(sisa[0]).resolve() if sisa else Path(__file__).parent.resolve()
LOOP = ROOT / "orion_tool_loop.py"

G = "[OK]"
R = "[XX]"
W = "[!!]"

BLOK_MEMORI = [
    "",
    "# === MEMORI JANGKA PANJANG (ditambah colok_memori_loop.py) ===",
    "import time as _time_mem",
    '_MEM_MOD = "belum"',
    '_MEM_KONSOLIDASI = "belum"',
    '_KATA_NEGATIF = ["dimaki", "maki", "sedih", "marah", "kesal", "capek",',
    '                 "bete", "badmood", "benci", "nyerah", "salah", "maaf",',
    '                 "kenapa", "kesalahan", "error"]',
    "",
    "def _cari_modul(nama_file):",
    '    """Cari modul di root/memory/core, load via spec. Fail-safe."""',
    '    for _rel in (nama_file, "memory/" + nama_file, "core/" + nama_file):',
    "        _p = BASE / _rel",
    "        if _p.exists():",
    "            try:",
    "                _spec = importlib.util.spec_from_file_location(",
    '                    "orion_" + nama_file.replace(".py", ""), str(_p))',
    "                _mod = importlib.util.module_from_spec(_spec)",
    "                _spec.loader.exec_module(_mod)",
    "                return _mod",
    "            except Exception:",
    "                return None",
    "    return None",
    "",
    "def _mem():",
    '    """Modul memory_manager (cache). None kalau tidak ketemu."""',
    "    global _MEM_MOD",
    '    if _MEM_MOD == "belum":',
    '        _MEM_MOD = _cari_modul("memory_manager.py")',
    "        if _MEM_MOD is not None:",
    "            try:",
    "                _MEM_MOD.init()",
    "            except Exception:",
    "                pass",
    "    return _MEM_MOD",
    "",
    "def _recall_memori(n=5):",
    '    """Ambil n chat terakhir -> teks konteks. \'\' kalau gagal."""',
    "    try:",
    "        _m = _mem()",
    "        if _m is None:",
    '            return ""',
    "        _ctx = _m.ambil_konteks(n) or []",
    "        _bagus = []",
    "        for _k in _ctx:",
    '            _gab = str(_k.get("user", "")) + " " + str(_k.get("orion", ""))',
    "            if any(_w in _gab.lower() for _w in _KATA_NEGATIF):",
    "                continue",
    "            _bagus.append(_k)",
    "        if not _bagus:",
    '            return ""',
    '        _t = ("\\n\\n[MEMORI PERCAKAPAN TERAKHIR \\u2014 pakai kalau relevan, "',
    '              "jangan sebut kamu membaca memori kecuali ditanya]\\n")',
    "        for _k in _bagus:",
    '            _t += "User: " + str(_k.get("user", ""))[:120] + "\\n"',
    '            _t += "Orion: " + str(_k.get("orion", ""))[:120] + "\\n"',
    "        return _t",
    "    except Exception:",
    '        return ""',
    "",
    "def _simpan_memori(user_pesan, orion_pesan):",
    '    """Simpan 1 pasang chat. Fail-safe."""',
    "    try:",
    "        _m = _mem()",
    "        if _m is None:",
    "            return",
    "        _m.simpan_chat(user_pesan, orion_pesan)",
    "    except Exception:",
    "        pass",
    "",
    "def _konsolidasi_throttled(hari=7):",
    '    """Konsolidasi max 1x per `hari`. Fail-safe."""',
    "    global _MEM_KONSOLIDASI",
    "    try:",
    '        if _MEM_KONSOLIDASI == "belum":',
    '            _MEM_KONSOLIDASI = _cari_modul("konsolidasi_memory.py")',
    "        if _MEM_KONSOLIDASI is None:",
    "            return",
    '        _stamp = BASE / ".konsolidasi_terakhir"',
    "        _now = _time_mem.time()",
    "        if _stamp.exists():",
    "            try:",
    "                if _now - float(_stamp.read_text().strip()) < hari * 86400:",
    "                    return",
    "            except Exception:",
    "                pass",
    "        _MEM_KONSOLIDASI.konsolidasi()",
    "        try:",
    "            _stamp.write_text(str(_now))",
    "        except Exception:",
    "            pass",
    "    except Exception:",
    "        pass",
]

BLOK_CARI_DB = [
    "",
    "# === CARI DB (ditambah colok_memori_loop.py) ===",
    "def _cari_db():",
    '    """Cari orion.db yang beneran ada. Fail-safe."""',
    "    from pathlib import Path as _P",
    "    _b = _P(__file__).parent",
    '    for _p in [_b / "orion.db", _b / "memory" / "orion.db",',
    '               _b.parent / "orion.db", _b.parent / "memory" / "orion.db"]:',
    "        if _p.exists():",
    "            return _p",
    '    return _b / "orion.db"',
]


def pecah(src):
    out = []
    for ln in src.split("\n"):
        out.append((ln[:-1], "\r") if ln.endswith("\r") else (ln, ""))
    return out


def gabung(baris):
    return "\n".join(b + e for b, e in baris)


def cari(isi, teks):
    return [i for i, b in enumerate(isi) if b == teks]


def compile_cek(path):
    r = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or "")[:200]


def patch_loop(kering):
    if not LOOP.exists():
        print(f"{R} tidak ketemu: {LOOP}")
        return False
    src = LOOP.read_text(encoding="utf-8", errors="replace")
    baris = pecah(src)
    isi = [b for b, _ in baris]
    ubah = 0

    # P1: blok helper sebelum LOAD SOUL
    if "_recall_memori" in src:
        print(f"{G} P1 helper memori: sudah ada, lewati")
    else:
        idx = cari(isi, "# === LOAD SOUL ===")
        if len(idx) != 1:
            print(f"{R} P1: jangkar LOAD SOUL ketemu {len(idx)}x, BATAL")
            return False
        i = idx[0]
        baris[i:i] = [(b, "") for b in BLOK_MEMORI]
        isi = [b for b, _ in baris]
        ubah += 1
        print(f"{G} P1 helper memori: disisipkan")

    # P2: recall + konsolidasi sebelum messages dibangun
    if "len(riwayat) < 4" in src:
        print(f"{G} P2 recall: sudah ada, lewati")
    else:
        jangkar = '    messages = [{"role": "system", "content": system}]'
        idx = cari(isi, jangkar)
        if len(idx) != 1:
            print(f"{R} P2: jangkar messages ketemu {len(idx)}x, BATAL")
            return False
        i = idx[0]
        baru = ["    if not riwayat or len(riwayat) < 4:",
                "        system = system + _recall_memori()",
                "        _konsolidasi_throttled()",
                jangkar]
        baris[i:i + 1] = [(b, "") for b in baru]
        isi = [b for b, _ in baris]
        ubah += 1
        print(f"{G} P2 recall ditempel ke chat()")

    # P3: simpan sebelum return jawaban final
    if "_simpan_memori(pesan," in src:
        print(f"{G} P3 simpan: sudah ada, lewati")
    else:
        jangkar = "            return jawaban.strip()  # jawaban final"
        idx = cari(isi, jangkar)
        if len(idx) != 1:
            print(f"{R} P3: jangkar return ketemu {len(idx)}x, BATAL")
            return False
        i = idx[0]
        baru = ["            _simpan_memori(pesan, jawaban.strip())",
                jangkar]
        baris[i:i + 1] = [(b, "") for b in baru]
        ubah += 1
        print(f"{G} P3 simpan_chat ditempel")

    if kering:
        print(f"{G} simulasi: {ubah} patch akan diterapkan")
        return True
    if ubah == 0:
        print(f"{G} tidak ada yang berubah")
        return True
    bak = LOOP.parent / f"orion_tool_loop.py.bak_colokmemori_{datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(LOOP, bak)
    print(f"{G} backup: {bak.name}")
    LOOP.write_text(gabung(baris), encoding="utf-8")
    ok, err = compile_cek(LOOP)
    if not ok:
        shutil.copy2(bak, LOOP)
        print(f"{R} compile GAGAL ({err}) -> dipulihkan")
        return False
    print(f"{G} compile OK")
    return True


def patch_konsolidasi(kering):
    for rel in ("konsolidasi_memory.py", "memory/konsolidasi_memory.py",
                "core/konsolidasi_memory.py"):
        p = ROOT / rel
        if p.exists():
            break
    else:
        print(f"{W} P4: konsolidasi_memory.py tidak ketemu, lewati")
        return True
    src = p.read_text(encoding="utf-8", errors="replace")
    baris = pecah(src)
    isi = [b for b, _ in baris]
    ubah = 0

    if "_cari_db" not in src:
        jelek = 'DB = BASE / "memory" / str(BASE / "memory" / "orion.db")'
        idx = cari(isi, jelek)
        if len(idx) == 1:
            i = idx[0]
            baris[i:i + 1] = [(b, "") for b in BLOK_CARI_DB] + [("DB = _cari_db()", baris[i][1])]
            isi = [b for b, _ in baris]
            src = gabung(baris)
            ubah += 1
            print(f"{G} P4a path DB dibetulkan ({rel})")
        else:
            print(f"{W} P4a: pola DB tidak dikenali, lewati")
    else:
        print(f"{G} P4a path DB: sudah benar, lewati")

    if "_cari_db()" in src and "def _conn():" in src:
        # pastikan _conn memakai _cari_db
        j1 = 'def _conn():'
        j2 = '    return sqlite3.connect(str(DB))'
        i1, i2 = cari(isi, j1), cari(isi, j2)
        if len(i1) == 1 and len(i2) == 1 and i2[0] == i1[0] + 1:
            baris[i2[0]] = ('    return sqlite3.connect(str(_cari_db()))', baris[i2[0]][1])
            ubah += 1
            print(f"{G} P4b _conn defensif")
        elif "_cari_db()" in "\n".join(isi[max(0, i1[0]):i1[0] + 3]) if i1 else "":
            print(f"{G} P4b _conn: sudah defensif, lewati")
        else:
            print(f"{W} P4b: pola _conn tidak dikenali, lewati")
    else:
        print(f"{W} P4b: lewati")

    if kering:
        print(f"{G} simulasi konsolidasi: {ubah} patch")
        return True
    if ubah == 0:
        return True
    bak = p.parent / f"{p.name}.bak_colokmemori_{datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(p, bak)
    p.write_text(gabung(baris), encoding="utf-8")
    ok, err = compile_cek(p)
    if not ok:
        shutil.copy2(bak, p)
        print(f"{R} compile konsolidasi GAGAL -> dipulihkan")
        return False
    print(f"{G} compile konsolidasi OK (backup {bak.name})")
    return True


def tes_wiring():
    """Uji wiring tanpa API: import modul patch-an, panggil helper."""
    print("=" * 60)
    print("TES WIRING MEMORI (tanpa API key)")
    print("=" * 60)
    kode = (
        "import sys; sys.path.insert(0, r'" + str(ROOT) + "');"
        "import orion_tool_loop as o;"
        "assert hasattr(o, '_recall_memori'), 'helper recall hilang';"
        "assert hasattr(o, '_simpan_memori'), 'helper simpan hilang';"
        "m = o._mem();"
        "print('memory_manager:', 'KETEMU' if m else 'TIDAK KETEMU (fail-safe aktif)');"
        "t = o._recall_memori();"
        "print('recall:', len(t), 'karakter');"
        "print('TES SELESAI')"
    )
    r = subprocess.run([sys.executable, "-c", kode], capture_output=True,
                       text=True, timeout=60, cwd=str(ROOT))
    print(r.stdout)
    if r.returncode != 0:
        print(f"{R} TES GAGAL:\n{(r.stderr or '')[:500]}")
    else:
        print(f"{G} wiring OK")


def main():
    print("=" * 60)
    print("COLOK MEMORI LOOP" + (" (SIMULASI)" if KERING else ""))
    print("Root:", ROOT)
    print("=" * 60)
    if TES:
        tes_wiring()
        return
    ok1 = patch_loop(KERING)
    ok2 = patch_konsolidasi(KERING)
    print("-" * 60)
    if KERING:
        print("Simulasi selesai, tidak ada file diubah.")
    elif ok1 and ok2:
        print("SELESAI. Uji: python colok_memori_loop.py --tes")
        print("Lalu ngobrol seperti biasa, restart, dan tanya hal tadi.")
    else:
        print(f"{R} ada yang gagal, cek di atas.")


if __name__ == "__main__":
    main()
