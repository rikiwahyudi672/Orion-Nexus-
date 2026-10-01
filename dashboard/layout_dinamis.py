import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""layout_dinamis.py - Layout terminal dinamis (v2)

Gabungan dari:
- orion_v8_core.py  (warna, box drawing, lebar visual)
- orion_v8_render.py (banner, panel, render dashboard)
- layout_dinamis.py lama (center, layout 2 kolom)

Semua fungsi lama tetap ada untuk backward compatibility.
"""
import os
import re
import shutil
import unicodedata
from datetime import datetime


# ============================================================
# BAGIAN 1: WARNA (TRUE COLOR)
# ============================================================
ANSI_RE = re.compile(r"\033\[[0-9;]*m")


class C:
    R = "\033[0m"
    B = "\033[1m"
    DIM = "\033[2m"
    # Gradient cyan -> purple
    G1 = "\033[38;2;100;181;246m"
    G2 = "\033[38;2;125;170;240m"
    G3 = "\033[38;2;150;160;235m"
    G4 = "\033[38;2;175;145;225m"
    G5 = "\033[38;2;195;135;215m"
    G6 = "\033[38;2;149;117;205m"
    # Semantic
    GREEN = "\033[38;2;102;187;106m"
    YELLOW = "\033[38;2;255;213;79m"
    RED = "\033[38;2;239;83;80m"
    GRAY = "\033[38;2;144;164;174m"
    WHITE = "\033[38;2;224;230;255m"
    PURPLE = "\033[38;2;149;117;205m"
    # Highlight
    HI = "\033[48;2;30;60;110m\033[38;2;255;255;255m"


def c(t, col):
    """Bungkus teks dengan warna."""
    return f"{col}{t}{C.R}"


# ============================================================
# BAGIAN 2: TERMINAL
# ============================================================
def clear():
    """Bersihkan layar."""
    os.system("cls" if os.name == "nt" else "clear")


def terminal_size():
    """Deteksi ukuran terminal REAL-TIME. Return (kolom, baris)."""
    try:
        s = shutil.get_terminal_size()
        return s.columns, s.lines
    except Exception:
        return 100, 30


# ============================================================
# BAGIAN 3: LEBAR VISUAL
# ============================================================
def lebar_visual(teks):
    """Lebar visual: ANSI=0, emoji/CJK=2, biasa=1."""
    teks_bersih = ANSI_RE.sub("", teks)
    w = 0
    for ch in teks_bersih:
        if ch == "\ufe0f":
            continue
        ea = unicodedata.east_asian_width(ch)
        if ea in ("W", "F"):
            w += 2
        else:
            w += 1
    return w


def pad(teks, lebar):
    """Pad teks ke lebar tertentu (presisi, emoji-aware)."""
    w = lebar_visual(teks)
    return teks + " " * max(0, lebar - w)


def center(teks, lebar):
    """Center teks (presisi, emoji-aware)."""
    w = lebar_visual(teks)
    kiri = max(0, (lebar - w) // 2)
    kanan = max(0, lebar - w - kiri)
    return " " * kiri + teks + " " * kanan


# ============================================================
# BAGIAN 4: BOX DRAWING
# ============================================================
def box_top(judul, lebar, color=None, icon=""):
    """Buat garis atas box:  judul """
    color = color or C.G1
    w_j = lebar_visual(judul)
    sisa = max(0, lebar - w_j - 4)
    return c(" ", color) + judul + c(" " + "" * sisa + "", color)


def box_mid(teks, lebar, color=None, highlight=False):
    """Buat baris isi box:  teks ..... """
    color = color or C.G1
    w = lebar_visual(teks)
    sisa = max(0, lebar - w - 2)
    if highlight:
        return c(" ", color) + c(teks + " " * sisa, C.HI) + c(" ", color)
    return c(" ", color) + teks + " " * sisa + c(" ", color)


def box_empty(lebar, color=None):
    """Baris kosong dalam box:           """
    color = color or C.G1
    return c("" + " " * lebar + "", color)


def box_bottom(lebar, color=None):
    """Garis bawah box: """
    color = color or C.G1
    return c("" + "" * lebar + "", color)


def bar(persen, lebar=8, color=None):
    """Progress bar: """
    color = color or C.G1
    isi = min(lebar, max(0, int(persen / 100 * lebar)))
    return c("" * isi, color) + c("" * (lebar - isi), C.GRAY)


# ============================================================
# BAGIAN 5: BANNER
# ============================================================
def banner(L):
    """Banner ORION dengan gradient."""
    print()
    print("  " + c("" + "" * (L - 2) + "", C.G1))
    print("  " + c("" + " " * (L - 2) + "", C.G1))

    logo = [
        "            ",
        "      ",
        "           ",
        "          ",
        "       ",
        "            ",
    ]
    colors = [C.G1, C.G2, C.G3, C.G4, C.G5, C.G6]

    for i, line in enumerate(logo):
        w = lebar_visual(line)
        kiri = max(0, (L - 2 - w) // 2)
        kanan = max(0, L - 2 - w - kiri)
        print("  " + c("", C.G1) + " " * kiri + c(line, colors[i]) + " " * kanan + c("", C.G1))

    print("  " + c("" + " " * (L - 2) + "", C.G1))
    sub = "Personal AI Assistant v8.0"
    print("  " + c("", C.G1) + center(c(sub, C.WHITE + C.B), L - 2) + c("", C.G1))
    print("  " + c("" + " " * (L - 2) + "", C.G1))
    print("  " + c("" + "" * (L - 2) + "", C.G1))
    print()


# ============================================================
# BAGIAN 6: DATA PROVIDER (internal)
# ============================================================
_uptime_start = None


def _init_uptime():
    global _uptime_start
    if _uptime_start is None:
        import time
        _uptime_start = time.time()


def data_status():
    """Status bot."""
    _init_uptime()
    import time
    h = int((time.time() - _uptime_start) // 3600)
    m = int(((time.time() - _uptime_start) % 3600) // 60)
    return {"bot": "ONLINE", "python": "jalan", "uptime": f"{h}h {m}m"}


def data_system():
    """Info sistem (CPU/RAM/disk)."""
    try:
        import psutil
        return {
            "cpu": int(psutil.cpu_percent(interval=0.1)),
            "ram": int(psutil.virtual_memory().percent),
            "disk": int(psutil.disk_usage("C:\\").percent),
        }
    except Exception:
        return {"cpu": 0, "ram": 0, "disk": 0}


def data_otak():
    """Status otak (model ML)."""
    try:
        import core
        from pathlib import Path
        m = Path(core.P["model"])
        if m.exists():
            return {
                "status": "AKTIF",
                "data": f"{len(core.DATA_HABIT)} titik",
                "model": f"{m.stat().st_size} B",
            }
    except Exception:
        pass
    return {"status": "BELUM", "data": "-", "model": "-"}


def data_log(limit=4):
    """Log aksi terakhir."""
    try:
        import core
        rows = core.db_exec(
            "SELECT aksi, waktu FROM log_aksi ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [f"{w[11:16]}  {a[:50]}" for a, w in rows]
    except Exception:
        return []


def data_jam():
    return datetime.now().strftime("%H:%M:%S")


def data_tanggal():
    return datetime.now().strftime("%a, %d %b %Y")


# ============================================================
# BAGIAN 7: PANEL
# ============================================================
def panel_status(L):
    s = data_status()
    return [
        box_top("STATUS", L),
        box_mid(f"Bot    : {c(s['bot'], C.GREEN)}", L),
        box_mid(f"Python : {s['python']}", L),
        box_mid(f"Uptime : {s['uptime']}", L),
        box_bottom(L),
    ]


def panel_system(L):
    s = data_system()
    return [
        box_top("SYSTEM", L),
        box_mid(f"CPU   {bar(s['cpu'])} {s['cpu']:>3}%", L),
        box_mid(f"RAM   {bar(s['ram'])} {s['ram']:>3}%", L),
        box_mid(f"Disk  {bar(s['disk'])} {s['disk']:>3}%", L),
        box_bottom(L),
    ]


def panel_otak(L):
    o = data_otak()
    return [
        box_top("OTAK", L),
        box_mid(f"Status : {c(o['status'], C.GREEN)}", L),
        box_mid(f"Data   : {o['data']}", L),
        box_mid(f"Model  : {o.get('model', '-')}", L),
        box_bottom(L),
    ]


def panel_waktu(L):
    """Panel waktu (FIX: fungsi yang hilang di v8_render)."""
    return [
        box_top("WAKTU", L),
        box_mid(f"Jam     : {c(data_jam(), C.G4)}", L),
        box_mid(f"Tanggal : {data_tanggal()}", L),
        box_mid(f"Zona    : WIB", L),
        box_bottom(L),
    ]


def panel_full(judul, isi, L):
    """Panel full-width."""
    out = [box_top(judul, L)]
    for t in isi:
        out.append(box_mid(t, L))
    out.append(box_bottom(L))
    return out


# ============================================================
# BAGIAN 8: RENDER
# ============================================================
def render_dua_kolom(kiri, kanan, L_kol, gap):
    """Render 2 kolom presisi (emoji-aware)."""
    out = []
    max_len = max(len(kiri), len(kanan))
    for i in range(max_len):
        k = kiri[i] if i < len(kiri) else " " * (L_kol + 4)
        r = kanan[i] if i < len(kanan) else ""
        w_k = lebar_visual(k)
        pad_k = max(0, L_kol + 4 - w_k)
        out.append("  " + k + " " * pad_k + " " * gap + r)
    return "\n".join(out)


def render():
    """Render dashboard dynamic."""
    total_kolom, _ = terminal_size()
    margin = 6
    L_total = total_kolom - margin
    gap = 4
    L_kol = (L_total - gap) // 2

    print()
    banner(L_total)

    # Baris 1: STATUS | SYSTEM
    print(render_dua_kolom(panel_status(L_kol), panel_system(L_kol), L_kol, gap))
    print()

    # Baris 2: OTAK | WAKTU
    print(render_dua_kolom(panel_otak(L_kol), panel_waktu(L_kol), L_kol, gap))
    print()

    # Baris 3: AKTIVITAS
    for line in panel_full("AKTIVITAS", data_log() or ["(kosong)"], L_total):
        print("  " + line)
    print()

    # Baris 4: KONTROL
    for line in panel_full("KONTROL", [
        "[C] Chat  [P] Prediksi  [V] Voice  [I] Ingat  [R] Refresh  [Q] Keluar"
    ], L_total):
        print("  " + line)
    print()


# ============================================================
# BAGIAN 9: BACKWARD COMPAT (dari layout_dinamis lama)
# ============================================================
def ukuran_terminal():
    """Alias lama untuk terminal_size()."""
    return terminal_size()


def bersihkan():
    """Alias lama untuk clear()."""
    return clear()


def center_teks(teks, lebar=None):
    """Center teks (FIX: pakai lebar_visual, bukan len())."""
    if lebar is None:
        lebar, _ = terminal_size()
    return center(teks, lebar)


def center_baris(baris_list, lebar=None):
    """Center list baris."""
    if lebar is None:
        lebar, _ = terminal_size()
    return [center_teks(b, lebar) for b in baris_list]


def layout_2kolom(kiri_judul, kiri_items, kanan_judul, kanan_items, lebar=None):
    """Layout 2 kolom (FIX: pakai lebar_visual)."""
    if lebar is None:
        lebar, _ = terminal_size()

    kolom_w = min(35, (lebar - 10) // 2)

    # Header (pakai lebar_visual untuk presisi)
    w_ki = lebar_visual(kiri_judul)
    w_ka = lebar_visual(kanan_judul)
    kiri_h = " " + kiri_judul + " " + "" * max(0, kolom_w - w_ki - 6) + ""
    kanan_h = " " + kanan_judul + " " + "" * max(0, kolom_w - w_ka - 6) + ""

    # Body
    max_rows = max(len(kiri_items), len(kanan_items))
    body = []
    for i in range(max_rows):
        kiri = kiri_items[i] if i < len(kiri_items) else ""
        kanan = kanan_items[i] if i < len(kanan_items) else ""
        w_k = lebar_visual(kiri)
        w_r = lebar_visual(kanan)
        kiri_pad = kiri + " " * max(0, kolom_w - w_k - 2)
        kanan_pad = kanan + " " * max(0, kolom_w - w_r - 2)
        body.append(f"  {kiri_pad}      {kanan_pad} ")

    # Footer
    footer = "" + "" * (kolom_w + 2) + "   " + "" * (kolom_w + 2) + ""

    lines = [f"{kiri_h}   {kanan_h}"]
    lines += body
    lines.append(footer)

    return center_baris(lines, lebar)

# ============================================================
# BAGIAN 10: DASHBOARD MINIMALIS + BANNER BESAR (v3)
# ============================================================


# ============================================================
# BAGIAN 10: BANNER BESAR + DASHBOARD MINIMALIS (v3)
# ============================================================
def banner_besar():
    """Banner ORION besar dengan logo ASCII + bintang + garis."""
    L, _ = terminal_size()
    print()

    # Baris bintang atas
    print(" " * 40 + c("\u2726", C.G1) + "         " + c("\u2726", C.G1))
    print(" " * 38 + c("\u2726", C.G2) + "         " + c("\u2b50", C.YELLOW) + "         " + c("\u2726", C.G2))
    print(" " * 48 + c("\u2726", C.G3) + "         " + c("\u2726", C.G3))
    print()

    # Logo ASCII ORION
    logo = [
        "\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2557   \u2588\u2588\u2557",
        "\u2588\u2588\u2554\u2550\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2551",
        "\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2588\u2588\u2557 \u2588\u2588\u2551",
        "\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2557\u2588\u2588\u2551",
        "\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2588\u2551",
        " \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u255d  \u255a\u2550\u2550\u2550\u255d",
    ]
    colors = [C.G1, C.G2, C.G3, C.G4, C.G5, C.G6]

    for i, line in enumerate(logo):
        w = lebar_visual(line)
        kiri = max(0, (L - w) // 2)
        print(" " * kiri + c(line, colors[i]))

    print()
    print(" " * 40 + c("\u2726", C.G4) + "         " + c("\u2726", C.G4))
    print(" " * 38 + c("\u2726", C.G5) + "         " + c("\u2b50", C.YELLOW) + "         " + c("\u2726", C.G5))
    print(" " * 48 + c("\u2726", C.G6) + "         " + c("\u2726", C.G6))
    print()

    # Garis + info
    L_garis = min(L - 4, 70)
    print(" " * max(0, (L - L_garis) // 2) + c("\u2550" * L_garis, C.G1))

    judul = "\U0001f916  Personal AI Assistant  v2.7  ORION Unified"
    sub = "\U0001f464  Orion Ai"
    print(" " * max(0, (L - lebar_visual(judul)) // 2) + c(judul, C.WHITE + C.B))
    print(" " * max(0, (L - lebar_visual(sub)) // 2) + c(sub, C.GRAY))

    print(" " * max(0, (L - L_garis) // 2) + c("\u2550" * L_garis, C.G1))
    print()


def render_simple():
    """Dashboard minimalis: banner besar + status + prompt (tanpa menu)."""
    clear()
    banner_besar()

    s = data_status()
    sys = data_system()

    print(f"  {c('Status', C.GRAY)}  : {c('\U0001f49a ' + s['bot'], C.GREEN)}")
    print(f"  {c('Jam', C.GRAY)}     : {c(data_jam(), C.G4)}")
    print(f"  {c('Tanggal', C.GRAY)} : {data_tanggal()}")
    print(f"  {c('CPU', C.GRAY)}     : {sys['cpu']}%    "
          f"{c('RAM', C.GRAY)}: {sys['ram']}%    "
          f"{c('Disk', C.GRAY)}: {sys['disk']}%")
    print()

    L, _ = terminal_size()
    L_garis = min(L - 4, 70)
    print("  " + " " * max(0, (L - L_garis) // 2) + c("\u2500" * L_garis, C.DIM + C.GRAY))
    print(f"  {c('Ketik', C.GRAY)} {c('help', C.G1)} {c('untuk menu,', C.GRAY)} "
          f"{c('q', C.RED)} {c('untuk keluar', C.GRAY)}")
    print()
    print(c("  \u2b50 Orion > ", C.G1 + C.B), end="")
