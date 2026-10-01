# Update Diri

## Deskripsi
Orion update diri sendiri - dengan pengawasan.

## Alur
1. Bikin draft
2. Cek draft
3. Apply draft (dengan backup)
4. Test
5. Rollback kalau gagal

## Cara Pakai
```python
from update import bikin_draft, cek_draft, apply_draft, test_target

# Bikin draft
bikin_draft("file_baru.py", "print('hello')")

# Cek draft
cek_draft("_draft/file_baru.py.draft")

# Apply
apply_draft("_draft/file_baru.py.draft", "file_baru.py")

# Test
test_target("file_baru.py")
@'
# Update Diri

## Deskripsi
Orion update diri sendiri - dengan pengawasan.

## Alur
1. Bikin draft
2. Cek draft
3. Apply draft (dengan backup)
4. Test
5. Rollback kalau gagal

## Cara Pakai
python -c "import sys; sys.path.insert(0, 'skills/update-diri'); from update import bikin_draft; bikin_draft('file_baru.py', 'print(1)')"

## Fungsi
- bikin_draft(nama, kode) - bikin draft
- cek_draft(file) - cek syntax draft
- apply_draft(draft, target) - apply + backup
- test_target(file) - test syntax & import
- rollback(backup, target) - kembalikan backup
