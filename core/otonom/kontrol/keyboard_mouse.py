"""keyboard_mouse.py - Kontrol keyboard + mouse Orion (JARVIS style)."""
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("[KeyboardMouse] pyautogui tidak ada — install: pip install pyautogui")


def ketik(teks: str, delay: float = 0.05) -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        pyautogui.write(teks, interval=delay)
        return {"sukses": True, "pesan": f"Mengetik: {teks[:50]}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def tekan(tombol: str) -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        pyautogui.press(tombol)
        return {"sukses": True, "pesan": f"Menekan: {tombol}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def hotkey(*tombol) -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        pyautogui.hotkey(*tombol)
        return {"sukses": True, "pesan": f"Hotkey: {'+'.join(tombol)}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def klik(x: int = None, y: int = None, tombol: str = "left") -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, button=tombol)
        else:
            pyautogui.click(button=tombol)
        return {"sukses": True, "pesan": f"Klik {tombol}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def scroll(jumlah: int) -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        pyautogui.scroll(jumlah)
        return {"sukses": True, "pesan": f"Scroll {jumlah}"}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def posisi_mouse() -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        x, y = pyautogui.position()
        return {"sukses": True, "x": x, "y": y}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


def ukuran_layar() -> dict:
    if not HAS_PYAUTOGUI:
        return {"sukses": False, "pesan": "pyautogui tidak ada"}
    try:
        w, h = pyautogui.size()
        return {"sukses": True, "width": w, "height": h}
    except Exception as e:
        return {"sukses": False, "pesan": f"Error: {e}"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST KEYBOARD + MOUSE")
    print("=" * 60)
    
    print(f"\npyautogui: {'OK' if HAS_PYAUTOGUI else 'X'}")
    
    if HAS_PYAUTOGUI:
        print(f"\nUkuran layar: {ukuran_layar()}")
        print(f"Posisi mouse: {posisi_mouse()}")
