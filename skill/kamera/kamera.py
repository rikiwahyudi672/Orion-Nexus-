"""kamera.py - Skill kamera Orion (Haarcascade)."""
import time
from pathlib import Path
from datetime import datetime

BASE = Path("E:/Project Software/Orion")
OUTPUT_DIR = BASE / "output" / "kamera"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HAAR_CASCADE = BASE / "models" / "haarcascade_frontalface_default.xml"
FACE_MODEL = BASE / "models" / "face_model.yml"


def info():
    """Info kamera."""
    try:
        import cv2
        
        cameras = []
        for i in range(1):  # Cuma kamera 0
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cameras.append({"index": i, "width": width, "height": height})
                cap.release()
        
        return {"sukses": True, "total_kamera": len(cameras), "kamera": cameras}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def lihat(durasi=3, kamera_index=0):
    """Lihat kamera - ringkasan cepat."""
    try:
        import cv2
        import numpy as np
        
        if not HAAR_CASCADE.exists():
            return {"sukses": False, "error": "Model haarcascade tidak ada"}
        
        face_cascade = cv2.CascadeClassifier(str(HAAR_CASCADE))
        
        cap = cv2.VideoCapture(kamera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if not cap.isOpened():
            return {"sukses": False, "error": "Kamera tidak bisa dibuka"}
        
        frames = []
        start = time.time()
        
        while time.time() - start < durasi:
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            time.sleep(0.1)
        
        cap.release()
        
        if not frames:
            return {"sukses": False, "error": "Tidak ada frame"}
        
        # Analisa frame terakhir
        last = frames[-1]
        avg = np.mean(last, axis=(0, 1))
        brightness = np.mean(avg)
        
        # Deteksi wajah
        gray = cv2.cvtColor(last, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return {
            "sukses": True,
            "durasi": durasi,
            "kecerahan": round(float(brightness), 1),
            "wajah": len(faces),
            "pesan": f"Lihat {durasi}s - {len(faces)} wajah, kecerahan {brightness:.0f}",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def deteksi_wajah(durasi=5, kamera_index=0):
    """Deteksi wajah realtime - 10 FPS."""
    try:
        import cv2
        
        if not HAAR_CASCADE.exists():
            return {"sukses": False, "error": "Model haarcascade tidak ada"}
        
        face_cascade = cv2.CascadeClassifier(str(HAAR_CASCADE))
        
        cap = cv2.VideoCapture(kamera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if not cap.isOpened():
            return {"sukses": False, "error": "Kamera tidak bisa dibuka"}
        
        start = time.time()
        frames = 0
        max_wajah = 0
        total_wajah = 0
        detail_terakhir = []
        
        while time.time() - start < durasi:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            frames += 1
            
            if len(faces) > 0:
                max_wajah = max(max_wajah, len(faces))
                total_wajah += len(faces)
                detail_terakhir = [
                    {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    for (x, y, w, h) in faces
                ]
        
        cap.release()
        
        return {
            "sukses": True,
            "durasi": durasi,
            "fps": round(frames / durasi, 1),
            "frames": frames,
            "max_wajah_sekaligus": max_wajah,
            "total_deteksi": total_wajah,
            "detail_terakhir": detail_terakhir,
            "pesan": f"Lihat {durasi}s - {frames/durasi:.1f} FPS, max {max_wajah} wajah",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def foto(output=None, kamera_index=0):
    """Ambil foto."""
    try:
        import cv2
        
        if not output:
            nama = f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            output = OUTPUT_DIR / nama
        
        cap = cv2.VideoCapture(kamera_index)
        if not cap.isOpened():
            return {"sukses": False, "error": "Kamera tidak bisa dibuka"}
        
        time.sleep(0.5)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {"sukses": False, "error": "Gagal ambil foto"}
        
        cv2.imwrite(str(output), frame)
        
        return {
            "sukses": True,
            "output": str(output),
            "size": Path(output).stat().st_size,
            "pesan": f"Foto disimpan: {Path(output).name}",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def kenali_wajah(durasi=5, kamera_index=0):
    """Kenali wajah pakai model LBPH."""
    try:
        import cv2
        
        if not HAAR_CASCADE.exists() or not FACE_MODEL.exists():
            return {"sukses": False, "error": "Model tidak lengkap"}
        
        face_cascade = cv2.CascadeClassifier(str(HAAR_CASCADE))
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(FACE_MODEL))
        
        cap = cv2.VideoCapture(kamera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if not cap.isOpened():
            return {"sukses": False, "error": "Kamera tidak bisa dibuka"}
        
        start = time.time()
        frames = 0
        results = []
        
        while time.time() - start < durasi:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            frames += 1
            
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                label, confidence = recognizer.predict(roi_gray)
                results.append({
                    "label": int(label),
                    "confidence": round(float(confidence), 1),
                    "nama": f"Orang #{label}" if confidence >= 50 else f"Riki (conf: {confidence:.0f})",
                })
        
        cap.release()
        
        return {
            "sukses": True,
            "durasi": durasi,
            "fps": round(frames / durasi, 1),
            "wajah": results[-5:],
            "pesan": f"Kenali {durasi}s - {len(results)} deteksi",
        }
    except Exception as e:
        return {"sukses": False, "error": str(e)}


# === Fungsi utama untuk tool loop ===
def jalankan(aksi="info", durasi=5, kamera_index=0, output=""):
    """
    Jalankan aksi kamera.
    
    Args:
        aksi: "info" / "lihat" / "deteksi_wajah" / "foto" / "kenali_wajah"
        durasi: berapa detik
        kamera_index: index kamera
        output: path output (untuk foto)
    """
    if aksi == "info":
        return info()
    elif aksi == "lihat":
        return lihat(durasi, kamera_index)
    elif aksi == "deteksi_wajah":
        return deteksi_wajah(durasi, kamera_index)
    elif aksi == "foto":
        return foto(output or None, kamera_index)
    elif aksi == "kenali_wajah":
        return kenali_wajah(durasi, kamera_index)
    else:
        return {
            "sukses": False,
            "error": f"Aksi tidak dikenal: {aksi}",
            "aksi_tersedia": ["info", "lihat", "deteksi_wajah", "foto", "kenali_wajah"],
        }


if __name__ == "__main__":
    print("=== Test kamera Orion ===")
    
    print("\n[1] Info:")
    print(f"  {info()}")
    
    print("\n[2] Lihat 3s:")
    print(f"  {lihat(3)}")
    
    print("\n[3] Deteksi wajah 5s:")
    print(f"  {deteksi_wajah(5)}")
