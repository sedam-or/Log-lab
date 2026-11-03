# Catatan perubahan

## Belum dirilis

### Kontrak parameter 1.1.0 (MINOR, 3 November 2026)

- Menambah status endpoint (`implemented`/`planned`), rute UI Monitor, kode error beserta perilaku retry, aturan retry sender, pemetaan counter status Source, test vector digest event, dan izin berkas tambahan (CA/sertifikat, daftar akun uji, backup, `/run/loglab`).
- Menambah aturan versi (MAJOR/MINOR/PATCH) dan riwayat perubahan kontrak.
- `LOGLAB_CONTRACT_VERSION` berubah menjadi `1.1.0`: env yang dibuat dari templat 1.0.0 harus dibuat ulang (mis. lewat `make lab-bundle`).
- Tes baru memeriksa rute aplikasi terhadap kontrak.

### Source, sender, dan deployment

- Source: `/health`, `GET /login`, `POST /api/v1/login`, entrypoint `loglab.source_main:app`, seed akun dari `test-accounts.json`, kapasitas outbox (10.000 event / 64 MiB).
- Sender di dalam proses Source (file lock, retry backoff, validasi receipt, heartbeat).
- `deployment/source/*`, `scripts/make_lab_bundle.py`, `make lab-bundle|setup-source|setup-monitor`, `docs/OPERASI-VM.md`. Belum dibuktikan pada VM.

### Dokumentasi

- Menetapkan struktur repository mengikuti contoh materi Pertemuan 5.
- Mencatat baseline kerja Debian, pembagian Source/Monitor, alur kontribusi, dan daftar pekerjaan dokumentasi/integrasi.
- Menjelaskan SSH sebagai pilihan yang direkomendasikan untuk memudahkan copy-paste dari host.

Belum ada rilis aplikasi, installer tervalidasi, atau acceptance pasangan VM pada repository ini.

### Refinement dokumentasi

- Menetapkan nama samaran Erna untuk Source dan Arhasya untuk Monitor.
- Menginventarisasi dokumen lama, memindahkan PRD dan memecah SRS per kemampuan, serta menggunakan ulang assets diagram dan standar dengan status yang jelas.
- Menambahkan index dokumentasi, panduan workspace guest/SSH, task spesifik anggota, dan perjalanan integrasi Git serta runtime.
- Memperjelas bahwa Erna/Arhasya menulis kode dan tes peran; training offline dan helper bersama ditangani integrator.

### Panduan untuk pembaca pemula

- Menjelaskan host/guest, SSH, folder, Git/PR, event/outbox/receipt, fitur dan inferensi dengan contoh bertahap.
- Menulis ulang panduan coding Erna/Arhasya, alur kontribusi dan integrasi dengan hasil yang diharapkan serta case pemeriksaan.
- Menambahkan tujuh diagram Mermaid beserta PNG render untuk dokumentasi dan ekspor berikutnya.
- Memperbaiki dependensi penyerahan hasil peran agar mendahului pengujian pasangan, serta menjelaskan merge fitur yang diperlukan training.

### Hasil branch dan navigasi tim

- Menyederhanakan panduan anggota menjadi empat halaman di `docs/tugas/`: daftar, Erna, Arhasya dan panduan bersama.
- Menambahkan target pohon file, hasil perilaku, bukti, serta isi setiap PR untuk kedua peran.
- Memperluas README sebagai pintu masuk tujuan, aturan, pembagian kerja dan hasil repo gabungan.
- Menambahkan tombol tautan pada halaman penting serta menyimpan catatan hasil pada panduan anggota masing-masing.

### Kontrak parameter 1.0.0 pada 29 Oktober 2026

- Membekukan IP/port, hostname, source ID, service/path, nama Settings/env dan endpoint untuk pasangan lab.
- Menambahkan manifest publik, template env per peran, pemeriksa repo/env/pasangan, tes alat dan workflow PR/main.
- Memastikan alamat host-only bukan default gateway, scope HMAC hanya Source, dan secret pasangan diprovision privat.
- Menyelaraskan panduan dengan command yang benar-benar tersedia; installer/aplikasi dan acceptance tetap belum tersedia.

### Fondasi agar anggota dapat mulai coding

- Menambahkan config/contract.md yang dihasilkan dari JSON, serta pilihan ISO/hash resmi.
- Menyediakan package bersama, lock web/test ber-hash, loader, schema/fixture/receiver simulasi dan bootstrap yang dapat dijalankan.
- Menambahkan make dev-setup, test dan first-check, memperbarui README serta tugas awal tanpa menunggu model/deployment final.
- Menandai mulai-v1 sebagai titik awal coding, bukan tag rilis aplikasi; asal helper lama dan batas pengujian dicatat.
