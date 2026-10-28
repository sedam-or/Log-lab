# Panduan Arhasya menulis dan memasang Monitor

Arhasya bertanggung jawab atas penerima log serta halaman tempat operator memeriksa hasilnya. Kodenya harus menerima event sesuai kontrak, menyimpan data sebelum menjawab Source, mengelompokkan aktivitas, menghitung hasil, dan menampilkannya dengan konteks yang benar.

Beban Monitor lebih luas daripada Source. Karena itu pekerjaan dibagi menjadi ingest, analisis, inferensi, console, lalu deployment. Integrator menyiapkan training offline dan paket model. Arhasya tetap menulis loader serta jalur inferensi runtime, yaitu pemakaian model yang sudah dilatih untuk menghitung prediksi pada input baru.

Baca [dasar proyek](basics.md) dan [workspace](workspace.md) sebelum mulai. Kerjakan satu tahap lalu baca SRS yang dirujuk tahap tersebut. Source/helper dan command bootstrap belum diterbitkan; coding dimulai setelah fondasi F-04 siap.

## Gambaran perjalanan Arhasya

![Urutan task Arhasya dan ketergantungan paket model](../architecture/assets/learning/arhasya-journey.png)

[Sumber Mermaid](../architecture/assets/learning/arhasya-journey.mmd).

R-03 dapat diuji memakai fixture tanpa menunggu Source Erna. Setelah fitur R-04 diterima, integrator menggunakan fitur yang sama untuk training F-05. Sambil menunggu paket model, Arhasya dapat menulis route console yang tidak bergantung pada prediksi final. Pengujian inferensi akhir menunggu paket dan fixture prediksi tersebut.

## File yang menjadi tempat coding

| File atau direktori rencana | Fungsi yang ditulis |
| --- | --- |
| `src/loglab/monitor_app.py`, `monitor_main.py` | Endpoint ingest/status, bootstrap runtime dan route dashboard |
| `src/loglab/analysis.py` | Window, kualitas, revisi snapshot, rules dan penyimpanan hasil |
| `src/loglab/features.py` | Ekstraktor tujuh fitur; ditinjau integrator karena dipakai training dan runtime |
| `src/loglab/model.py` | Loader, pemeriksaan paket model dan inferensi |
| `tests/test_monitor_app.py`, `test_analysis.py`, `test_features.py`, `test_model.py` | Tes input, transaksi, fitur, analisis, model dan console |
| `deployment/monitor/`, `config/monitor.example.*` | Service, aturan jaringan dan konfigurasi contoh Monitor |

Nama file adalah target implementasi. Integrator mengelola schema event, helper DB/security/config, root Makefile, dependency dan training. Jika helper belum mendukung kebutuhan Monitor, jelaskan operasi yang diperlukan dalam PR bersama, beserta dampaknya pada Source. Hindari membuat versi field/validasi sendiri yang berbeda dari fixture bersama.

## R-01 Memahami penerimaan log dan memeriksa laptop

Perhatikan perjalanan event pada dasar proyek. Monitor menyimpan event sebelum menjawab receipt. Jika menjawab sukses terlebih dahulu tetapi proses mati sebelum menyimpan, Source mungkin menganggap pekerjaannya selesai padahal data hilang. Hubungan ini menjadi alasan utama urutan validasi → commit → receipt.

Tulis penjelasan singkat urutan itu, lalu catat OS/VMware, RAM dan disk host. Profil Monitor adalah 2 vCPU, RAM 2 GiB, disk dinamis 20 GiB. Task awal selesai ketika resource tercatat dan Arhasya dapat menjelaskan perbedaan “API merespons” dengan “event benar-benar tersimpan”. Requirement terkait: EP-03/EP-04 dan OP-01.

## R-02 Menyiapkan guest dan environment coding

Menunggu baseline F-04. Pasang Debian dari ISO/hash yang sama dengan Erna, gunakan VM `LogLab-Monitor-Arhasya`, akun `loglab`, dan jaringan host-only. SSH direkomendasikan untuk menempelkan perintah dari host, dengan console sebagai alternatif.

Clone ke `~/LogLab`, buat branch task dari baseline yang diberikan, lalu ikuti bootstrap Python/dependency. Periksa OS, remote repo, branch, folder dan tes fondasi. Simpan hasil aman. Jika environment atau fixture belum disediakan, laporkan dependensi agar kode berikutnya tidak ditulis berdasarkan format tebakan.

## R-03 Menulis ingest dan receipt

**Ingest** berarti proses menerima data masuk. **API** adalah cara aplikasi bertukar request dan response dengan format yang disepakati. Pada tahap ini, Arhasya membuat endpoint penerima event dan status sumber sesuai [EP-03/EP-04/EP-05/EP-07](../requirements/srs/event-pipeline.md).

Mulai di branch `feat/arhasya-ingest`. Kerjakan endpoint pada aplikasi Monitor, pemanggilan helper DB dan tes ingest. Fixture integrator menyediakan event valid, event invalid, digest dan response yang diharapkan.

