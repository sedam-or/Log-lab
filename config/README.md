# Template konfigurasi

Simpan nilai contoh tanpa secret di sini, misalnya `source.example.*` dan `monitor.example.*`. Template aktual dibuat melalui D-04 dan ditinjau bersama karena alamat tujuan, trust TLS, identitas sumber, dan versi schema harus cocok.

Alamat layanan harus dapat dikonfigurasi. Setup meminta atau menghasilkan secret lokal dengan izin terbatas dan tidak menimpanya pada pemanggilan ulang. Password, bearer token, private key, database, serta konfigurasi runtime privat tidak disimpan di repo atau task PDF. File yang telanjur di-commit tidak hilang dari riwayat hanya karena ditambahkan ke `.gitignore`.
