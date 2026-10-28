# Menyiapkan fondasi dan menyatukan dua pekerjaan

Integrator bertanggung jawab agar Source Erna dan Monitor Arhasya memakai aturan yang sama. Tanggung jawab ini dimulai sebelum coding paralel, lalu berlanjut ketika PR masuk dan kedua VM diuji bersama. Nama penanggung jawab integrasi belum diisi; sementara peran tersebut mengikuti pemilik repo/pemimpin tim.

Ada dua hasil yang perlu dibedakan saat merencanakan pekerjaan. **Integrasi kode** menyatukan perubahan file ke main dan memeriksa tesnya. **Integrasi runtime** menjalankan dua layanan dari kode tersebut pada jaringan yang sama, lalu membuktikan komunikasi sebenarnya. Keduanya diperlukan karena Git dapat menggabungkan file meskipun URL, token, format event atau perilaku kedua layanan belum cocok.

![Perjalanan dari fondasi sampai rilis yang diperiksa](../architecture/assets/learning/integration-journey.png)

[Sumber Mermaid](../architecture/assets/learning/integration-journey.mmd).

## Tahap pertama menyiapkan bahan kerja bersama

Erna dan Arhasya menulis kode aplikasi. Mereka membutuhkan batas yang jelas supaya tidak harus menebak format event, menulis helper security berbeda, atau memasang dependency yang tidak kompatibel. Integrator menyediakan fondasi F-01 sampai F-04 sebelum environment coding anggota dianggap siap.

### F-01 Menetapkan kebutuhan yang dipakai

Review [PRD](../requirements/PRD.md), [SRS per bagian](../requirements/srs/index.md), baseline dan diagram. PRD menjelaskan tujuan/scope, sedangkan SRS menjelaskan aturan teknis serta pemeriksaannya. Pastikan target Windows 11, Debian dan peran kedua VM konsisten. Catat usulan lama yang belum diterima agar anggota tidak menganggapnya requirement aktif.

Hasil F-01 adalah versi kebutuhan yang dapat dirujuk Erna/Arhasya, beserta status review yang nyata. Tugas membaca resource laptop E-01/R-01 dapat berlangsung sambil review ini berjalan. Kode peran belum ditandai lulus hanya karena kebutuhan sudah tertulis.

### F-02 Membekukan format dan interface bersama

Tentukan ISO Debian beserta SHA-256, versi Python/dependency dan helper yang akan tersedia. Tetapkan field event/receipt/status, metode digest dan operasi database/security/config yang diperlukan kedua peran. Jelaskan fungsi dan cara pakai helper; anggota perlu mengetahui input, output serta error yang mungkin terjadi.

Buat fixture event valid/invalid, duplikat, konflik, receipt cocok/tidak cocok dan status sumber. Fixture menjadi contoh yang dapat dijalankan, sehingga Erna dan Arhasya mempunyai jawaban yang sama untuk kasus yang sama. Contohnya, duplikat event identik harus dipahami sebagai satu kejadian oleh kedua sisi.

Tetapkan feature schema serta rubrik training. Paket model final menunggu ekstraktor R-04; jangan membekukan model berdasarkan ekstraktor lain yang belum disepakati. Hasil F-02 berupa kontrak, daftar input bersama, versi lingkungan, dan pembagian file yang bisa diperiksa anggota.

### F-03 Menyiapkan environment dan alat uji dasar

Siapkan skeleton package, dependency lock, runner tes dan helper bersama `events.py`, `config.py`, `db.py`, `security.py`, serta `backup.py` sesuai kontrak yang ditetapkan. **Skeleton** berarti struktur awal yang menyediakan tempat dan interface untuk menambahkan kode, belum aplikasi peran yang selesai.

Sediakan bootstrap environment, receiver uji untuk Erna dan fixture pengirim untuk Arhasya. Dokumentasikan command beserta expected output yang sudah dicoba pada Debian target. Root Makefile mengoordinasikan pemanggilan helper/target peran; implementasi deployment Source/Monitor diselesaikan pada E-05/R-06.

