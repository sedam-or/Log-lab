# Fondasi dan integrasi kedua VM

Integrator menyiapkan fondasi bersama dan menjaga perjalanan dari dua pekerjaan anggota menjadi satu sistem yang dapat diulang. Menggabungkan PR menggabungkan file/riwayat; itu tidak otomatis menyatukan dua VM pada dua laptop. Penerimaan akhir harus menguji dua peran yang dipasang dari commit sama dalam jaringan yang dapat saling terhubung.

## F-01 sampai F-04 Sebelum coding paralel

| Task | Tindakan integrator | Selesai ketika |
| --- | --- | --- |
| F-01 | Review adaptasi PRD, SRS, istilah, diagram, dan host Windows. Tetapkan requirement yang dipakai dan tandai usulan yang belum aktif. | Review tercatat, tidak ada kontrak saling bertentangan atau status lama yang diklaim baru |
| F-02 | Pilih ISO resmi+SHA-256, Python/dependency lock, daftar modul dan pemilik file, schema dan fixture event/receipt/status. Tetapkan feature schema, rubrik data dan pipeline training; paket model final disiapkan setelah implementasi fitur R-04 diterima. Tetapkan bootstrap akun serta pembagian secret lewat jalur privat. | Kedua anggota memakai input yang sama dan tahu siapa mengurus bagian bersama |
| F-03 | Migrasikan atau tulis skeleton paket, runner tes dan helper bersama (`events.py`, `config.py`, `db.py`, `security.py`, `backup.py`). Source/Monitor tidak disalin sebagai peran selesai: Erna dan Arhasya menulis implementasinya melalui task coding. Ubah path `deploy/` menjadi `deployment/` dan hapus ketergantungan path/symlink host lama. Sediakan bootstrap environment, runner tes, kontrak wrapper setup per peran, receiver uji untuk Erna, fixture producer untuk Arhasya, serta helper backup/restore. Skrip deployment aplikasi diselesaikan oleh pemilik peran pada E-05/R-06. | Environment dasar dan bootstrap dicoba pada Debian target; wrapper setup/tes memiliki interface jelas. Acceptance aplikasi penuh menunggu kode kedua peran |
| F-04 | Periksa pengaturan main/PR, catat SHA commit baseline, isi semua placeholder panduan, dan render PDF peran dari sumber Markdown. | Erna dan Arhasya menerima versi panduan, ISO/hash, command dan baseline yang sama |

Erna dan Arhasya menulis kode perannya, unit tests, dan deployment. Integrator bertanggung jawab atas helper/kontrak/dependency bersama serta dataset, training dan evaluasi ML-01–ML-04. Arhasya menulis ekstraktor fitur dengan review integrator, analisis, inferensi dan console. Setelah fitur R-04 diterima, integrator menghasilkan paket model dan fixture prediksi untuk R-05. Urutan ini mencegah dua ekstraktor berbeda dan menjaga beban tugas tetap terbagi. Jangan memberikan kode peran lama sebagai hasil kontribusi anggota tanpa menyatakan bagian yang digunakan ulang.

## F-05 Paket model setelah fitur disepakati

Sesudah R-04 masuk main, integrator menyiapkan atau mengadaptasi `dataset.py`, `generate_dataset.py`, `training.py`, dan `train_model.py` bersama tests dataset/training. Gunakan feature schema yang sama dengan runtime, data sintetis, rubrik label yang ditinjau, split per run, konfigurasi/seed tercatat dan pembandingan terhadap rules serta baseline sesuai ML-01–ML-04. Simpan provenance, checksum, schema, urutan fitur, expected prediction, dan batas klaim. Berikan paket melalui sumber distribusi yang dipatok hash; jangan menaruh eksperimen besar atau secret dalam repo.

F-05 menunggu fitur R-04, tetapi tidak menahan Erna menulis sender atau Arhasya memulai route console. R-05 inferensi final menunggu paket ini. Review label independen dan metrik yang belum tersedia ditandai sebagai keterbatasan, tidak diisi dari angka laporan lama.

## I-01 Integrasi perubahan Git

