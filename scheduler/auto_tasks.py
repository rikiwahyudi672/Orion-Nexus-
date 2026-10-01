

# ============================================================
# TRAINING BERKALA
# ============================================================

def training_reflection():
    """Refleksi harian."""
    try:
        import reflection_orion
        hasil = reflection_orion.refleksi_harian()
        print("[training] Refleksi: " + str(hasil))
    except Exception as e:
        print("[training] Refleksi error: " + str(e))


def training_konsolidasi():
    """Konsolidasi 7 hari."""
    try:
        import konsolidasi_memory
        konsolidasi_memory.konsolidasi()
        konsolidasi_memory.hapus_chat_lama(30)
        print("[training] Konsolidasi selesai")
    except Exception as e:
        print("[training] Konsolidasi error: " + str(e))


def training_evolusi():
    """Evolusi 30 hari."""
    try:
        import evolusi_prompt
        evolusi_prompt.evolusi()
        print("[training] Evolusi selesai")
    except Exception as e:
        print("[training] Evolusi error: " + str(e))
