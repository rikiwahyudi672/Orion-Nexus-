"""kompresi_konteks.py - Kompresi konteks kesadaran (biar tidak 413)."""
from pathlib import Path

BASE = Path("E:/Project Software/Orion")


def kompres_konteks(konteks: str, max_char: int = 4000) -> str:
    """Kompres konteks — ambil yang penting."""
    if len(konteks) <= max_char:
        return konteks
    
    # Split per baris
    lines = konteks.split("\n")

    # FIX GEMA 01/10: tembok identitas cukup 3 baris unik pertama.
    # Dulu puluhan baris "Aku Orion..." lolos dedup (beda teks dikit) lalu
    # dimuat di depan sebagai "penting" hingga memakan jatah max_char.
    import re as _re_gema
    _pola_ident = _re_gema.compile(r'aku\s+orion', _re_gema.IGNORECASE)
    _ident, _sudah_ident, _sisa = [], set(), []
    for _b in lines:
        if _pola_ident.search(_b):
            _k = _b.strip().lower()
            if _k not in _sudah_ident and len(_ident) < 3:
                _sudah_ident.add(_k)
                _ident.append(_b)
            # selebihnya dibuang — identitas cukup disebut sekali
        else:
            _sisa.append(_b)
    lines = _sisa
    
    # Prioritas: baris yang mengandung keyword penting
    PENTING = [
        "KONTEKS ORION", "STATE ORION", "MISI ORION",
        # FIX GEMA 01/10: "Aku Orion" keluar dari PENTING (identitas max 3 baris, lihat atas).
        "Rumah", "Emosi", "Tubuh",
        "Meta-", "Moral", "Spiritual",
    ]
    
    # PERINGKAS 30/09: buang baris yang identik (sisakan kemunculan pertama)
    # — mencegah tembok "KONTEKS ORION:" / "Aku Orion." berulang di prompt
    _sudah_lihat = set()
    _baris_unik = []
    for _b in lines:
        if _b not in _sudah_lihat:
            _sudah_lihat.add(_b)
            _baris_unik.append(_b)
    lines = _baris_unik
    # TAHAP2 30/09: ringkas header mirip-tapi-beda-isi (near-duplicate)
    # - kemunculan PERTAMA tiap kunci tetap di posisi aslinya (ikut front-load);
    #   kemunculan berikutnya dipindah ke belakang agar tidak membanjiri depan.
    # - tidak ada baris yang dibuang: semua tetap ada sampai batas max_char.
    import re as _re_t2
    _pola_t2 = _re_t2.compile(r'^(KONTEKS ORION|STATE ORION|MISI ORION)\s*:')
    _t2_depan, _t2_belakang, _t2_sudah = [], [], set()
    for _t2_ln in lines:
        _t2_m = _pola_t2.match(_t2_ln.strip())
        if _t2_m:
            _t2_kunci = _t2_m.group(1)
            if _t2_kunci in _t2_sudah:
                _t2_belakang.append(_t2_ln)
                continue
            _t2_sudah.add(_t2_kunci)
        _t2_depan.append(_t2_ln)
    lines = _t2_depan + _t2_belakang
    
    penting_lines = []
    biasa_lines = []
    
    for line in lines:
        if any(k in line for k in PENTING):
            penting_lines.append(line)
        else:
            biasa_lines.append(line)
    
    # Gabung — penting dulu
    # FIX GEMA 01/10: identitas (max 3 baris) sekali di depan, lalu penting, lalu biasa
    hasil = _ident + penting_lines + biasa_lines
    hasil_str = "\n".join(hasil)
    
    # Potong kalau masih lebih
    if len(hasil_str) > max_char:
        hasil_str = hasil_str[:max_char] + "\n... [dipotong]"
    
    return hasil_str


if __name__ == "__main__":
    print("=" * 60)
    print("  KOMPRESI KONTEKS")
    print("=" * 60)
    
    # Test
    konteks_panjang = "A" * 10000
    hasil = kompres_konteks(konteks_panjang, 4000)
    print(f"  Sebelum: {len(konteks_panjang)} char")
    print(f"  Sesudah: {len(hasil)} char")