1. Erna dan Arhasya mengirim PR kecil per task. Setiap PR menunjuk requirement dan hasil perannya. Review file bersama sebelum merge.
2. Reviewer memeriksa scope, output verifikasi dan secret. Merge PR pertama ke `main` dengan merge commit sesuai kebijakan repo.
3. Pemilik PR kedua menjalankan `git fetch origin` dan `git merge origin/main` pada branch-nya. Periksa/resolusikan konflik jika ada, jalankan ulang checks terdampak, lalu push tanpa force.
4. Review kembali perubahan setelah sinkronisasi, merge PR kedua, lalu catat SHA `main` untuk uji gabungan. Command yang mengeksekusi tests mengikuti runner yang sudah benar-benar tersedia; belum ada CI aktif yang boleh diklaim lulus.

Jika kontrak berubah, proses berhenti pada koordinasi file bersama sampai producer dan consumer cocok. Konflik teks kosong tidak cukup untuk menganggap API kompatibel. Latihan konflik Modul 5 dilakukan pada branch latihan/dokumen aman jika tidak ada konflik alami, dan ditandai sebagai latihan.

## I-02 Integrasi runtime pada satu host

Pilih host integrasi Windows 11 dengan VMware Workstation. Pakai guest relevan yang tersedia, atau guest bersih yang memang disiapkan untuk acceptance; jangan menghapus VM aktif atau membuat salinan tambahan tanpa tujuan. Kedua VM berada pada host-only yang sama. Jaringan host-only pada laptop Erna dan laptop Arhasya berbeda meskipun subnetnya sama; koneksi langsung antarlaptop tidak menjadi asumsi.

Pasang peran Source dan Monitor dari SHA hasil I-01. Konfigurasi alamat A `.21`, B `.22`, host `.1` pada subnet baseline yang telah diperiksa bebas. Pasang trust CA dan secret yang cocok secara privat. A harus memverifikasi sertifikat B; tidak memakai bypass TLS. Salinan disk VM boleh menjadi alat bantu transfer, tetapi sumber Git dan konfigurasi terdokumentasi tetap dasar pemasangan ulang.

| Case | Siapa mengerjakan | Pemeriksaan dan syarat lulus |
| --- | --- | --- |
| INT-01 | Erna + integrator | Host membuka Source melalui HTTPS; login berhasil/gagal menghasilkan event dengan sequence/digest sesuai EP-01/EP-02 |
| INT-02 | Erna + Arhasya | Sender A mengirim ke B sebenarnya; B menyimpan lalu mengembalikan receipt; A ACK hanya sesudah receipt cocok; ID/jumlah cocok di kedua sisi (EP-03/EP-04) |
| INT-03 | Keduanya | Hentikan layanan Monitor sementara pada lingkungan uji, tetap lakukan login. Pulihkan dan buktikan backlog terkirim tanpa duplikasi/kehilangan; identitas event dipertahankan (EP-05/EP-06) |
| INT-04 | Arhasya + integrator | Status sumber segar, kualitas window dan rules benar; input READY dianalisis, data ineligible/model gagal tidak berlabel normal; versi/hash model terlihat (EP-07, AA, ML-05/06) |
| INT-05 | Arhasya + Erna sebagai reviewer | Login operator, filter dan detail event/hasil bekerja. Reviewer dapat menelusuri aktivitas login ke evidence (UI-01–UI-05) |
| INT-06 | Keduanya + integrator | Reboot masing-masing guest, verifikasi IP/service/data; uji backup/restore terisolasi dan keamanan jaringan/TLS (OP-01–OP-03) |

Tabel ini adalah urutan smoke integrasi, bukan pengganti semua profil numerik/fault/security pada [operasi SRS](../requirements/srs/lab-operations.md). Penerimaan final harus mencantumkan semua requirement wajib beserta hasil, pengecualian yang diterima, atau alasan belum lulus.

## I-03 Handoff dan laporan

Catat commit, versi Windows/VMware/Debian/Python, konfigurasi non-secret, hash model/input, waktu, case/requirement, langkah, expected/actual, pass/fail, serta reviewer. Raw evidence tetap privat; repo memuat ringkasan aman dan sumber editable. Screenshot yang diberi label VMware berasal langsung dari layar VMware; SSH output adalah bukti terminal.

Rilis/tag hanya dibuat setelah acceptance disetujui dan keterbatasannya tertulis. Dokumentasi akhir menyertakan cara clone/setup per peran, startup/shutdown guest, SSH opsional, health dan log, backup/restore, serta pemulihan gangguan. PDF Modul 5 merangkum lokasi repo, graph/log, branch/merge, konflik/resolusi, dan kontribusi aktual Erna/Arhasya; tidak menampilkan hasil dari laptop lama sebagai pekerjaan mereka.
