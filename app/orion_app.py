"""orion_app.py - Orion Windows App - MVP."""
import sys
import os
from pathlib import Path
from datetime import datetime

# Import TTS
try:
    import sys
    from pathlib import Path as _Path
    _BASE = _Path(__file__).parent.parent
    sys.path.insert(0, str(_BASE))
    from orion_voice import tts_speak
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ============ CEK GUI ============
print("[App] Cek GUI...")

GUI = None
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog, QMessageBox
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QIcon, QFont
    GUI = "PyQt6"
    print("[App] ✅ PyQt6")
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog, QMessageBox
        )
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QIcon, QFont
        GUI = "PyQt5"
        print("[App] ✅ PyQt5")
    except ImportError:
        print("[App] ❌ PyQt6/PyQt5 tidak ada")
        sys.exit(1)

# ============ PATH ============
BASE = Path(__file__).parent
LOGO_PATH = BASE / "assets" / "logo" / "orion.ico"
if not LOGO_PATH.exists():
    LOGO_PATH = BASE / "assets" / "logo" / "orion_logo_512.png"

# ============ ORION APP ============
# ============ SETUP PATH CLI ============
# SETUP_PATH_CLI
import sys
import os
from pathlib import Path as _Path

_BASE = _Path(__file__).parent.parent
os.chdir(str(_BASE))

if str(_BASE) not in sys.path:
    sys.path.insert(0, str(_BASE))
if str(_BASE / "py") not in sys.path:
    sys.path.insert(0, str(_BASE / "py"))

# ============ IMPORT SISTEM CLI ============
try:
    from otak_orion import diskusi_orion, diskusi
    OTAK_AVAILABLE = True
except ImportError as e:
    print(f"[App] Otak error: {e}")
    OTAK_AVAILABLE = False

try:
    from orion_hub import proses, lapor_diri
    HUB_AVAILABLE = True
except ImportError as e:
    print(f"[App] Hub error: {e}")
    HUB_AVAILABLE = False


