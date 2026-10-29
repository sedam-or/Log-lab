# Konfigurasi yang dipakai kedua anggota

[contract.json](contract.json) menetapkan parameter publik versi 1.0.0. [source.example.env](source.example.env) adalah titik awal Erna; [monitor.example.env](monitor.example.env) untuk Arhasya. Penjelasan nama, nilai, rahasia, scope peran dan command pemeriksaan ada pada [kontrak parameter](../docs/interface-contracts/index.md).

Jalankan `python3 scripts/check_contract.py` dari root repo. Jika kontrak diubah melalui PR bersama, `python3 scripts/check_contract.py --sync` menghasilkan ulang contoh dan tabel. Jangan mengedit template terpisah dari JSON. Contoh berisi placeholder sehingga tidak dapat dipakai sebagai env runtime sebelum diisi privat dan lulus validasi.

Env runtime berada di `/etc/loglab/`, bukan dalam clone. Token/password/private key/database tidak masuk Git. Konfigurasi berbentuk literal KEY=value; jangan menjalankan file env dengan shell source karena hash password mengandung karakter dolar.
