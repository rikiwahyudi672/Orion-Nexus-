"""
fungsi_20261001_073602

Evolusi v2.7.1: Adaptasi dari masukan Riki.

Fungsi ini mengeksekusi sekumpulan *tugas* (tasks) dengan pendekatan yang
tenang, terukur, dan menghindari duplikasi kerja.  Empat prinsip utama
diperhatikan:

1. **Mode nrimo** – tidak mengambil semua tugas sekaligus; diproses satu‑per‑satu
   (atau dalam batch kecil) agar tidak terlalu agresif.
2. **Anti‑muter** – meminimalkan jumlah pemanggilan alat/fungsi; setiap tugas
   hanya diproses satu kali.
3. **Jujur lapor** – mengembalikan informasi apakah sebuah tugas sudah ada
   (sudah diproses sebelumnya) atau baru dibuat.
4. **Catat pelajaran** – setiap koreksi atau catatan disimpan dalam *kompas*
   (bukan sekadar arsip mati) untuk dipakai pada pemanggilan berikutnya.

Parameter
---------
tasks: list[dict]
    Daftar tugas yang akan diproses.  Setiap elemen harus memiliki minimal
    kunci ``"id"`` (identifier unik) dan ``"action"`` (callable yang menerima
    ``task`` sebagai argumen).  Contoh:
    ``{"id": "t1", "action": lambda t: print(t["id"])}``

max_batch: int, optional
    Jumlah maksimum tugas yang diproses dalam satu batch.  Nilai ``None`` berarti
    tidak ada batas (tetapi tetap diproses satu per satu untuk menjaga
    *nrimo*).  Default: ``1``.

return
------
dict
    Ringkasan hasil eksekusi dengan kunci:
    - ``"processed"``: list of task ids yang baru diproses.
    - ``"skipped"``: list of task ids yang sudah ada (tidak diproses lagi).
    - ``"lessons"``: list of catatan/lesson yang ditambahkan selama eksekusi.

Contoh penggunaan
-----------------
>>> tasks = [
...     {"id": "t1", "action": lambda t: print("run", t["id"])},
...     {"id": "t2", "action": lambda t: print("run", t["id"])}
... ]
>>> result = fungsi_20261001_073602(tasks, max_batch=2)
>>> result["processed"]
['t1', 't2']
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Set, Any


class _TaskEngine:
    """
    Engine internal yang menyimpan state global (processed tasks & lessons)
    dan menyediakan metode eksekusi yang mematuhi prinsip‑prinsip Riki.
    """

    def __init__(self) -> None:
        # Set of task identifiers yang sudah selesai diproses.
        self._done: Set[str] = set()
        # Catatan/lesson yang dipelajari selama eksekusi.
        self._lessons: List[str] = []

    def _log_lesson(self, message: str) -> None:
        """Simpan lesson baru jika belum ada (menghindari duplikasi)."""
        if message not in self._lessons:
            self._lessons.append(message)

    def process_task(self, task: Dict[str, Any]) -> str:
        """
        Proses satu task dengan aman.

        Parameters
        ----------
        task: dict
            Harus memiliki kunci ``"id"`` (str) dan ``"action"`` (callable).

        Returns
        -------
        str
            ``"new"`` bila task diproses, ``"existing"`` bila sudah diproses
            sebelumnya.
        """
        # Validasi dasar
        if not isinstance(task, dict):
            raise TypeError("Task harus berupa dict.")
        if "id" not in task or "action" not in task:
            raise KeyError('Task harus memiliki kunci "id" dan "action".')
        task_id = task["id"]
        action = task["action"]

        if not isinstance(task_id, str):
            raise TypeError('Task["id"] harus berupa str.')
        if not callable(action):
            raise TypeError('Task["action"] harus callable.')

        # Anti‑muter: hindari duplikasi
        if task_id in self._done:
            self._log_lesson(f"Task {task_id} sudah diproses sebelumnya.")
            return "existing"

        # Eksekusi dengan penanganan error terisolasi
        try:
            # Action diharapkan menerima task sebagai argumen.
            action(task)
        except Exception as exc:  # pragma: no cover
            # Jujur lapor: catat kegagalan tapi jangan mengklaim berhasil.
            self._log_lesson(f"Gagal mengeksekusi task {task_id}: {exc}")
            raise RuntimeError(f"Eksekusi task {task_id} gagal.") from exc

        # Tandai selesai
        self._done.add(task_id)
        self._log_lesson(f"Task {task_id} selesai diproses.")
        return "new"

    def get_lessons(self) -> List[str]:
        """Kembalikan salinan list lesson."""
        return list(self._lessons)


# Engine bersifat singleton dalam modul ini (mempertahankan state antar panggilan).
_engine = _TaskEngine()


def fungsi_20261001_073602(
    tasks: List[Dict[str, Any]],
    *,
    max_batch: Optional[int] = 1,
) -> Dict[str, List[str]]:
    """
    Eksekusi sekumpulan tugas dengan prinsip *nrimo*, *anti‑muter*, *jujur lapor*,
    dan *catat pelajaran*.

    Parameters
    ----------
    tasks: list[dict]
        Daftar tugas yang akan diproses.
    max_batch: int | None, optional
        Batas maksimum tugas yang diproses dalam satu batch.  ``None`` berarti
        tidak ada batas, namun tetap diproses satu per satu untuk menjaga
        ketenangan (mode nrimo).  Default: ``1``.

    Returns
    -------
    dict
        Ringkasan eksekusi dengan kunci ``"processed"``, ``"skipped"``, dan
        ``"lessons"``.
    """
    if not isinstance(tasks, list):
        raise TypeError("Parameter `tasks` harus berupa list.")
    if max_batch is not None and (not isinstance(max_batch, int) or max_batch <= 0):
        raise ValueError("`max_batch` harus berupa int positif atau None.")

    processed: List[str] = []
    skipped: List[str] = []

    # Mode nrimo: proses dalam batch kecil, tidak mengambil semua sekaligus.
    batch_size = max_batch if max_batch is not None else len(tasks)

    # Loop dengan langkah terukur
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i : i + batch_size]

        for task in batch:
            try:
                result = _engine.process_task(task)
                if result == "new":
                    processed.append(task["id"])
                else:
                    skipped.append(task["id"])
            except Exception as exc:  # pragma: no cover
                # Jujur lapor: catat kegagalan tetapi teruskan eksekusi batch selanjutnya.
                skipped.append(task.get("id", "<unknown>"))
                # Simpan lesson tentang kegagalan (sudah dilakukan di _engine)
                continue

    return {
        "processed": processed,
        "skipped": skipped,
        "lessons": _engine.get_lessons(),
    }