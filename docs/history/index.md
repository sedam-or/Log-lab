# Riwayat dan migrasi

[Inventaris lengkap](inventory.md) mencatat sumber lama, SHA-256, keputusan pemindahan, dan yang masih perlu diselaraskan. Halaman ini menyimpan konteks agar anggota tidak perlu membaca seluruh arsip sebelum bekerja.

Implementasi lama pernah menjalankan dua guest Debian pada host Linux. Audit lama mencatat source/outbox/sender di A; ingest/analisis/model/dashboard di B; classifier StandardScaler dan Logistic Regression lokal dengan seed 42. Audit juga mencatat pengujian 27 tes serta eksperimen sintetis. Angka tersebut adalah klaim pada laporan historis beserta batas lingkungannya; tidak dihitung sebagai hasil pada commit repo baru.

Kesenjangan yang tetap relevan: belum ada acceptance host lab Windows 11, review label independen dan walkthrough operator independen belum lengkap, kanal VMware Tools/VIX pernah bermasalah, dan kesamaan hash arsip tidak menjamin perilaku setelah boot. Panduan sekarang mengutamakan SSH host-ke-guest untuk kemudahan terminal dan tidak bergantung pada copy-paste console VMware.

Riwayat task selesai, reset VM, path laptop, dan identitas paket backup lama tidak dipakai sebagai instruksi Erna/Arhasya. Source lama belum dimigrasikan. Paket model dan dependency yang dirujuk laporan lama harus diverifikasi ulang sebelum integrator menawarkannya sebagai rilis yang dapat dipasang.

Keputusan baru: satu repo, dua peran, guest Debian yang sama, target host integrasi Windows 11, struktur `deployment/`, Erna untuk Source dan Arhasya untuk Monitor. Panduan penugasan berstatus draf pembagian untuk diskusi; hasil instalasi/PR mereka belum ada.

Klarifikasi pemilik: Erna dan Arhasya juga menulis kode aplikasi perannya, bukan hanya memasang/menguji. Panduan peran direvisi menjadi task coding + tests + deployment. Integrator menyediakan fondasi bersama dan training offline; Arhasya menulis inferensi runtime.
