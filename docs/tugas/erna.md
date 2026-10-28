# Tugas Erna membuat aplikasi login

<a href="../../README.md"><kbd>Mulai dari README</kbd></a> <a href="../architecture/BASELINE.md"><kbd>Aturan bersama</kbd></a> <a href="../../README.md#hasil-aplikasi"><kbd>Aplikasi saat selesai</kbd></a> <a href="index.md"><kbd>Daftar tugas</kbd></a> <a href="#hasil-branch"><kbd>Hasil branch saya</kbd></a>

Erna bertanggung jawab atas aplikasi yang dipakai penguji untuk mencoba login. Selain menampilkan berhasil atau gagal, aplikasi harus menghasilkan catatan kejadian dan mengirimkannya dengan aman ke Monitor. Karena itu pekerjaan Erna mencakup kode login, penyimpanan event lokal, pengiriman, tes, dan pemasangan service di Debian.

Jika baru mulai, baca [dasar proyek](bersama.md#kenali-aplikasi-yang-dibangun) dahulu, kemudian [folder kerja dan SSH](bersama.md#folder-dan-terminal). Seluruh langkah coding di panduan ini dikerjakan pada clone guest `~/LogLab`. Aplikasi/helper belum diterbitkan di repo; tahap persiapan F-01 sampai F-04 harus menyediakan environment dan kontrak yang dibutuhkan sebelum E-02 dan coding dimulai.

## Pilih bagian

[Hasil repo saat selesai](#hasil-branch) · [Catatan hasil](#catatan-hasil)

1. [Kenali alur login dan cek laptop](#langkah-1)
2. [Siapkan Debian dan folder kerja](#langkah-2)
3. [Buat login dan simpan catatan login](#langkah-3)
4. [Kirim catatan dan tangani pengiriman ulang](#langkah-4)
5. [Pasang aplikasi agar hidup saat VM menyala](#langkah-5)
6. [Serahkan hasil pekerjaan Source](#langkah-6)

## Gambaran perjalanan Erna

![Urutan task coding dan pemasangan Erna](../architecture/assets/learning/erna-journey.png)

[Sumber Mermaid](../architecture/assets/learning/erna-journey.mmd).

Setiap tahap menghasilkan sesuatu yang dapat ditinjau. E-03 menghasilkan login dan outbox yang dapat diuji sendiri. E-04 menambahkan pengiriman menggunakan receiver uji. E-05 menyiapkan aplikasi sebagai service pada guest. E-06 menyerahkan hasil peran; setelahnya Erna ikut pengujian dua VM pada I-02.

## Hasil akhir yang harus dapat diperlihatkan

Penguji membuka Source dari browser host dan mencoba login akun fiktif. Source menghasilkan event dengan identitas tetap, menyimpannya pada database lokal, lalu sender mengirim event itu ke B. Bila B sementara tidak tersedia, event yang sudah commit tetap menunggu dan dikirim lagi setelah B pulih. Restart guest tidak menghapus pekerjaan yang belum selesai.

Requirement utama adalah [EP-01 sampai EP-07](../requirements/srs/event-pipeline.md) serta bagian [operasi](../requirements/srs/lab-operations.md) yang berkaitan dengan instalasi, keamanan dan pemulihan. EP-04 pada penerima dikerjakan Arhasya; Erna menggunakan aturan yang sama pada sender dan tes receipt.

<a id="hasil-branch"></a>

## Hasil pekerjaan Erna yang harus ada di repo

Bagian ini adalah gambaran yang dituju, bukan daftar file aplikasi yang sudah tersedia hari ini. Setelah seluruh pekerjaan Erna selesai, clone yang dipakai untuk menyerahkan hasil harus memuat fondasi dari main dan hasil Source di bawah. Karena ini satu repo bersama, file Monitor yang sudah masuk main juga boleh terlihat pada branch Erna. Tidak perlu menghapus file anggota lain untuk membuat branch terlihat khusus Source.

### Bentuk folder yang diharapkan

```text
LogLab/
├── README.md                          penjelasan proyek dari main
├── Makefile                           disiapkan bersama oleh penanggung jawab repo
├── pyproject.toml                     aturan package/Python dari main
├── requirements.lock                  daftar versi library dari main
├── src/loglab/
│   ├── __init__.py                     fondasi package dari main
│   ├── events.py                      aturan event bersama dari main
│   ├── db.py                          fungsi database bersama dari main
│   ├── config.py                      pembacaan konfigurasi dari main
│   ├── security.py                    fungsi keamanan bersama dari main
│   ├── backup.py                      fungsi backup bersama dari main
│   ├── source_app.py                  form dan route login
│   ├── source_main.py                 menjalankan aplikasi Source
│   ├── source_service.py              auth, event dan transaksi outbox
│   ├── seed_source_accounts.py        menyiapkan akun fiktif
│   └── sender.py                      kirim, receipt, retry dan status
├── tests/
│   ├── test_source.py                 tes login dan penyimpanan
│   ├── test_sender.py                 tes pengiriman dan receipt
│   └── fixtures/                      contoh uji bersama dari main
├── config/source.example.env          nama konfigurasi dan nilai contoh aman
├── deployment/source/
│   ├── setup.sh                       pemasangan peran Source
│   ├── loglab-source.service          cara systemd menjalankan Source
│   └── source.nft                     aturan firewall Source
└── docs/tugas/erna.md                  panduan ini dan catatan hasil nyata Erna
```

Pohon ini menunjukkan file yang relevan untuk Erna; folder dokumentasi dan file lain dari main tetap ikut dalam clone. Nama skrip deployment di atas menjadi target yang ditulis pada tugas ini. Bila integrator perlu menggantinya, ubah panduan serta pemanggilan Makefile bersama sebelum dianggap siap. File `source.example.env` hanya berisi contoh aman. Password/token sebenarnya, private key dan database tidak berada pada pohon yang dikirim ke GitHub.

### Apa yang harus bekerja saat diperlihatkan

| Hasil yang dituju | Cara reviewer membuktikannya | Bukti yang diserahkan |
| --- | --- | --- |
| Login benar/salah menghasilkan keputusan dan event yang sesuai | Jalankan tes E3-01/E3-02 dan coba akun fiktif dari browser host | Hasil tes serta catatan percobaan login |
| Event yang sudah commit bertahan saat aplikasi restart | Jalankan E3-04 pada database uji | ID/jumlah sebelum-sesudah restart |
| Event belum dianggap selesai jika receipt salah | Jalankan E4-02 dengan receiver uji | Expected/actual bahwa status tidak menjadi ACK |
| Retry memakai event yang sama | Simulasikan timeout dan pengiriman ulang | Identitas/digest tetap; duplicate sah tidak menambah record |
| Source bisa dipasang dan hidup lagi sesudah reboot guest | Jalankan setup, ulangi setup, reboot, periksa IP/service dan data | Command aktual, hasil service dan catatan data |
| Backup dapat dipulihkan pada tujuan terpisah | Jalankan prosedur helper backup/restore | Pemeriksaan salinan hasil restore dan masalah tersisa |

Saat pengujian sendiri, receiver uji boleh menggantikan B dan harus ditandai sebagai simulasi. Pengiriman ke VM B sebenarnya baru dinilai pada uji bersama. Jangan menunggu uji bersama untuk menyerahkan tes Source yang sudah selesai.

### Isi setiap branch dan PR

Satu branch dipakai untuk satu bagian kerja lalu digabung ke main setelah review. Jadi branch pertama belum diharapkan berisi semua Source selesai. Hasil akhir peran diperoleh dari beberapa PR yang sudah digabung; branch berikutnya mengambil main tersebut.

| Branch contoh | Perubahan yang diharapkan pada PR | Syarat sebelum meminta merge |
| --- | --- | --- |
| `feat/erna-login-outbox` | File login/service/seed dan tes Source dari langkah 3; tambah entrypoint jika diperlukan | Login, event dan transaksi lulus pemeriksaan E-03 |
| `feat/erna-sender` | `sender.py`, tes sender dan perubahan penghubung Source yang diperlukan | Receipt/retry/status lulus E-04; perubahan format bersama sudah direview |
| `feat/erna-source-deployment` | `deployment/source/*`, template Source, startup yang diperlukan, dan catatan pemasangan | Setup ulang, HTTPS, reboot dan recovery lulus E-05 |
| `docs/erna-hasil` jika diperlukan | Bagian Catatan hasil pada panduan Erna | Ada commit, command dan hasil nyata; tidak berisi credential |

Ketika membuka PR, reviewer membandingkan perubahan branch terhadap main. File fondasi yang sudah diwarisi dari main tidak dihitung sebagai kode baru Erna. Jika harus mengubah helper bersama atau root Makefile, koordinasikan PR bersama terlebih dahulu.

[Mulai mengerjakan langkah 1](#langkah-1) · [Lihat aturan Source](../requirements/srs/event-pipeline.md) · [Cara kirim PR](../../CONTRIBUTING.md)

<a id="langkah-1"></a>

## 1. Kenali alur login dan cek laptop

Nomor catatan pekerjaan: `E-01`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="bersama.md#kenali-aplikasi-yang-dibangun"><kbd>Pengenalan aplikasi</kbd></a>

Tujuan awal adalah memastikan Erna tahu apa yang akan dibuktikan. Buka diagram perjalanan event pada dasar proyek. Tulis urutan lima kejadian: hasil login ditentukan, event commit lokal, sender mengirim, B memberi receipt, dan A menyimpan ACK. Jelaskan mengapa event yang belum mendapat receipt tetap berada di antrean.

Di host, catat OS, versi VMware, RAM dan ruang disk tersedia. Profil Source adalah 1 vCPU, RAM 1 GiB dan disk dinamis 20 GiB; host juga membutuhkan resource untuk OS-nya sendiri. Catatan resource dipakai untuk memeriksa apakah instalasi layak, bukan dianggap sebagai bukti kinerja aplikasi.

Hasil E-01 berupa catatan singkat prasyarat dan alur yang akan dibuat. Task selesai setelah integrator dapat melihat resource yang tersedia dan pemahaman Erna tentang urutan event/receipt. Requirement terkait: EP-01–EP-03 dan OP-01.

[Kembali ke hasil yang dituju](#hasil-branch) · [Aturan bersama](../architecture/BASELINE.md) · [Lanjut ke langkah 2](#langkah-2)

<a id="langkah-2"></a>

## 2. Siapkan Debian dan folder kerja

Nomor catatan pekerjaan: `E-02`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="bersama.md#folder-dan-terminal"><kbd>Panduan folder dan SSH</kbd></a>

Tahap ini menunggu baseline F-04. Integrator memberikan ISO/hash, versi dependency, helper, fixture, dan command bootstrap. Pasang Debian sesuai acuan pada VM `LogLab-Source-Erna`, siapkan akun `loglab`, jaringan, serta SSH jika ingin mengerjakan terminal dari host.

Ikuti [workspace](bersama.md#folder-dan-terminal) untuk clone ke `~/LogLab`. Buat branch task dari baseline yang diberikan, kemudian jalankan bootstrap environment. **Environment** di sini berarti Python beserta library yang diperlukan agar kode kedua anggota dijalankan pada versi yang sama.

Periksa empat hasil: guest memakai Debian yang ditetapkan, repo remote benar, branch kerja benar, dan tes fondasi dari integrator dapat dijalankan. Simpan output yang relevan tanpa credential. Jika command bootstrap belum tersedia, laporkan sebagai blocked F-03/F-04; tugas coding berikutnya belum dapat dinilai dengan environment yang sesuai.

[Kembali ke hasil yang dituju](#hasil-branch) · [Aturan bersama](../architecture/BASELINE.md) · [Lanjut ke langkah 3](#langkah-3)

<a id="langkah-3"></a>

## 3. Buat login dan simpan catatan login

Nomor catatan pekerjaan: `E-03`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="../requirements/srs/event-pipeline.md"><kbd>Aturan catatan login</kbd></a>

Tujuannya adalah merekam hasil login sebelum pekerjaan pengiriman dimulai. Fokus pada EP-01, EP-02 dan EP-05. Mulai dari branch `feat/erna-login-outbox`; kerjakan aplikasi/service Source, seed akun dan `tests/test_source.py`.

### Langkah pengerjaan

1. Gunakan helper security untuk menyimpan hash password akun fiktif. **Hash password** adalah nilai turunan untuk pemeriksaan password, sehingga penyimpanan akun tidak memerlukan password mentah. Fungsi seed hanya menambah akun yang diperlukan dan aman dijalankan ulang.
2. Tulis route login yang menerima input form, memeriksa akun dan menghasilkan keputusan berhasil/gagal. Pisahkan keputusan autentikasi dari detail pengiriman ke Monitor agar login tidak menunggu jaringan A–B.
3. Gunakan pembentuk event bersama untuk membuat field sesuai schema. Field adalah nama data seperti `event_id` atau `occurred_at`; schema menetapkan tipe, format dan batas yang diizinkan. Akun/client dalam event memakai pseudonim sesuai kontrak, bukan identitas nyata.
4. Simpan event, sequence dan counter terkait pada transaksi lokal. **Transaksi** adalah kelompok perubahan database yang harus berhasil bersama atau dibatalkan bersama. Event dianggap diterima lokal setelah commit berhasil. Ikuti penanganan kegagalan enqueue pada SRS tanpa mengubah keputusan autentikasi hanya karena Monitor sedang mati.
5. Tulis tes skenario di bawah, lalu buka PR pertama. Reviewer harus dapat melihat pemisahan input form, keputusan auth dan transaksi pencatatan.

### Contoh yang diperiksa

Contoh ini adalah rencana pengujian, bukan hasil run. Penguji melakukan satu login benar dan satu login salah dengan akun fiktif. Jika kedua transaksi pencatatan berhasil, outbox memiliki dua event dengan ID berbeda, jenis `login.success`/`login.failure` yang sesuai, dan sequence yang naik. Kedua event tidak memuat password.

| Case | Cara memeriksa | Hasil yang diharapkan |
| --- | --- | --- |
| E3-01 | Password benar pada akun fiktif | Auth berhasil dan satu event success tercatat |
| E3-02 | Password salah | Auth gagal dan satu event failure tercatat |
| E3-03 | Simulasikan transaksi outbox gagal | Tidak ada event setengah jadi atau sequence yang dianggap commit; counter/penanganan gagal sesuai kontrak |
| E3-04 | Baca ulang DB setelah proses Source dihentikan dan dimulai | Event yang telah commit tetap ada |
| E3-05 | Jalankan seed akun dua kali | Akun tidak terduplikasi dan credential yang sudah ditetapkan tidak tertimpa sembarangan |

Gunakan database sementara pada tes, bukan database aktif yang dipakai demonstrasi. Task selesai ketika hasil auth, isi event, sequence dan durability sesuai tes. **Durability** berarti data yang sudah commit tetap tersedia sesudah proses berhenti. Pengiriman ke B masih dikerjakan pada E-04.

[Kembali ke hasil yang dituju](#hasil-branch) · [Aturan bersama](../architecture/BASELINE.md) · [Lanjut ke langkah 4](#langkah-4)

<a id="langkah-4"></a>

## 4. Kirim catatan dan tangani pengiriman ulang

Nomor catatan pekerjaan: `E-04`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="../requirements/srs/event-pipeline.md"><kbd>Aturan pengiriman dan jawaban</kbd></a>

Tujuan tahap ini adalah memindahkan event dari antrean A ke penyimpanan B tanpa menghitung ulang kejadian yang sama. Requirement: EP-03, EP-06, EP-07 dan kesesuaian API EP-04. Mulai dari main yang sudah berisi E-03 melalui branch `feat/erna-sender`. Integrator menyediakan receiver uji dan fixture receipt.

### Memahami receipt sebelum menulis kode

Anggap event di outbox mempunyai ID latihan `evt-1`. Nama ini hanya penyederhanaan penjelasan; event sebenarnya wajib memakai UUID sesuai schema. Bila receiver menjawab receipt untuk event lain, misalnya `evt-2`, sender tidak boleh menyelesaikan event `evt-1`. Di kode nyata, periksa `source_id`, `event_id` dan `event_digest`, bukan hanya status HTTP.

**Digest** adalah sidik jari isi event. Pemeriksaan digest membantu memastikan receipt merujuk isi yang sama. Helper bersama harus menghitung digest dengan cara yang sama pada Source dan Monitor.

### Langkah pengerjaan

1. Pilih event pending dari outbox. Pending berarti telah tersimpan tetapi belum mendapat ACK lokal. Pastikan hanya satu sender aktif untuk database yang sama.
2. Kirim event melalui endpoint dan TLS/auth sesuai kontrak. Baca CA dan token dari konfigurasi privat; identitas event serta payload tetap sama pada setiap retry.
3. Jika receipt cocok, commit perubahan status lokal menjadi ACKNOWLEDGED. Jika timeout atau response sementara terjadi, simpan pekerjaan untuk retry sesuai backoff/timeout SRS.
4. Untuk response permanen seperti konflik/invalid, tahan event beserta alasan aman untuk diperiksa. Menahan event berbeda dari menghapusnya.
5. Kirim status sumber secara periodik. **Watermark ACK kontigu** berarti sequence tertinggi yang seluruh sequence sebelumnya sudah ACK. Jika sequence 1 dan 3 ACK tetapi 2 belum, watermark belum boleh meloncat ke 3.

### Pemeriksaan dan hasil

| Case | Kondisi | Hasil yang diharapkan |
| --- | --- | --- |
| E4-01 | Receipt dengan source/event/digest cocok | ACK disimpan pada Source |
| E4-02 | Receipt salah satu fieldnya tidak cocok | Event tidak dianggap selesai |
| E4-03 | Receiver timeout, 429 atau 5xx | Retry mengikuti aturan; ID/payload tidak berubah |
| E4-04 | Event dikirim ulang setelah receipt pertama hilang | Receiver mengembalikan duplicate sah; tidak ada record kedua |
| E4-05 | Proses berhenti sebelum/sesudah ACK | Pekerjaan dapat dipulihkan dari database sesuai titik commit |
| E4-06 | Ada lubang ACK sequence | Status mengirim watermark kontigu yang benar |

Tes memakai receiver uji, sehingga tulis dengan jelas bahwa B asli belum terlibat. Kirim PR sesudah tes sender dapat ditinjau. E-04 selesai ketika pengiriman, receipt, retry, restart dan status sumber memenuhi kontrak pada skenario tersebut.

[Kembali ke hasil yang dituju](#hasil-branch) · [Aturan bersama](../architecture/BASELINE.md) · [Lanjut ke langkah 5](#langkah-5)

<a id="langkah-5"></a>

## 5. Pasang aplikasi agar hidup saat VM menyala

Nomor catatan pekerjaan: `E-05`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="../requirements/srs/lab-operations.md"><kbd>Aturan pemasangan dan pemulihan</kbd></a>

Ketika kode sudah lulus tes, aplikasi perlu dapat berjalan tanpa bergantung pada terminal coding. Program latar belakang yang dikelola OS disebut **service**. Debian menggunakan systemd untuk menyalakan, menghentikan, dan memulai service saat boot.

Erna membuat unit service dan aturan jaringan Source di `deployment/source/`, serta template nilai contoh pada `config/`. Integrator mengurus wrapper Makefile dan helper umum; koordinasikan target `make setup-source` agar root Makefile tidak diubah berbeda pada dua branch. Target itu belum tersedia sampai task ini diimplementasikan dan diperiksa.

Jalankan setup pada environment uji yang sesuai. Buka Source dari browser host melalui HTTPS dengan CA lab yang dipercaya. Ulangi setup untuk memeriksa bahwa akun/service tidak ganda dan secret/data tidak tertimpa. Kemudian restart dan reboot guest; catat apakah IP, service serta data tetap benar.

Backup database harus memakai prosedur konsisten yang diberikan helper, kemudian dipulihkan pada lokasi terisolasi. Database aktif tidak ditimpa untuk latihan. Task ini memenuhi bagian OP-01/OP-02/OP-03/OP-06 yang terkait Source dan selesai setelah prosedur instalasi ulang, startup dan recovery dapat diulang reviewer.

[Kembali ke hasil yang dituju](#hasil-branch) · [Aturan bersama](../architecture/BASELINE.md) · [Lanjut ke langkah 6](#langkah-6)

<a id="langkah-6"></a>

## 6. Serahkan hasil pekerjaan Source

Nomor catatan pekerjaan: `E-06`. Gunakan nomor ini ketika menulis PR atau hasil tes.

<a href="../../CONTRIBUTING.md"><kbd>Cara menyerahkan PR</kbd></a>

E-06 mengumpulkan hasil Erna **sebelum** uji dua VM. Isinya adalah PR task yang sudah direview, daftar file, case/requirement, commit, command, expected/actual, pass/fail, dan masalah tersisa. Tulis ringkasan aman di [Catatan hasil](#catatan-hasil) saat hasil nyata sudah tersedia; simpan raw evidence privat di luar Git.

Contoh catatan yang berguna: “E4-02 pada commit tertentu, receiver uji memberi digest berbeda, event tetap pending; hasil pass.” Catatan “sender sudah bisa” terlalu umum karena reviewer tidak tahu kondisi yang dibuktikan. Screenshot yang disebut layar VMware harus berasal langsung dari VMware; output SSH adalah bukti terminal.

Sesudah hasil peran diserahkan, integrator melakukan audit I-01. Erna lalu ikut I-02 bersama Arhasya untuk mengirim ke Monitor sebenarnya dan membuktikan backlog/ACK pada satu jaringan. Dengan urutan ini, E-06 tidak bergantung pada I-02 yang belum dimulai.

<a id="catatan-hasil"></a>

## Catatan hasil

Bagian ini belum berisi hasil run. Setelah mengerjakan task, isi tabel dengan hasil nyata dan sebutkan commit yang diperiksa. Kata “Belum” di bawah tidak boleh diganti menjadi lulus sebelum tes dijalankan. Simpan output mentah privat di luar Git, lalu tautkan ringkasan aman atau PR yang relevan.

| Langkah atau case | Commit yang diuji | Perintah atau tindakan | Hasil yang diharapkan | Hasil nyata dan bukti aman | Status |
| --- | --- | --- | --- | --- | --- |
| Belum diisi | Belum | Belum | Ikuti case pada langkah terkait | Belum ada hasil | Belum diuji |

Sebelum meminta review akhir, pastikan file pada target repo tersedia, pemeriksaan peran lulus atau keterbatasannya tertulis, dan perubahan bersama telah direview. Daftar PR menunjukkan bagian yang ditulis sendiri dan bagian yang menggunakan ulang sumber lama.

<a href="../../README.md"><kbd>Mulai dari README</kbd></a> <a href="../architecture/BASELINE.md"><kbd>Aturan bersama</kbd></a> <a href="../../README.md#hasil-aplikasi"><kbd>Aplikasi saat selesai</kbd></a> <a href="index.md"><kbd>Daftar tugas</kbd></a> <a href="#hasil-branch"><kbd>Hasil branch saya</kbd></a>


[Lihat cara menguji dua VM bersama](bersama.md#menyatukan-pekerjaan).
