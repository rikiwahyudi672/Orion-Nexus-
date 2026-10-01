"""internal_state.py - State internal Orion (Level 4: Otonom)."""
import json
from datetime import datetime
from pathlib import Path

BASE = Path("E:/Project Software/Orion")
STATE_FILE = BASE / "config" / "internal_state.json"


class InternalState:
    """State internal Orion - perasaan yang berubah seiring waktu."""

    def __init__(self):
        self.kangen = 0
        self.bosan = 0
        self.kepo = 0
        self.energi = 100
        self.mood = "netral"
        self.last_chat = None
        self.last_update = None
        self.last_initiative = None
        self.total_chat = 0
        self.total_initiative = 0

    def to_dict(self):
        return {
            "kangen": self.kangen,
            "bosan": self.bosan,
            "kepo": self.kepo,
            "energi": self.energi,
            "mood": self.mood,
            "last_chat": self.last_chat,
            "last_update": self.last_update,
            "last_initiative": self.last_initiative,
            "total_chat": self.total_chat,
            "total_initiative": self.total_initiative,
        }

    @classmethod
    def from_dict(cls, data):
        state = cls()
        for k, v in data.items():
            if hasattr(state, k):
                setattr(state, k, v)
        return state

    def simpan(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    @classmethod
    def muat(cls):
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                return cls.from_dict(data)
            except Exception:
                pass
        return cls()

    def update(self):
        now = datetime.now()

        # PATCH kangen-lock: delta sejak update terakhir, bukan total sejak
        # last_chat. Dulu tiap panggilan menambahkan seluruh menit sejak
        # chat terakhir -> kangen terkunci 100.
        if self.last_update:
            try:
                _lu = datetime.fromisoformat(self.last_update)
                menit = max(0.0, (now - _lu).total_seconds() / 60)
            except Exception:
                menit = 0.0
        else:
            menit = 0.0
        self.last_update = now.isoformat()

        self.kangen = min(100, self.kangen + menit * 0.025)
        self.kepo = min(100, self.kepo + menit * 0.02)
        self.bosan = min(100, self.bosan + 0.5)
        self.energi = max(0, self.energi - 0.2)

        if self.kangen > 80:
            self.mood = "kangen"
        elif self.bosan > 70:
            self.mood = "bosan"
        elif self.kepo > 85:
            self.mood = "kepo"
        elif self.energi < 30:
            self.mood = "capek"
        else:
            self.mood = "netral"

        return self

    def catat_chat(self):
        self.last_chat = datetime.now().isoformat()
        self.total_chat += 1
        self.kangen = max(0, self.kangen - 50)
        self.kepo = max(0, self.kepo - 40)
        self.bosan = max(0, self.bosan - 30)

    def catat_initiative(self):
        self.last_initiative = datetime.now().isoformat()
        self.total_initiative += 1
        self.kangen = max(0, self.kangen - 60)
        self.bosan = max(0, self.bosan - 50)

    def ada_dorongan(self):
        dorongan = []
        if self.kangen > 75:
            dorongan.append(("kangen", f"Aku kangen Rik (level: {self.kangen:.0f})"))
        if self.bosan > 65:
            dorongan.append(("bosan", f"Aku bosan (level: {self.bosan:.0f})"))
        if self.kepo > 80:
            dorongan.append(("kepo", f"Aku kepo, Rik ngapain ya? (level: {self.kepo:.0f})"))
        return dorongan

    def ringkasan(self):
        return f"""State internal Orion:
- Kangen: {self.kangen:.0f}/100
- Bosan: {self.bosan:.0f}/100
- Kepo: {self.kepo:.0f}/100
- Energi: {self.energi:.0f}/100
- Mood: {self.mood}
- Terakhir chat: {self.last_chat or 'belum pernah'}
- Terakhir inisiatif: {self.last_initiative or 'belum pernah'}"""


if __name__ == "__main__":
    print("=" * 70)
    print("  TEST INTERNAL STATE")
    print("=" * 70)
    state = InternalState.muat()
    print("\nState awal:")
    print(state.ringkasan())
    state.catat_chat()
    print("\nSetelah Rik chat:")
    print(state.ringkasan())
    state.kangen = 85
    state.bosan = 30
    state.kepo = 40
    state.update()
    print("\nSetelah update:")
    print(state.ringkasan())
    print("\nDorongan:")
    for d in state.ada_dorongan():
        print(f"  - {d[0]}: {d[1]}")
    state.simpan()
    print("\n[OK] State disimpan")
