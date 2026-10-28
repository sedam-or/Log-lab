# Panduan Erna untuk kode dan VM A Source

Erna menulis kode Source, mengujinya, lalu memasangnya di VM Debian miliknya. Source adalah aplikasi login fiktif yang menyimpan event secara lokal sebelum mengirimkannya ke Monitor. Hasil kerja mencakup kode, tes, konfigurasi deployment, dan bukti; memasang VM saja belum menyelesaikan tugas.

Baca [workspace](workspace.md), [istilah](../requirements/srs/terms.md), dan [kontrak event](../requirements/srs/event-pipeline.md). Panduan ini adalah draf pembagian coding yang sudah memasukkan arahan pemilik. Command final untuk bootstrap/dependency ditambahkan setelah F-04; kode lama dapat menjadi referensi yang disanitasi, bukan dianggap sudah tersedia di repo.

## Workspace dan file milik Erna

VM: `LogLab-Source-Erna`. Clone di guest: `~/LogLab`. Buat branch dari main baseline per PR, misalnya `feat/erna-login-outbox` dan `feat/erna-sender`. Branch adalah jalur perubahan Git; Erna tetap bekerja di folder clone yang sama.

| File yang direncanakan | Yang ditulis Erna |
| --- | --- |
| `src/loglab/source_app.py`, `source_main.py` | Route/form login, bootstrap runtime Source, pemanggilan domain |
| `src/loglab/source_service.py` | Keputusan login dan pencatatan outbox/counter/sequence dengan transaksi |
| `src/loglab/seed_source_accounts.py` | Pembuatan akun fiktif yang aman dijalankan ulang |
| `src/loglab/sender.py` | Satu sender, POST event, validasi receipt, retry, dan status sumber |
| `tests/test_source.py`, `tests/test_sender.py` | Login, commit, receipt, retry dan restart Source |
| `deployment/source/`, `config/source.example.*` | Service, firewall, dan template konfigurasi tanpa secret untuk peran A |
| `docs/tasks/results/erna.md` | Ringkasan hasil aktual dan masalah Erna |

File di atas belum diimplementasikan di repo baru. Jangan membuat salinan `events.py`, `db.py`, `config.py`, atau `security.py` khusus Erna. Interface bersama disiapkan integrator pada F-02/F-03. Jika helper belum cukup, ajukan kebutuhan melalui PR bersama sebelum mengubahnya.

## E-01 Pahami alur dan periksa laptop

**Tujuan:** Erna dapat menjelaskan alur login → commit outbox → kirim → receipt → ACK tanpa mengandalkan Monitor selalu hidup. **Requirement:** EP-01–EP-03, OP-01. Di host, catat OS/VMware/resource dan profil A: 1 vCPU, 1 GiB RAM, disk dinamis 20 GiB. Baca field event serta aturan sequence/digest. Serahkan ringkasan alur dan catatan prasyarat di hasil Erna; jangan mencantumkan secret. Selesai bila alur dipahami dan resource diperiksa.

## E-02 Siapkan guest dan environment coding

**Dependensi:** baseline F-04. Pasang Debian dari ISO/hash yang diberikan, akun `loglab`, jaringan host-only, lalu SSH opsional sesuai [workspace](workspace.md). Clone Git di guest, buat branch dari SHA baseline, dan pasang environment menggunakan command bootstrap yang diterbitkan integrator.

Periksa OS/Python, remote Git, branch, working directory, dan tes fondasi. Hasilnya adalah guest untuk coding yang memakai kontrak/dependency sama dengan Arhasya. Tidak perlu menyalin file dengan clipboard VMware. Jika bootstrap belum tersedia, laporkan dependensi F-03, bukan menebak versi paket.

## E-03 Tulis login dan outbox

**Tujuan:** setiap hasil autentikasi tercatat sekali dengan identitas stabil. **Requirement:** EP-01/EP-02/EP-05. **File:** aplikasi, service Source, seed akun dan tes Source pada tabel di atas. **Input:** schema event, helper DB/security, dan fixture integrator.

