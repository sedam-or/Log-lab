# Pengujian

Tes pemeriksa kontrak sudah tersedia di `test_contract.py`. Jalankan `make test-contract` dari root repo; tes memakai nilai sintetis, bukan credential deployment. Tes memeriksa drift env/template/dokumen, salah alamat/URL, token pasangan, placeholder, format secret, serta pesan error yang tidak mencetak nilai privat.

Tes aplikasi, API event, delivery, analisis dan dua VM belum tersedia; harus ditulis pada task anggota. Konvensinya `unittest`, file `test_*.py`, method `test_*`. Lulus pemeriksaan konfigurasi tidak berarti layanan atau acceptance sudah lulus.
