# Aturan dasar proyek

<a href="../../README.md"><kbd>README</kbd></a> <a href="../../README.md#hasil-aplikasi"><kbd>Hasil aplikasi</kbd></a> <a href="../tugas/erna.md"><kbd>Erna</kbd></a> <a href="../tugas/arhasya.md"><kbd>Arhasya</kbd></a>

Baseline berarti aturan awal yang dipakai semua anggota agar OS, format data dan bagian bersama tetap cocok. Halaman ini menjadi rujukan ketika menjalankan tugas; gambaran aplikasi saat selesai ada pada tombol di atas.

**Tanggal:** 29 Oktober 2026. **Status:** parameter integrasi sudah dibekukan sebagai kontrak konfigurasi 1.0.0; installer, ISO/hash final dan acceptance aplikasi masih menunggu pengerjaan. Dokumen ini mengikat pembagian pekerjaan awal. PRD/SRS dan standar telah diadaptasi sebagai draf; installer dan acceptance belum tersedia. Lihat [index arsitektur](index.md) dan [task tim](../tugas/index.md).

Untuk pembaca baru, [dasar proyek](../tugas/bersama.md#kenali-aplikasi-yang-dibangun) menjelaskan istilah dan satu contoh alur. Halaman baseline ini digunakan sebagai referensi lingkungan dan batas file ketika mengerjakan task.

## Kontrak IP dan nama variabel

[Kontrak parameter](../interface-contracts/index.md) menetapkan nilai final profil integrasi dalam [config/contract.json](../../config/contract.json), contoh env Source/Monitor, serta cara memeriksanya. Kedua anggota wajib menjalankan `make check-contract` sebelum PR dan pemeriksaan env privat sebelum startup. Perubahan IP/nama/port lewat satu branch saja tidak diterima. Nilai contoh yang ada di tabel baseline ini merujuk kontrak tersebut.

## Tujuan dan pembagian VM

LogLab memakai akun fiktif untuk menghasilkan event login. VM A mencatat hasil autentikasi ke outbox lokal dan mengirimnya ke B. VM B menerima event, menyimpan data, membentuk analisis rules serta klasifikasi Logistic Regression lokal, dan menyajikan dashboard operator. Model dilatih offline; tidak ada LLM, broker tambahan, atau pemblokiran akun otomatis.

| Aspek | Baseline kerja |
| --- | --- |
| Host integrasi akhir | Windows 11 dengan VMware Workstation; versi aktual dicatat saat acceptance |
| Guest A dan B | Debian 13 amd64 yang sama; ISO dan SHA-256 persis ditetapkan sebelum task instalasi dibagikan |
| Profil A | 1 vCPU, RAM 1 GiB, disk dinamis 20 GiB |
| Profil B | 2 vCPU, RAM 2 GiB, disk dinamis 20 GiB |
| Runtime | Python 3.13 dengan virtual environment dan dependency lock; paket yang dipakai harus diverifikasi pada Debian target |
| Jaringan integrasi | Host-only `172.16.202.0/24`; host `.1`, A `.21`, B `.22`, setelah diperiksa tidak berbenturan |
| Port | SSH `22` untuk administrasi jika diaktifkan; HTTPS `8443` untuk aplikasi |
| Arah aplikasi | Browser host ke A/B; sender A ke API B; database tidak membuka port jaringan |
| Internet | Akses sementara saat clone/install; runtime demonstrasi terisolasi sesuai konfigurasi yang diverifikasi |

Nomor interface guest dan pemetaan VMnet ditentukan dari mesin aktual, bukan di-hardcode dari laptop pengembang. Alamat layanan harus dapat dikonfigurasi. Laptop anggota dapat memiliki host OS berbeda, tetapi guest yang diuji tetap Debian target. Petunjuk host Windows dan Linux yang berbeda perlu ditandai pada panduan.

## SSH untuk kenyamanan copy-paste

Rekomendasi SSH berasal dari kebutuhan menyalin perintah di terminal host tanpa bergantung pada clipboard VMware. Panduan anggota harus menjelaskan pemasangan OpenSSH Server di guest, pemeriksaan IP, login host-ke-guest, pemasangan public key, serta verifikasi fingerprint. Console VMware tetap menjadi alternatif dan jalur pemulihan jika jaringan/SSH belum siap. Jangan menaruh password atau private key dalam task PDF.

SSH tidak diperlukan di antara VM A dan B untuk jalur aplikasi. A mengirim event melalui HTTPS. Nama/path TLS, CA, token sumber dan env mengikuti kontrak parameter 1.0.0; nilai rahasia dibuat privat saat provisioning.

## Reproducibility yang dinilai

Targetnya adalah pemasangan ulang dari sumber yang menghasilkan layanan dan perilaku yang sama pada lingkungan tercatat. Clone Git tidak menjamin disk VM identik bit demi bit atau membawa database/snapshot sebelumnya.

Sebelum memberi label siap dipasang ulang, catat dan verifikasi:

- Commit/tag repo, guest OS, nama ISO, sumber unduhan resmi, dan SHA-256 ISO.
- Versi Python, dependency lock beserta hash paket, daftar paket Debian, serta sumber repositori paket yang dipakai. Jika memakai mirror bergerak, jelaskan batas kesamaan versi; kebutuhan versi OS yang persis memerlukan sumber paket yang dibekukan.
- Resource VM, jaringan, port, konfigurasi tanpa secret, versi schema, serta versi/hash model dan seed yang relevan.
- Setup yang dapat dijalankan ulang tanpa menimpa secret, menghapus data, atau membuat service ganda.
- Hasil instalasi bersih, startup, reboot, dan tes peran; penerimaan final mencakup kedua VM bersama.

Repo akan menyediakan satu target setup per peran. Nama yang direncanakan adalah `make setup-source` dan `make setup-monitor`; keduanya belum tersedia. Make dijalankan di guest Debian. Pembuatan guest dan konfigurasi VMware pada host adalah prasyarat tersendiri, bukan kemampuan yang otomatis diberikan oleh perintah setup aplikasi.

## Kepemilikan file

| Pemilik | Cakupan yang direncanakan |
| --- | --- |
| Erna | Implementasi dan tes login/outbox/sender/status Source, setup dan verifikasi peran, `deployment/source/`, template `config/source.example.*`, tes Source, panduan tugas A |
| Arhasya | Implementasi dan tes ingest/analysis/inferensi/dashboard, setup dan verifikasi peran, `deployment/monitor/`, template `config/monitor.example.*`, tes Monitor, panduan tugas B |
| Integrator dengan review Erna/Arhasya | Schema/helper bersama, training/evaluasi offline, paket model, root Makefile, dependency lock, `deployment/common/`, tes kontrak/integrasi, PRD/SRS, baseline, serta daftar task |

Path per peran dibuat ketika berisi implementasi; direktori kosong tidak perlu ditambahkan. Tentukan daftar modul aktual sebelum implementasi. Jika kode lama masih memakai modul datar dalam `src/loglab/`, petakan kepemilikannya tanpa refactor besar hanya demi pembagian tugas.

## Pengujian di laptop anggota dan integrasi

Host-only pada dua laptop merupakan dua jaringan terpisah. Memakai subnet yang sama tidak membuat A di laptop pertama dapat mencapai B di laptop kedua. Setiap anggota menguji perannya memakai fixture atau mock yang dibekukan bersama. Hasil ini dicatat sebagai uji peran.

Untuk acceptance pasangan, integrator memasang kedua peran dari commit yang sama pada satu host VMware. Verifikasi TLS, penerimaan event, receipt, retry/duplikat, hasil analisis, dashboard, dan service setelah reboot. Riwayat merge atau keberhasilan setup satu VM tidak menggantikan pengujian tersebut.

## Hal yang perlu diselaraskan

Dokumen workspace sebelumnya memakai istilah host Linux, path `deploy/`, serta catatan deployment/evidence lama. Migrasi harus menyesuaikan target Windows 11 dan `deployment/`, memeriksa link, menghapus path privat, serta mempertahankan ID requirement. Status draf, persetujuan pemilik, persetujuan dosen, dan hasil uji aktual harus ditulis berbeda. Jangan mengklaim evidence lama berlaku pada commit repo baru.

## Panduan peran

Workspace anggota dijelaskan di [workspace](../tugas/bersama.md#folder-dan-terminal). Erna membuka [task Source](../tugas/erna.md); Arhasya membuka [task Monitor](../tugas/arhasya.md). Batas coding bersama dan urutan penyatuan dijelaskan pada [integrasi](../tugas/bersama.md#menyatukan-pekerjaan).