### Langkah pengerjaan

1. Periksa autentikasi, sumber, ukuran dan bentuk JSON request. JSON adalah format data dengan pasangan nama/nilai; misalnya `schema_version` berisi angka versi. Ikuti batas serta field yang diterima schema bersama.
2. Periksa digest dan identitas event. Event ID menandai satu kejadian; sequence menunjukkan urutan dalam stream Source. Kedua identitas tidak boleh dipakai ulang untuk isi berbeda.
3. Simpan event dan informasi receipt dengan transaksi. Balas setelah commit berhasil. Untuk duplikat identik, kembalikan duplicate sah sesuai kontrak tanpa membuat record tambahan.
4. Untuk konflik, pertahankan record awal dan kirim error sesuai kontrak. Untuk status sumber, simpan metadata waktu/watermark; status bukan event login baru.
5. Tes sebelum menambahkan analisis. Fokus R-03 adalah perilaku penerimaan, sehingga kegagalan analisis belum boleh menghambat receipt event yang sudah tersimpan.

### Contoh dan syarat selesai

Kirim fixture event yang sama dua kali. Hasil yang diharapkan adalah satu record event pada B. Receipt kedua menunjukkan duplikat untuk identitas dan digest yang sama. Berikutnya, ubah isi tetapi gunakan ID awal; permintaan itu harus ditolak sebagai konflik dan record awal tetap utuh.

| Case | Input | Yang harus diperiksa |
| --- | --- | --- |
| R3-01 | Event valid | Record tersimpan dan receipt cocok |
| R3-02 | Event identik dikirim ulang | Satu record, receipt duplicate sah |
| R3-03 | ID/sequence konflik | Error sesuai kontrak; data awal tidak berubah |
| R3-04 | Token salah, schema/digest invalid atau payload berlebih | Ditolak pada kategori yang benar, tanpa secret pada log |
| R3-05 | Status sumber valid/invalid | Field dan watermark divalidasi; tidak menambah event login |

Kirim PR ingest setelah case tersebut dapat diulang. Pengujian ini menggunakan fixture, sehingga belum menjadi bukti koneksi dari Source sebenarnya.

## R-04 Menulis fitur, snapshot dan rules

Event tunggal memberi tahu bahwa suatu login terjadi. Untuk melihat pola, Monitor mengelompokkan event dalam rentang waktu. Rentang ini disebut **window**. Pada LogLab, window berdurasi 60 detik dengan pengelompokan sesuai source, stream dan client pada [kontrak analisis](../requirements/srs/activity-analysis.md).

**Snapshot** menyimpan kumpulan input dan metadata analisis suatu window. **Revision** adalah versi snapshot ketika membership atau kelas kualitas berubah; revisi lama tetap tersedia. **Fitur** adalah angka yang dihitung dari input, misalnya jumlah login gagal. Model dan rules memakai fitur yang sama agar hasil dapat dibandingkan.

### Mulai dari fitur yang dapat diperiksa manual

Gunakan contoh latihan berikut: satu source/stream/client dan satu akun fiktif memiliki login gagal pada detik 0, 10, 20 dan 30, kemudian login sukses pada detik 40 dalam menit yang sama. Lima event tersebut adalah input latihan, bukan evidence hasil proyek.

| Fitur | Nilai contoh | Alasannya |
| --- | --- | --- |
| `event_count` | 5 | Ada lima event unik |
| `failure_count` | 4 | Empat event login gagal |
| `success_count` | 1 | Satu login berhasil |
| `failure_ratio` | 0.8 | 4 dibagi 5 |
| `distinct_accounts` | 1 | Semua event memakai akun pseudonim yang sama |
| `max_consecutive_failures` | 4 | Empat gagal berurutan sebelum sukses |
| `active_span_seconds` | 40 | Event terakhir dikurangi waktu event pertama |

Tulis tes yang membandingkan ekstraktor terhadap nilai tersebut. Tambahkan event di batas menit untuk membuktikan bahwa waktu tepat pada akhir window masuk window berikutnya. Urutan tujuh fitur harus sama dengan kontrak; jangan mengurutkan kolom sendiri karena model membaca posisi yang telah ditetapkan.

### Lanjutkan ke kualitas dan rules

Kumpulan data belum selalu lengkap ketika window waktunya lewat. Source mungkin masih mengirim backlog. Monitor membutuhkan heartbeat, watermark dan bukti kelengkapan sesuai SRS sebelum menetapkan **READY**, yaitu input layak dianalisis.

Tulis membership/urutan, penutupan window, kualitas dan revisi. Tes window terbuka, data kosong, heartbeat usang, sequence hilang, clock offset dan event terlambat. Hasil tidak layak harus mempunyai alasan yang terlihat. Perubahan data/kualitas membuat revisi baru sesuai kontrak, bukan menghapus riwayat lama.

