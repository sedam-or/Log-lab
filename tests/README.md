# Pengujian

Jalankan `make dev-setup` sekali, lalu `make test` untuk semua tes yang tersedia. Tes fondasi mencakup config/kontrak, event/digest/receipt/status, DB/rollback/unique identity, backup, password/pseudonim dan stack web ASGI. `make first-check ROLE=source` atau monitor memberi contoh hasil yang dapat dibaca pemula tanpa VM lawan.

Folder fixtures berisi data sintetis dan receipt yang diharapkan; tidak ada credential deployment. Fixture JSON diperiksa oleh helper event dan unit tests. Tes peran Source/Monitor, fault/performa dan acceptance dua VM ditambahkan pada tugas anggota. Lulus fondasi bukan bukti aplikasi atau deployment final sudah lulus.
