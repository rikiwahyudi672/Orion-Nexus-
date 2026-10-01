"""
thinker_orion.py - Layer "mikir" untuk ORION.
"""


def think(pesan: str) -> dict:
    """Thinker utama."""
    intent = _parse_intent(pesan)
    risiko = _analyze_risk(pesan, intent)
    langkah = _plan(pesan, intent)
    butuh_konfirmasi = risiko == "tinggi"

    return {
        "intent": intent,
        "risiko": risiko,
        "langkah": langkah,
        "butuh_konfirmasi": butuh_konfirmasi,
        "alasan": f"Intent: {intent}, Risiko: {risiko}",
    }


def _parse_intent(pesan: str) -> str:
    """Pahami maksud user."""
    p = pesan.lower()

    # CODING - CEK DULU (paling spesifik)
    if any(k in p for k in ["code", "coding", "program", "script", "fix bug", 
                            "debug", "fungsi", "class", "aplikasi", "software"]):
        return "coding"

    # EKSEKUSI - shutdown, hapus, buat folder, tulis file
    if any(k in p for k in ["shutdown", "matiin", "matikan", "restart", "reboot",
                            "hapus", "delete", "remove", "format",
                            "buat file", "bikin file", "tulis file",
                            "buat folder", "bikin folder",
                            "copy", "salin", "file", "folder"]):
        return "eksekusi"

    # Riset
    if any(k in p for k in ["cari", "search", "riset", "research", "googling", "tokoh", "fakta"]):
        return "riset"

    # Chat biasa
    return "chat"


def _analyze_risk(pesan: str, intent: str) -> str:
    """Cek risiko."""
    p = pesan.lower()

    if any(k in p for k in ["hapus semua", "format", "rm -rf", "shutdown", "delete all", "restart"]):
        return "tinggi"

    if any(k in p for k in ["hapus", "delete", "remove", "transfer", "kirim uang"]):
        return "sedang"

    return "rendah"


def _plan(pesan: str, intent: str) -> list:
    """Susun langkah."""
    if intent == "eksekusi":
        return [
            "1. Deteksi tipe eksekusi",
            "2. Cek risiko",
            "3. Eksekusi",
            "4. Lapor hasil",
        ]
    elif intent == "coding":
        return [
            "1. Pahami kebutuhan",
            "2. Cari skill coding",
            "3. Tulis kode",
            "4. Test",
        ]
    elif intent == "riset":
        return [
            "1. Pahami topik",
            "2. Cari skill riset",
            "3. Kumpulkan data",
            "4. Rangkum",
        ]
    else:
        return [
            "1. Pahami pesan",
            "2. Cari skill relevan",
            "3. Jawab",
        ]


if __name__ == "__main__":
    print("=== Test thinker_orion ===")
    test_cases = [
        "bikin folder test",
        "hapus semua file",
        "buat program kalkulator",
        "cari tokoh Soekarno",
        "halo orion",
    ]
    for tc in test_cases:
        hasil = think(tc)
        print(f"\nPesan: {tc}")
        print(f"  Intent: {hasil['intent']}")
        print(f"  Risiko: {hasil['risiko']}")
        print(f"  Konfirmasi: {hasil['butuh_konfirmasi']}")
