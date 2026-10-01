"""cek_mic.py - Cek semua mic device"""
import sounddevice as sd

print("Default input device:")
print(sd.query_devices(kind="input"))
print()
print("Semua input devices:")
default_idx = sd.default.device[0]
for i, d in enumerate(sd.query_devices()):
    if d["max_input_channels"] > 0:
        marker = " <-- DEFAULT" if i == default_idx else ""
        print(f'  [{i}] {d["name"]}')
        print(f'       Channels: {d["max_input_channels"]}, Sample Rate: {d["default_samplerate"]} Hz{marker}')