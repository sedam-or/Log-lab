# Riwayat dan migrasi

[Inventaris lengkap](inventory.md) mencatat sumber lama, SHA-256, keputusan pemindahan, dan yang masih perlu diselaraskan. Halaman ini menyimpan konteks agar anggota tidak perlu membaca seluruh arsip sebelum bekerja.

Implementasi lama pernah menjalankan dua guest Debian pada host Linux. Audit lama mencatat source/outbox/sender di A; ingest/analisis/model/dashboard di B; classifier StandardScaler dan Logistic Regression lokal dengan seed 42. Audit juga mencatat pengujian 27 tes serta eksperimen sintetis. Angka tersebut adalah klaim pada laporan historis beserta batas lingkungannya; tidak dihitung sebagai hasil pada commit repo baru.

Kesenjangan yang tetap relevan: belum ada acceptance host lab Windows 11, review label independen dan walkthrough operator independen belum lengkap, kanal VMware Tools/VIX pernah bermasalah, dan kesamaan hash arsip tidak menjamin perilaku setelah boot. Panduan sekarang mengutamakan SSH host-ke-guest untuk kemudahan terminal dan tidak bergantung pada copy-paste console VMware.

Riwayat task selesai, reset VM, path laptop, dan identitas paket backup lama tidak dipakai sebagai instruksi Erna/Arhasya. Aplikasi peran lama tidak disalin utuh; adaptasi helper bersama dijelaskan di bawah. Paket model dan dependency yang dirujuk laporan lama harus diverifikasi ulang sebelum integrator menawarkannya sebagai rilis yang dapat dipasang.

Keputusan baru: satu repo, dua peran, guest Debian yang sama, target host integrasi Windows 11, struktur `deployment/`, Erna untuk Source dan Arhasya untuk Monitor. Panduan penugasan sekarang dapat dipakai untuk mulai; hasil instalasi/PR anggota tetap menunggu pekerjaan mereka.

Klarifikasi pemilik: Erna dan Arhasya juga menulis kode aplikasi perannya, bukan hanya memasang/menguji. Panduan peran direvisi menjadi task coding + tests + deployment. Integrator menyediakan fondasi bersama dan training offline; Arhasya menulis inferensi runtime.

## Fondasi coding 29 Oktober 2026

Helper events/security/db/backup dan tes dasarnya diadaptasi dari workspace sebelumnya, bukan diakui sebagai kode baru Erna/Arhasya. Perubahan meliputi validasi input, identitas event lintas stream, penolakan downgrade DB, penutupan handle SQLite, loader config yang memakai validator parameter yang sama, fixture serta ReceiverStub. Nama event/receipt dan parameter versi 1.0.0 dipertahankan.

Environment diverifikasi pada CPython 3.13.16 Linux x86-64 terisolasi; host developer bukan Debian guest anggota. SHA ISO diperiksa dari daftar resmi Debian, tetapi seluruh image dan instalasi VM laptop anggota belum diuji oleh agen. Peringatan handle SQLite diperbaiki dan tes HTTP memakai HTTPX ASGITransport untuk menghindari wrapper yang deprecated. Tes async tertahan dalam sandbox terbatas lalu lulus pada proses di luar sandbox; batas environment itu tidak dinyatakan sebagai hasil VM.

Penyelarasan kontrak status: SRS kini menyebut sepuluh field request persis seperti fixture, sedangkan waktu penerimaan dan perkiraan offset dihitung Monitor. Schema DB baru juga menyimpan offered/accepted_local. Ini menyelesaikan ambiguitas request/response sebelum anggota menulis endpoint; database lama tidak dimigrasikan otomatis oleh fondasi.

Pemeriksaan fondasi: 36 tes unittest lulus pada Python 3.13.16, bootstrap berhasil dijalankan ulang, dan first-check Source/Monitor lulus dengan receiver simulasi. Pemeriksaan navigasi menemukan 385 tautan lokal valid sebelum penambahan tabel penjelas kontrak; gambar mulai kerja dirender dan diperiksa. Pemeriksaan ini tidak menandai aplikasi peran, TLS nyata, training atau acceptance Windows selesai.