Bila menggunakan ulang kode lama, periksa dependency/path dan jelaskan asalnya. Anggota tidak diminta mengklaim kode lama yang disalin penuh sebagai implementasi yang ditulis sendiri. F-03 selesai ketika environment dasar dan tes helper dapat dijalankan ulang; pengujian aplikasi penuh menunggu kode anggota.

### F-04 Membagikan baseline pengembangan

Catat SHA commit yang berisi fondasi, cara bootstrap, ISO/hash, contoh command yang sudah terisi, dan cara memperoleh konfigurasi privat. Periksa bahwa akun GitHub anggota dapat mengakses repo dan menyerahkan perubahan. Pengaturan review/proteksi main diperiksa pada GitHub; aturan yang ditulis pada dokumen tidak otomatis mengaktifkan fitur tersebut.

Beri Erna dan Arhasya sumber panduan dengan versi yang sama. Jika mengekspor PDF, gunakan Markdown yang sama dan pastikan gambar terbaca. Baseline pengembangan ini cukup untuk mulai menulis kode; installer aplikasi yang lengkap tetap diselesaikan bersama kode peran.

## Tahap kedua coding paralel dan review bertahap

Erna mengerjakan login/outbox, sender, lalu deployment. Arhasya mengerjakan ingest, fitur/analisis, inferensi/console, lalu deployment. Setiap bagian mempunyai PR kecil, tes dan reviewer. PR tidak ditahan sampai seluruh task anggota selesai.

Urutan bertahap itu diperlukan untuk dependency model. PR fitur R-04 harus diterima lebih dahulu agar integrator dapat melatih model pada fitur yang sama. Jika semua PR Arhasya baru boleh masuk setelah model selesai, training justru akan menunggu kode yang belum tersedia di main.

### F-05 Menyiapkan training dan paket model

Sesudah ekstraktor R-04 diterima, integrator menulis atau mengadaptasi `dataset.py`, `generate_dataset.py`, `training.py`, `train_model.py`, dan tests terkait. Pekerjaan ini memenuhi ML-01–ML-04: dataset berlabel yang dapat dijelaskan, split tanpa kebocoran, training offline dan evaluasi yang sesuai.

**Training offline** berarti model dilatih sebagai pekerjaan terpisah, bukan dilatih ulang otomatis dari setiap login. Hasilnya adalah paket model yang memiliki schema, urutan fitur, konfigurasi, seed, checksum dan catatan asal input. Paket diberikan bersama contoh prediksi yang diharapkan untuk tes runtime Arhasya. Batas data sintetis dan review yang belum selesai ditulis dengan jelas.

F-05 menunggu fitur R-04, tetapi tidak menahan Erna mengerjakan sender atau Arhasya menulis console. R-05 bagian inferensi final menunggu paket ini. Klaim metrik dan provenance harus berasal dari run yang dibuat, bukan menyalin angka laporan laptop lama.

## Tahap ketiga menyiapkan satu versi gabungan

E-06 dan R-07 adalah penyerahan hasil peran sebelum pengujian pasangan. Keduanya berisi PR, tes dan masalah yang masih ada. Partisipasi menguji dua VM dilakukan pada I-02 setelah audit berikut; dengan demikian tidak ada ketergantungan berputar.

### I-01 Audit perubahan yang sudah masuk main

Periksa seluruh PR yang dibutuhkan, termasuk helper, fitur, training, kedua aplikasi, tes dan deployment. Sebagian PR sudah masuk selama pengerjaan. I-01 memeriksa keadaan gabungan terakhir, bukan menjadi satu-satunya waktu merge sepanjang proyek.

Untuk PR yang masih terbuka, merge satu per satu. Anggota yang belum merge mengambil main terbaru pada branch-nya, memeriksa/resolusikan konflik jika ada, lalu menjalankan tes yang terdampak dan memperbarui PR. Langkah command dijelaskan pada [panduan kontribusi](../../CONTRIBUTING.md).

Sesudah semua perubahan yang diperlukan tersedia, jalankan pemeriksaan gabungan dan catat satu SHA commit untuk pengujian dua VM. **Mematok commit** berarti mencatat versi persis yang harus dipasang pada keduanya; memakai main yang berubah pada dua waktu berbeda dapat menghasilkan kode yang tidak sama.

