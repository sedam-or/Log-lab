# Pekerjaan Erna, Arhasya, dan integrator

Pembagian nama sudah ditetapkan: **Erna menangani VM A Source**, **Arhasya menangani VM B Monitor**. Integrator adalah pemilik repo/pemimpin tim; nama penanggung jawab integrasi belum diisi. Nama Erna dan Arhasya adalah samaran kerja yang disetujui pemilik. Task ID adalah nomor pekerjaan; ID EP/AA/ML/UI/OP adalah rujukan requirement, bukan task yang berbeda.

Jika baru belajar software engineering, mulai dari [dasar proyek](basics.md), lalu baca [workspace](workspace.md), lalu [Erna](erna.md) atau [Arhasya](arhasya.md). Untuk urutan merge dan acceptance, baca [integrasi](integration.md). Rincian pembagian di bawah merupakan draf untuk diskusi; status instalasi tidak akan diubah menjadi selesai hanya karena panduannya sudah ditulis.

## Cara memakai daftar ini

Satu baris berarti satu hasil kerja yang harus bisa diperiksa. Kolom dependensi menunjukkan hasil yang perlu tersedia lebih dahulu. Contohnya, E-04 menunggu E-03 karena sender membutuhkan event yang sudah dibuat oleh login/outbox. Status “Belum” berarti belum ada bukti penyelesaian task, bukan berarti anggota pasti belum membaca panduan.

Kerjakan satu task dari panduan peran. Setelah hasil dan tesnya dapat diperiksa, ajukan PR kecil. Catat hasil aktual sebelum memperbarui status. Jika task masih membutuhkan hasil orang lain, gunakan blocked dan sebutkan dependensinya; jika tes berjalan tetapi salah, gunakan fail.

![Perjalanan tim sampai dua VM diuji](../architecture/assets/learning/integration-journey.png)

[Sumber Mermaid](../architecture/assets/learning/integration-journey.mmd).

## Status dan dependensi

| ID | Pemilik | Hasil yang harus diserahkan | Bergantung pada | Status aktual |
| --- | --- | --- | --- | --- |
| F-01 | Integrator | PRD/SRS teradaptasi, glossary dan index yang bisa ditinjau | Inventaris lama | Draf tersedia; review isi belum selesai |
| F-02 | Integrator + Erna/Arhasya | Daftar modul, schema/fixture A–B, ISO/hash, paket Python, template konfigurasi, kontrak paket model dan feature schema yang dibekukan | F-01 | Belum |
| F-03 | Integrator | Skeleton paket/runner, helper bersama, target bootstrap/setup umum dan fixture siap; kode peran ditulis Erna/Arhasya | F-02 | Belum |
| F-04 | Integrator | Commit baseline pengembangan dicatat, pengaturan review main/PR diverifikasi, panduan dirender ke PDF | F-03 | Belum |
| F-05 | Integrator | Dataset/training/evaluasi offline, paket model + hash + expected prediction | F-02 + R-04 diterima | Belum |
| E-01 | Erna | Catatan resource laptop dan rencana VM Source | F-01 | Belum |
| E-02 | Erna | Guest Debian, jaringan, akses host dan workspace Git sesuai panduan | F-04 | Belum |
| E-03 | Erna | Kode login/outbox + unit tests dan PR pertama | E-02 | Belum |
| E-04 | Erna | Kode sender/status + tests retry/receipt, memakai receiver uji | E-03 | Belum |
| E-05 | Erna | Deployment Source, reboot/backup/restore dan PR konfigurasi | E-04 | Belum |
| E-06 | Erna | Ringkasan bukti peran sebelum integrasi | E-05 | Belum |
| R-01 | Arhasya | Catatan resource laptop dan rencana VM Monitor | F-01 | Belum |
| R-02 | Arhasya | Guest Debian, jaringan, akses host dan workspace Git sesuai panduan | F-04 | Belum |
| R-03 | Arhasya | Kode ingest/status dan tests validasi/receipt/konflik | R-02 | Belum |
| R-04 | Arhasya | Kode fitur, window/kualitas/revisi dan rules beserta tes | R-03 | Belum |
| R-05 | Arhasya | Kode inferensi/runtime model dan dashboard beserta tes | R-04 + F-05 | Belum |
| R-06 | Arhasya | Deployment Monitor, reboot/backup/restore dan PR konfigurasi | R-05 | Belum |
| R-07 | Arhasya | Ringkasan bukti peran sebelum integrasi | R-06 | Belum |
| I-01 | Integrator + keduanya | Audit PR yang sudah masuk; merge sisanya dan catat commit integrasi | E-06/R-07 | Belum |
| I-02 | Integrator + keduanya | Dua peran dari commit yang sama diuji pada satu host Windows 11 | I-01 | Belum |
| I-03 | Integrator + keduanya | Hasil acceptance, tag jika lulus, serta sumber/PDF artefak Modul 5 | I-02 | Belum |

E-01/R-01 dapat dikerjakan sambil Fase fondasi berjalan: membaca panduan dan mencatat prasyarat tidak memerlukan installer. E-02/R-02 menunggu baseline F-04 agar anggota tidak memasang versi berbeda. Erna dan Arhasya menulis kode serta memasang VM perannya. Setiap task dapat diajukan sebagai PR kecil; jangan menahan seluruh pekerjaan sampai semua task peran selesai.

## Arti selesai

Sebuah task selesai bila output ada, pemeriksaan yang disebut pada panduan peran sudah dijalankan, hasil aktual ditulis, dan reviewer menyetujui. Jika belum lulus, catat pesan error aman, kondisi awal, langkah yang dicoba, dampak dan langkah selanjutnya. Command tanpa output atau checklist yang dicentang tanpa bukti tidak cukup.

Sumber bukti privat disimpan di luar Git. Ringkasan aman memakai case ID, requirement, commit, versi OS/runtime, langkah, expected/actual, status, dan reviewer. Screenshot VMware harus benar-benar dari layar VMware. Screenshot host/SSH, diagram, dan log bukan screenshot VM.

## Pengumpulan tugas

PDF Erna dan PDF Arhasya dibuat dari Markdown peran yang sama setelah F-04, dilengkapi bagian workspace bersama yang diperlukan. Sumber tetap diedit di repo. PDF Modul 5 baru dibuat setelah kontribusi, konflik/resolusi nyata atau latihan berlabel, dan integrasi benar-benar tercatat. Nama tim/NIM tidak ditebak.

## Batas penyerahan peran dan pengujian pasangan

E-06 dan R-07 hanya menunggu hasil coding/tes/deployment peran. Setelah keduanya diserahkan, integrator melakukan I-01 dan tim menjalankan I-02. Erna/Arhasya ikut I-02 sebagai pekerjaan bersama. Penyerahan peran tidak menunggu I-02, sehingga urutan dependensi dapat dijalankan tanpa berputar. PR fitur R-04 tetap dapat masuk lebih awal untuk memungkinkan training F-05.
