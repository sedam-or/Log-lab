# Deployment Debian

Direktori ini memuat provisioning guest, unit systemd, dan aturan firewall. Gunakan `source/` untuk A, `monitor/` untuk B, serta `common/` hanya untuk kebutuhan bersama yang nyata. Direktori peran dibuat saat sudah berisi berkas implementasi.

Rencana antarmuka setup adalah `make setup-source` dan `make setup-monitor` dari root repo di guest Debian. Root Makefile menjadi wrapper tipis untuk skrip di sini. Target `make setup-source` dan `make setup-monitor` memanggil `deployment/<peran>/setup.sh`; langkah lengkapnya ada di [docs/OPERASI-VM.md](../docs/OPERASI-VM.md). Guest harus sudah terpasang, memiliki Git/Make dan akses paket sementara, serta konfigurasi jaringan VMware yang sesuai; target aplikasi tidak otomatis membuat VM dari Windows kosong.

Setup memeriksa OS, memasang dependensi yang tercatat, menyiapkan konfigurasi lokal, memasang service/firewall, lalu memeriksa layanan. Pemanggilan ulang harus aman terhadap data dan secret yang ada. Perubahan yang bisa memutus SSH memerlukan pemeriksaan akses dan langkah pemulihan console. Panduan mencantumkan perintah console guest yang sama dengan yang dipakai lewat SSH dari host.

Saat memigrasikan konfigurasi lama dari `deploy/`, ubah semua referensi ke `deployment/`. Hindari path host privat, nomor interface yang diasumsikan, symlink menuju laptop pengembang, dan dependensi yang hanya kebetulan sudah ada.

Nama service, path env/DB/TLS, user service, bind IP, port dan entrypoint sudah dikunci pada [kontrak parameter 1.1.0](../docs/interface-contracts/index.md). Setup peran wajib memvalidasi env sebelum startup, membaca bind/port dari env untuk launcher, serta menolak placeholder/alias. Root Makefile memiliki `check-contract`, `test-contract`, `lab-bundle` (host), `setup-source` dan `setup-monitor` (VM; `LOGLAB_BUNDLE=` membawa env, TLS, dan akun dari `scripts/make_lab_bundle.py`). Skrip hanya diuji statis di CI; pembuktian pada VM masih harus dijalankan dan dicatat.