class OrionApp(QMainWindow):
    """Orion Windows App."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.setWindowTitle("Orion - Digital Lieutenant")
        self.setGeometry(100, 100, 900, 700)
        
        # Icon
        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0A1428;
            }
            QLabel {
                color: #00B4FF;
                font-family: 'Segoe UI';
            }
            QLabel#Title {
                font-size: 24px;
                font-weight: bold;
                color: #00B4FF;
            }
            QLabel#Status {
                font-size: 12px;
                color: #00FFC8;
            }
            QTextEdit {
                background-color: #102040;
                color: #E0E0E0;
                border: 1px solid #00B4FF;
                border-radius: 8px;
                font-family: 'Consolas';
                font-size: 12px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #102040;
                color: #FFFFFF;
                border: 1px solid #00B4FF;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QPushButton {
                background-color: #00B4FF;
                color: #0A1428;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00FFC8;
            }
            QPushButton:pressed {
                background-color: #0088CC;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # === HEADER ===
        header = QHBoxLayout()
        
        # Logo
        if LOGO_PATH.exists():
            logo_label = QLabel()
            pixmap = QIcon(str(LOGO_PATH)).pixmap(48, 48)
            logo_label.setPixmap(pixmap)
            header.addWidget(logo_label)
        
        # Title
        title = QLabel("ORION")
        title.setObjectName("Title")
        header.addWidget(title)
        
        header.addStretch()
        
        # Status
        self.status_label = QLabel("● Online")
        self.status_label.setObjectName("Status")
        header.addWidget(self.status_label)
        
        layout.addLayout(header)
        
        # === CHAT AREA ===
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText("Chat dengan Orion...")
        layout.addWidget(self.chat_area)
        
        # === INPUT AREA ===
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ketik pesan...")
        self.input_field.returnPressed.connect(self.kirim_pesan)
        input_layout.addWidget(self.input_field)
        
        self.btn_kirim = QPushButton("Kirim")
        self.btn_kirim.clicked.connect(self.kirim_pesan)
        input_layout.addWidget(self.btn_kirim)
        
        layout.addLayout(input_layout)
        
        # === BUTTON AREA ===
        btn_layout = QHBoxLayout()
        
        self.btn_voice = QPushButton("🎤 Voice")
        self.btn_voice.clicked.connect(self.toggle_voice)
        btn_layout.addWidget(self.btn_voice)
        
        self.btn_file = QPushButton("📁 File")
        self.btn_file.clicked.connect(self.kirim_file)
        btn_layout.addWidget(self.btn_file)
        
        self.btn_status = QPushButton("📊 Status")
        self.btn_status.clicked.connect(self.cek_status)
        btn_layout.addWidget(self.btn_status)
        
        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.clicked.connect(self.clear_chat)
        btn_layout.addWidget(self.btn_clear)
        
        layout.addLayout(btn_layout)
        
        # === WELCOME ===
        self.tambah_chat("Orion", "Halo Rik! Gue Orion. Ada yang bisa gue bantu?")
        
        # Timer untuk cek status
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # 5 detik
    
    def tambah_chat(self, pengirim, pesan):
        """Tambah chat ke area."""
        waktu = datetime.now().strftime("%H:%M")
        
        if pengirim == "Orion":
            warna = "#00FFC8"
            nama = "🤖 Orion"
        else:
            warna = "#00B4FF"
            nama = "👤 Riki"
        
        html = f'<div style="margin-bottom: 10px;">'
        html += f'<span style="color: {warna}; font-weight: bold;">{nama}</span>'
        html += f'<span style="color: #666; font-size: 10px;"> [{waktu}]</span><br>'
        html += f'<span style="color: #E0E0E0;">{pesan}</span>'
        html += f'</div>'
        
        self.chat_area.insertHtml(html)
        self.chat_area.insertPlainText("\n")
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
    
    def kirim_pesan(self):
        """Kirim pesan ke Orion."""
        pesan = self.input_field.text().strip()
        if not pesan:
            return
        
        self.input_field.clear()
        self.tambah_chat("Riki", pesan)
        
        # Proses di Orion
        try:
            # Set DB path ke root
            os.chdir(str(BASE))
            sys.path.insert(0, str(BASE / "py"))
            sys.path.insert(0, str(BASE))
            
            from otak_orion import diskusi_orion
            
            # PAKAI SISTEM CLI
            if OTAK_AVAILABLE:
                jawab = diskusi_orion(pesan)
            else:
                jawab = "Otak tidak tersedia"
            
            self.tambah_chat("Orion", jawab)
            
            # TTS - suara Ardi
            if TTS_AVAILABLE:
                try:
                    tts_speak(jawab, play=True, mode="edge")
                except Exception:
                    pass
        except Exception as e:
            self.tambah_chat("Orion", f"Error: {e}")
    
    def toggle_voice(self):
        """Toggle voice mode - dengan Whisper STT."""
        if getattr(self, '_voice_aktif', False):
            self._voice_aktif = False
            self.btn_voice.setText("🎤 Voice")
            self.tambah_chat("Orion", "Voice mode OFF")
            return
        
        self._voice_aktif = True
        self.btn_voice.setText("🔴 Stop")
        
        import threading
        thread = threading.Thread(target=self._voice_loop, daemon=True)
        thread.start()
    
    def _voice_loop(self):
        """Loop voice - dengar, proses, jawab."""
        try:
            self.tambah_chat("Orion", "🎤 Mendengarkan... (5 detik)")
            
            # Whisper STT
            import whisper
            import sounddevice as sd
            import tempfile
            import os
            from scipy.io.wavfile import write
            
            model = whisper.load_model("small")
            
            duration = 5
            samplerate = 16000
            
            recording = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            temp_file = tempfile.mktemp(suffix=".wav")
            write(temp_file, samplerate, recording)
            
            result = model.transcribe(temp_file, language="id")
            teks_user = result.get("text", "").strip()
            os.remove(temp_file)
            
            if not teks_user:
                self.tambah_chat("Orion", "Tidak ada suara terdeteksi")
                return
            
            self.tambah_chat("Riki", teks_user)
            
            # Proses di Orion
            import sys
            from pathlib import Path as _Path
            _BASE = _Path(__file__).parent.parent
            sys.path.insert(0, str(_BASE))
            sys.path.insert(0, str(_BASE / "py"))
            
            from otak_orion import diskusi_orion
            jawab = diskusi_orion(teks_user)
            self.tambah_chat("Orion", jawab)
            
            # TTS - suara Ardi
            try:
                sys.path.insert(0, str(_BASE))
                from orion_voice import tts_speak
                tts_speak(jawab, play=True, mode="edge")
            except Exception as e:
                print(f"[Voice] TTS error: {e}")
        
        except Exception as e:
            self.tambah_chat("Orion", f"Voice error: {e}")
        finally:
            self._voice_aktif = False
            self.btn_voice.setText("🎤 Voice")
    
    def kirim_file(self):
        """Kirim file ke Orion."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File", "", "All Files (*.*)"
        )
        
        if file_path:
            self.tambah_chat("Riki", f"[File: {Path(file_path).name}]")
            
            try:
                path = Path(file_path)
                if path.suffix in [".txt", ".md", ".py", ".json"]:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    self.tambah_chat("Orion", f"File dibaca:\n{content[:500]}")
                else:
                    self.tambah_chat("Orion", f"File: {path.name} ({path.stat().st_size} B)")
            except Exception as e:
                self.tambah_chat("Orion", f"Error: {e}")
    
    def cek_status(self):
        """Cek status Orion."""
        try:
            sys.path.insert(0, str(BASE / "py"))
            from orion_hub import lapor_diri
            lapor_diri()
            self.tambah_chat("Orion", "Status: OK - cek terminal")
        except Exception as e:
            self.tambah_chat("Orion", f"Error: {e}")
    
    def clear_chat(self):
        """Clear chat."""
        self.chat_area.clear()
        self.tambah_chat("Orion", "Chat di-clear.")
    
    def update_status(self):
        """Update status label."""
        try:
            from datetime import datetime
            waktu = datetime.now().strftime("%H:%M:%S")
            self.status_label.setText(f"● Online [{waktu}]")
        except Exception:
            pass


# ============ MAIN ============
if __name__ == "__main__":
    print(f"[App] GUI: {GUI}")
    print(f"[App] Logo: {LOGO_PATH}")
    print("[App] Jalanin...")
    
    app = QApplication(sys.argv)
    window = OrionApp()
    window.show()
    
    sys.exit(app.exec())
