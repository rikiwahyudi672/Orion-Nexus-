# ===PATCH===
# TYPE: replace_class
# TARGET: core.py
# CLASS: Otak
# DESC: Otak v2 - tambah Top-N, per-hari, auto-retrain
# ===END===

class Otak:
    """Otak ORION v2 - 48 titik, multi-fitur, Top-N, per-hari, auto-retrain."""

    def __init__(self):
        import torch
        import math
        torch.set_num_threads(CFG["model"].get("threads", 2))
        self.torch = torch
        self.math = math
        self.cfg = CFG["model"]
        self.aktivitas = self.cfg["aktivitas"]
        self.model = None
        self.path = Path(P["model"])
        self._init_db_pengalaman()

    def _init_db_pengalaman(self):
        """Bikin tabel pengalaman kalau belum ada."""
        try:
            con = sqlite3.connect(P["db"])
            con.execute("""CREATE TABLE IF NOT EXISTS pengalaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jam REAL,
                aktivitas TEXT,
                hari TEXT,
                tanggal TEXT,
                sumber TEXT DEFAULT 'user'
            )""")
            con.commit()
            con.close()
        except Exception as e:
            log.warning(f"Init db pengalaman gagal: {e}")

    def _fitur(self, jam):
        rad = 2 * self.math.pi * jam / 24
        return [self.math.sin(rad), self.math.cos(rad)]

    def _buat(self):
        nn = self.torch.nn
        layers = []
        prev = 2
        for h in [32, 16, 8]:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(0.1)]
            prev = h
        layers += [nn.Linear(prev, self.cfg["output"])]
        return nn.Sequential(*layers)

    def _data_gabung(self):
        """Gabungin DATA_HABIT + pengalaman user."""
        data = list(DATA_HABIT)
        try:
            con = sqlite3.connect(P["db"])
            rows = con.execute("SELECT jam, aktivitas FROM pengalaman").fetchall()
            con.close()
            for jam, akt in rows:
                if akt in self.aktivitas:
                    data.append((jam, akt))
                    data.append((jam, akt))  # reinforce 2x
        except Exception as e:
            log.warning(f"Ambil pengalaman gagal: {e}")
        return data

    def latih(self, verbose=True):
        t = self.torch
        if verbose:
            print("[Otak] Training v2...")

        data = self._data_gabung()

        X = t.tensor([self._fitur(d[0]) for d in data], dtype=t.float32)
        y = t.tensor([self.aktivitas.index(d[1]) for d in data], dtype=t.long)

        self.model = self._buat()

        from collections import Counter
        counter = Counter([d[1] for d in data])
        total = len(data)
        weights = [total / (len(self.aktivitas) * counter[a]) for a in self.aktivitas]
        class_weights = t.tensor(weights, dtype=t.float32)

        opt = t.optim.Adam(self.model.parameters(), lr=0.01, weight_decay=1e-4)
        loss_fn = t.nn.CrossEntropyLoss(weight=class_weights)

        epoch = 2000
        for ep in range(epoch):
            opt.zero_grad()
            out = self.model(X)
            loss = loss_fn(out, y)
            loss.backward()
            opt.step()
            if verbose and ep % 400 == 0:
                print(f"  epoch {ep:4d} | loss={loss.item():.4f}")

        t.save(self.model.state_dict(), self.path)
        if verbose:
            print(f"[Otak] OK - Disimpan: {self.path}")
            print(f"[Otak] Data: {len(DATA_HABIT)} habit + {len(data)-len(DATA_HABIT)} pengalaman")
        catat("Training otak v2")

    def load(self):
        t = self.torch
        if self.path.exists():
            self.model = self._buat()
            self.model.load_state_dict(t.load(self.path))
            self.model.eval()
            return True
        return False

    def prediksi(self, jam):
        """Prediksi aktivitas + confidence."""
        t = self.torch
        if self.model is None and not self.load():
            return None, 0
        with t.no_grad():
            fitur = t.tensor([self._fitur(jam)], dtype=t.float32)
            logits = self.model(fitur)
            probs = t.nn.functional.softmax(logits, dim=1)
            conf, idx = t.max(probs, dim=1)
            return self.aktivitas[idx.item()], conf.item()

    def prediksi_top_n(self, jam, n=3):
        """Top-N prediksi (default 3)."""
        t = self.torch
        if self.model is None and not self.load():
            return []
        with t.no_grad():
            fitur = t.tensor([self._fitur(jam)], dtype=t.float32)
            logits = self.model(fitur)
            probs = t.nn.functional.softmax(logits, dim=1)[0]
            top_probs, top_idx = t.topk(probs, min(n, len(self.aktivitas)))
            hasil = []
            for i in range(len(top_idx)):
                hasil.append((self.aktivitas[top_idx[i].item()], top_probs[i].item()))
            return hasil

    def prediksi_per_hari(self, jam, hari):
        """Prediksi dengan konteks hari (Senin-Minggu).
        Hari cuma dipakai buat pattern matching sederhana.
        Kalau ada pengalaman di hari itu, priority ke pengalaman."""
        # Cek pengalaman di hari itu
        try:
            con = sqlite3.connect(P["db"])
            rows = con.execute(
                "SELECT aktivitas, COUNT(*) FROM pengalaman WHERE hari = ? AND CAST(jam AS INT) = ? GROUP BY aktivitas ORDER BY COUNT(*) DESC LIMIT 1",
                (hari, int(jam))
            ).fetchall()
            con.close()
            if rows:
                akt, count = rows[0]
                if count >= 2:  # minimal 2x baru dianggap pattern
                    return akt, min(0.95, 0.7 + count * 0.05)
        except Exception as e:
            log.warning(f"Prediksi per hari gagal: {e}")

        # Fallback: prediksi biasa
        return self.prediksi(jam)

    def simpan_pengalaman(self, jam, aktivitas, hari=None, sumber="user"):
        """Simpan pengalaman user ke database."""
        if aktivitas not in self.aktivitas:
            return False, f"Aktivitas '{aktivitas}' tidak dikenal"
        try:
            con = sqlite3.connect(P["db"])
            con.execute(
                "INSERT INTO pengalaman (jam, aktivitas, hari, tanggal, sumber) VALUES (?, ?, ?, ?, ?)",
                (jam, aktivitas, hari, datetime.now().isoformat(), sumber)
            )
            con.commit()
            con.close()
            catat(f"Pengalaman: jam {jam} = {aktivitas}")
            return True, "Tersimpan"
        except Exception as e:
            return False, str(e)

    def hitung_pengalaman(self):
        """Hitung jumlah pengalaman user."""
        try:
            con = sqlite3.connect(P["db"])
            n = con.execute("SELECT COUNT(*) FROM pengalaman").fetchone()[0]
            con.close()
            return n
        except:
            return 0

    def retrain_dari_pengalaman(self, verbose=True):
        """Retrain otak dari DATA_HABIT + pengalaman user."""
        n = self.hitung_pengalaman()
        if n == 0:
            if verbose:
                print("[Otak] Belum ada pengalaman user.")
            return False
        if verbose:
            print(f"[Otak] Retrain dari {n} pengalaman user...")
        self.latih(verbose=verbose)
        return True