Setelah itu implementasikan rules. Rule adalah kondisi yang ditetapkan manusia, misalnya hitungan gagal mencapai ambang. Tes ambang 9/10 kegagalan dan 4/5 akun mengikuti aturan `REPEATED_FAILURES` dan `ACCOUNT_SWEEP`. Satu rule menyimpan alasan, versi, hitungan dan event pendukung.

Bagi R-04 menjadi PR fitur, kemudian PR snapshot/kualitas/rules agar review lebih mudah. Requirement AA-01–AA-05 selesai ketika fitur benar, input tidak lengkap ditangani jelas, revisi dapat ditelusuri, dan tes batas lulus. Integrator wajib meninjau ekstraktor sebelum memakainya untuk training F-05.

## R-05 Menulis inferensi model dan console

Training membentuk parameter model dari dataset; integrator mengerjakannya pada F-05. Inferensi memakai parameter yang sudah dibentuk untuk menghitung prediksi pada fitur baru; bagian ini ditulis Arhasya. Model bukan pengganti pemeriksaan kelengkapan data: snapshot yang belum READY belum boleh diberi label normal/suspicious.

### Bagian inferensi

Di `model.py`, tulis loader paket numerik dan pemeriksaan checksum, schema, urutan fitur serta angka. **Checksum model** membantu mendeteksi file berubah atau korup. Integrator memberikan paket, hash dan contoh prediksi yang diharapkan agar hasil runtime dapat dibandingkan dengan hasil training.

Tes paket valid, hash salah, schema tidak cocok, angka invalid dan paket hilang. Untuk input valid, bandingkan skor/label dengan fixture integrator dalam toleransi yang ditetapkan SRS. Jangan membuat target skor sendiri atau mengubah threshold supaya tes lulus. Threshold adalah batas skor untuk memilih label yang dibekukan bersama paket.

Simpan hasil yang terkait dengan revisi snapshot dan hash model. Bila paket tidak tersedia atau inferensi gagal, hasil mencatat alasan dan label kosong sesuai kontrak. Menghasilkan label normal untuk kegagalan tersebut akan memberi kesan bahwa data telah dianalisis padahal belum.

### Bagian console

Console adalah halaman web operator. Operator perlu login, mencari event, melihat detail, dan mengetahui apakah hasil analisis sudah tersedia atau data belum layak. Mulai bagian ini pada PR terpisah, misalnya `feat/arhasya-console`; route/filter dan data uji dapat dikerjakan sambil menunggu paket model.

Gunakan helper sesi/security untuk login/logout dan proteksi setiap route data. Tes pengguna tanpa sesi tidak dapat membuka data, filter invalid ditolak, pagination dibatasi, dan teks dari input di-escape sebelum dirender. **Escaping** membuat karakter input ditampilkan sebagai teks yang aman pada halaman, bukan dijalankan sebagai kode HTML.

R-05 mencakup ML-05/ML-06 serta UI-01–UI-05. Tahap selesai setelah inferensi sesuai fixture dan operator dapat menelusuri input, rules/model/version serta kualitasnya. Klaim skor dunia nyata tidak dibuat dari dataset latihan sintetis.

## R-06 Memasang Monitor sebagai service

Sesudah kode lulus tes, buat unit systemd, aturan firewall dan template konfigurasi Monitor pada scope peran. Unit systemd memberi Debian aturan menjalankan aplikasi saat boot. Firewall membatasi koneksi ke layanan sesuai profil lab.

Koordinasikan root Makefile dengan integrator agar `make setup-monitor` memakai helper umum dan file Monitor yang benar. Jalankan setup pada guest uji, ulangi setup, buka dashboard dari host melalui HTTPS, lalu reboot. Periksa kembali IP/service, event yang sudah tersimpan dan identitas paket model.

Jalankan backup konsisten dan restore terisolasi. Pulihkan pada salinan/tujuan uji sehingga data aktif tidak tertimpa. R-06 selesai ketika pemasangan/reboot/recovery dapat diulang dan sesuai bagian OP-01–OP-03/OP-06 terkait Monitor. Catat masalah konfigurasi atau kode yang masih membutuhkan perbaikan.

## R-07 Menyerahkan hasil peran

R-07 mengumpulkan PR dan bukti Monitor **sebelum** pengujian pasangan. Tulis hasil nyata pada `docs/tasks/results/arhasya.md`: case/requirement, commit, command, expected/actual, pass/fail serta masalah. File itu dibuat ketika hasil sudah ada; raw output privat disimpan di luar Git.

Catatan yang membantu reviewer menyebut kondisi, misalnya “R3-02, fixture sama dikirim dua kali, jumlah record tetap satu dan receipt kedua duplicate.” Catatan “API sudah jalan” belum menunjukkan bahwa duplikasi dicegah.

Sesudah handoff peran dan audit I-01, Arhasya ikut I-02 bersama Erna untuk menerima event dari Source sebenarnya. Periksa receipt, outage/backlog, analisis dan console pada satu host/jaringan. Hasil fixture tetap berguna, tetapi belum menggantikan uji dua VM tersebut.
