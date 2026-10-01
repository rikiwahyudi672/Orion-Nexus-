# ===PATCH===
# TYPE: replace_var
# TARGET: core.py
# VAR: DATA_HABIT
# DESC: Ganti DATA_HABIT 24 titik jadi 48 titik (per 30 menit)
# ===END===

DATA_HABIT = [
    # 00:00 - 05:30 (tidur)
    (0.0, "tidur"),  (0.5, "tidur"),  (1.0, "tidur"),  (1.5, "tidur"),
    (2.0, "tidur"),  (2.5, "tidur"),  (3.0, "tidur"),  (3.5, "tidur"),
    (4.0, "tidur"),  (4.5, "tidur"),  (5.0, "tidur"),  (5.5, "tidur"),
    # 06:00 - 06:30 (makan pagi)
    (6.0, "makan"),  (6.5, "makan"),
    # 07:00 - 11:30 (kerja pagi)
    (7.0, "kerja"),  (7.5, "kerja"),
    (8.0, "kerja"),  (8.5, "kerja"),
    (9.0, "kerja"),  (9.5, "kerja"),
    (10.0, "kerja"), (10.5, "kerja"),
    (11.0, "kerja"), (11.5, "kerja"),
    # 12:00 - 12:30 (makan siang)
    (12.0, "makan"), (12.5, "makan"),
    # 13:00 - 17:30 (kerja sore)
    (13.0, "kerja"), (13.5, "kerja"),
    (14.0, "kerja"), (14.5, "kerja"),
    (15.0, "kerja"), (15.5, "kerja"),
    (16.0, "kerja"), (16.5, "kerja"),
    (17.0, "kerja"), (17.5, "kerja"),
    # 18:00 - 21:30 (santai)
    (18.0, "santai"), (18.5, "santai"),
    (19.0, "santai"), (19.5, "santai"),
    (20.0, "santai"), (20.5, "santai"),
    (21.0, "santai"), (21.5, "santai"),
    # 22:00 - 23:30 (tidur)
    (22.0, "tidur"), (22.5, "tidur"),
    (23.0, "tidur"), (23.5, "tidur"),
]