## Tahap keempat menjalankan dua VM pada satu jaringan

![Perbedaan coding pada dua laptop dan pengujian pada satu host](../architecture/assets/learning/local-and-integration.png)

[Sumber Mermaid](../architecture/assets/learning/local-and-integration.mmd).

Host-only adalah jaringan privat yang dibuat VMware pada satu host. Host-only Erna dan host-only Arhasya berada pada laptop berbeda. Memberi alamat `.21` dan `.22` pada kedua laptop tidak otomatis menghubungkan jaringan itu. Karena itu tes awal memakai mock/fixture, sedangkan I-02 memasang dua peran pada satu host Windows 11 yang menjadi host integrasi.

Gunakan guest relevan yang tersedia atau guest acceptance yang memang diperlukan. Pastikan VM aktif/bukti lama tetap aman; tidak perlu membuat salinan tambahan tanpa tujuan. Deploy A dan B dari commit I-01 yang sama, siapkan satu host-only, alamat dan trust CA, lalu berikan konfigurasi privat yang sesuai.

### I-02 Menguji jalur sebenarnya

Mulai dari keadaan layanan dan data uji yang tercatat. Jalankan case secara berurutan agar bila gagal, tim dapat mengetahui bagian mana yang bermasalah.

| Case | Tindakan | Hasil yang dicari |
| --- | --- | --- |
| INT-01 | Erna membuka Source dari browser host dan membuat login benar/salah | Hasil auth sesuai; event commit dengan identitas/sequence benar |
| INT-02 | Erna mengirim dan Arhasya memeriksa record/receipt | B menyimpan event lalu membalas; A ACK sesudah receipt cocok; jumlah/identitas sesuai |
| INT-03 | Hentikan Monitor sementara pada environment uji, buat event, lalu hidupkan kembali | Event pending tetap ada; backlog pulih; tidak ada event hilang atau record ganda |
| INT-04 | Arhasya memeriksa status sumber, window dan hasil analisis | Input layak dianalisis; input belum lengkap atau model gagal mempunyai state/alasan yang benar |
| INT-05 | Erna bertindak sebagai reviewer dashboard Arhasya | Operator dapat mencari event, membuka detail dan memahami hasil/versi/kualitasnya |
| INT-06 | Tim melakukan reboot dan restore pada tujuan terisolasi | Service/IP/data pulih; backup dapat digunakan tanpa merusak data aktif |

Ketika satu case gagal, catat input, langkah dan hasilnya. Perbaikan kode dilakukan melalui PR, lalu ulangi case yang terdampak dan pemeriksaan lain yang berpotensi berubah. Perubahan commit harus tercatat agar hasil sebelum/sesudah perbaikan tidak tertukar.

Tabel ini memberi urutan awal pemeriksaan alur sistem. Acceptance penuh tetap mengikuti seluruh requirement wajib dan profil numerik/fault/security di [SRS operasi](../requirements/srs/lab-operations.md). Health HTTP 200 hanya membuktikan endpoint menjawab; delivery, analisis dan restore memerlukan bukti masing-masing.

## Tahap kelima menyusun hasil dan rilis

I-03 mengumpulkan hasil setelah I-02: commit, environment, versi OS/runtime/VMware, konfigurasi aman, hash input/model, waktu, case/requirement, expected/actual, status dan reviewer. Jika suatu kewajiban belum lulus, tulis keterbatasan atau pengecualian yang benar-benar disetujui.

Tag rilis menandai versi hasil yang diterima. Tag dibuat setelah syarat rilis dipenuhi, sehingga pengguna berikutnya dapat memilih versi yang telah diuji. Sumber panduan tetap berada di repo; PDF merupakan salinan baca yang diekspor dari versi tersebut.

Laporan Modul 5 merangkum lokasi repo, riwayat branch/merge, cuplikan git log, konflik/resolusi dan kontribusi anggota. Jika konflik dilakukan sebagai latihan, beri label latihan. Raw evidence privat tetap di luar Git. Screenshot VMware harus capture dari layar VMware; output SSH ditulis sebagai bukti terminal.