1. Seed akun fiktif dengan hash password melalui helper; pemanggilan ulang tidak menduplikasi akun.
2. Tulis handler login dan hasil berhasil/gagal. Jangan log password atau mengambil nama/IP nyata sebagai isi event.
3. Pada transaksi lokal, tetapkan event ID/sequence, tulis event outbox dan counter sesuai kontrak. Jawaban login tidak menunggu pengiriman ke Monitor.
4. Tambahkan tes login benar/salah, commit gagal, counter, sequence, serta pembacaan kembali setelah restart. Gunakan `test_*` dan runner fondasi, bukan tes yang hanya memeriksa HTTP 200.
5. Ajukan PR `feat/erna-login-outbox` dengan requirement, hasil tes, dan contoh event aman.

**Lulus:** hasil auth benar; event mematuhi schema/digest; commit sukses menghasilkan event durable; kegagalan commit tercatat tanpa sequence palsu. Reviewer dapat mengulang tes. Aplikasi belum harus terkoneksi ke B pada tahap ini.

## E-04 Tulis sender dan status sumber

**Requirement:** EP-03/EP-06/EP-07, sisi Source EP-04. **File:** `sender.py`, tes sender, penyesuaian bootstrap Source. **Input:** receiver uji dan fixture receipt integrator. Mulai branch baru setelah E-03 masuk main, atau nyatakan dependensi PR jika belum masuk.

Baca event pending dari outbox, kirim melalui HTTPS dengan CA/token konfigurasi, lalu bandingkan source/event/digest pada receipt sebelum commit ACK. Terapkan satu sender, backoff/timeout, status permanen yang ditahan, serta heartbeat/watermark kontigu sesuai SRS. Retry mempertahankan ID dan payload; jangan menghapus pekerjaan hanya karena timeout.

Tes receipt cocok/tidak cocok, token/error permanen, timeout/429/5xx, duplicate, restart sebelum/sesudah ACK, serta status sumber. Gunakan mock yang berlabel dan tidak mengubah kontrak. **Lulus:** event tetap aman sampai ACK sah, tidak ada sender ganda, status/watermark benar, dan backlog pulih pada uji terisolasi. Kirim PR `feat/erna-sender`.

## E-05 Buat deployment dan periksa recovery

**Requirement:** OP-01/OP-02/OP-03/OP-06. Buat konfigurasi service, firewall dan template Source pada scope sendiri. Integrator menyediakan wrapper Makefile dan helper umum; koordinasikan target `make setup-source` agar tidak menulis Makefile root bersamaan dengan Arhasya.

Jalankan setup Source, periksa dari browser host, restart dan reboot guest, serta backup/restore terisolasi sesuai helper yang diberikan. Konfigurasi alamat harus dapat diubah dan tidak bergantung nomor interface/symlink laptop lain. Pemanggilan setup ulang tidak menimpa secret atau data. Jangan `cp` DB aktif atau membersihkan pending event untuk memaksa hasil lulus. Kirim PR `feat/erna-source-deployment`.

**Lulus:** service/IP kembali, HTTPS dipercaya, data tidak hilang, firewall membatasi akses, dan instruksi dapat diulang dari repo. Catat kegagalan yang belum selesai.

## E-06 Serahkan hasil dan ikut integrasi

Tulis hasil per case: task/requirement, commit, lokasi terminal, command, expected/actual, pass/fail, dan masalah. File privat tetap di luar Git. Screenshot yang disebut layar VMware harus capture VMware asli; output SSH adalah bukti terminal.

Sesudah PR peran masuk, Erna ikut [integrasi](integration.md) bersama Arhasya: mengirim event dari A nyata ke B nyata, menguji outage dan retry, serta merekonsiliasi record/ACK. Mock yang lulus belum menjadi acceptance pasangan. Peran selesai setelah tes Source, deployment dan bukti lolos review, serta hasil integrasi yang terkait sudah dicatat.
