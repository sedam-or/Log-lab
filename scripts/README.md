# Alat yang dapat dijalankan

| File | Cara pakai dari root repo | Hasil |
| --- | --- | --- |
| dev_setup.py | `make dev-setup` pada Python 3.13 | Venv, dependency terkunci, package lokal, pip check dan tes fondasi |
| first_check.py | `make first-check ROLE=source` atau monitor | Contoh DB/Settings/fixture dan receiver simulasi |
| check_contract.py | `make check-contract` atau CLI --help | Kesamaan JSON, versi manusia, contoh env dan tabel teknis |
| check_iso.py | `python3 scripts/check_iso.py /path/ke/ISO` | Nama dan SHA-256 file unduhan cocok atau ditolak |

`check_contract.py` adalah entrypoint tipis; validator bersama berada di src/loglab/contract.py dan juga dipakai Settings. `--sync` hanya menghasilkan ulang dokumen/template publik, bukan env privat. Skrip service guest tetap ditulis di deployment/ oleh anggota. Tak satu pun alat ini membuat screenshot VMware buatan.
