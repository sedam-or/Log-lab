> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

### 5.5 `lab-operations`

**Baseline sumber:** PRD v1.0.0. **Rincian teknis:** bagian ini. **Dependensi:** keempat modul produk.

#### Tujuan dan penerimaan

| ID | Requirement | Acceptance dan bukti |
| --- | --- | --- |
| OP-01 | Dua VM privat dapat dipasang ulang dari sumber dan konfigurasi yang tercatat. | Anggota tim mengulang install/startup pada VM bersih; dependency lock, image/hash, resource, IP, commit, dan perintah tercatat. Reboot memulihkan service dan alamat. |
| OP-02 | Transport, akses jaringan, dan secret memenuhi batas lab. | TLS/SAN/trust diperiksa; sertifikat salah atau token/sesi salah ditolak. Firewall membatasi source/host; DB tidak terbuka di jaringan. Env privat milik root berizin 0600; direktori konfigurasi root:loglab-svc 0750, private key TLS root:loglab-svc 0640, dan direktori data service 0700 menurut kontrak parameter. |
| OP-03 | Backup dapat dipulihkan menjadi data konsisten. | Backup harian dan sebelum reset/cleanup; salin ke lokasi privat di host di luar disk guest. Restore pada lokasi terisolasi lulus integrity check, rekonsiliasi event/outbox/ACK/revisi/hasil, dan penggunaan paket model yang tercatat. |
| OP-04 | Sistem memenuhi profil lab yang terukur. | Jalankan profil di bawah dan simpan hasil mentah, target, actual, serta pass/fail. Keberhasilan smoke tidak menggantikan uji gangguan/performa. |
| OP-05 | Setiap acceptance dapat dilacak dan diulang. | Manifest run mencantumkan requirement/case, commit dan dirty state, environment/config tanpa secret, input hashes, waktu, langkah, output mentah, hasil, serta reviewer. Tidak ada requirement wajib tanpa hasil/bukti pada penerimaan final. |
| OP-06 | Cleanup manual mempertahankan pekerjaan belum terkirim dan bukti yang masih diperlukan. | Cleanup hanya ketika layanan dihentikan, arsip/export dan hash telah diverifikasi, serta daftar data yang akan dibuang disetujui. Pending/held event dan dataset/evidence yang ditahan tidak ikut dihapus. |

#### Profil lingkungan baseline implementasi 1.0.0

Gunakan VMware Workstation pada host integrasi Windows 11 dan guest Debian 13 amd64 dari ISO dengan SHA-256 tercatat. Nama ISO dan checksum resmi sudah dicatat pada [kesepakatan OS](../../../config/contract.md#os-yang-diunduh). VM A (source) memakai 1 vCPU, RAM 1 GiB, dan disk dinamis 20 GiB; VM B (monitor) memakai 2 vCPU, RAM 2 GiB, dan disk dinamis 20 GiB. Profil ini menguji dua guest pada satu host, bukan dua server independen.

Gunakan VMware host-only `vmnet1`, subnet `172.16.202.0/24`, source A `172.16.202.21`, monitor B `172.16.202.22`, dan alamat adapter host `172.16.202.1`, setelah seluruh alamat diperiksa bebas. Login, ingest, source-status, dan dashboard menggunakan HTTPS pada port `8443`, TLS langsung pada Uvicorn, dan SAN sertifikat untuk alamat yang dipakai. Install CA lab pada host/browser dan trust store source. NAT boleh dipakai sementara untuk instalasi paket; sebelum acceptance matikan NAT/default route eksternal.

Catat versi SQLite yang benar-benar terhubung ke runtime Python. Bila memilih WAL, verifikasi patch [WAL-reset](https://sqlite.org/wal.html#the_wal_reset_bug) tersedia (SQLite 3.51.3+ atau backport yang terdokumentasi); alternatif journaling memerlukan verifikasi durability/konkurensi yang sama. Jangan menganggap versi paket Python menentukan versi SQLite sistem.

Admission resource: memori tersedia host pada Task Manager Windows atau MemAvailable Linux sebelum boot sekurang-kurangnya total RAM guest +2 GiB (minimal 5 GiB untuk profil ini); proyeksi ruang bebas setelah pertumbuhan disk guest, data, backup/evidence tetap ≥15% filesystem. Ukur ulang tepat sebelum provisioning. Nilai ini adalah batas operasional profil baseline; snapshot satu kali bukan bukti kinerja saat berbeban. Jika gagal, revisi profil melalui keputusan tercatat sebelum membuat VM baru.

Runtime memakai host-only; NAT sementara untuk instalasi dinonaktifkan sebelum acceptance. Source dan monitor memakai TLS, autentikasi sumber/sesi operator, verifikasi sertifikat, serta default-deny firewall. Instalasi CA lab pada client dilakukan secara eksplisit; flag untuk melewati validasi sertifikat dilarang. Aktifkan sinkronisasi waktu VMware Tools ke host dan ukur offset/ketidakpastiannya pada kedua guest. Target offset maksimal 2 detik mengikuti AA-02.

#### Profil acceptance numerik

| Pengukuran | Kondisi | Target usulan |
| --- | --- | --- |
| Delivery normal | 5 hasil auth/detik selama 10 menit; campuran berhasil/gagal | Semua accepted-local tersimpan satu kali; p95 waktu POST ingest→receipt tervalidasi ≤1 detik, memakai clock monotonic sender. |
| Pemulihan backlog | Monitor unavailable 60 detik; laju 5/detik tetap berjalan sesudah pulih | Semua accepted-local saat gangguan selesai ACK ≤120 detik sejak receiver siap; tidak ada duplikasi/record hilang. |
| Query dashboard | 20.000 event, tiga pembaca bersamaan masing-masing 1 request/detik selama 5 menit, filter dan page dibatasi UI-02 | p95 request daftar/detail ≤1 detik; hasil benar. |
| Hasil analisis | Snapshot READY, satu loop analisis | p95 seal→commit hasil ≤5 detik. Inferensi lokal p95 dan event→hasil turut dilaporkan; waktu menunggu window ditampilkan terpisah. |
| Memory aplikasi | Profil normal dan pemulihan di atas; ukur peak RSS proses aplikasi | Source ≤256 MiB, monitor ≤768 MiB; training offline diukur terpisah. Tidak ada OOM/VM hang. |
| Crash recovery | Kill sebelum/sesudah commit receiver, sesudah commit outbox, sebelum ACK source, dan sebelum/sesudah commit hasil | Rekonsiliasi ID/digest/membership berhasil; pending pekerjaan pulih atau failed eksplisit; tidak ada normal palsu. |
| Reboot/restore | Reboot setiap guest; restore DB ke lokasi terisolasi | Service/firewall aktif kembali ≤60 detik setelah OS siap. Restore lengkap ≤30 menit; target RPO backup harian ≤24 jam. |

5 event/detik, 20.000 event, dan target respons dipilih sebagai profil demonstrasi yang terbatas dan dapat diulang. Ini bukan hasil benchmark. Pilot boleh mengusulkan revisi sebelum test final; perubahan target setelah hasil final dilihat memerlukan baseline dan run baru. Throughput dihitung dari ID/revisi unik yang commit, bukan jumlah retry. Offered/accepted/rejected mengikuti EP-05; latency lintas VM disertai batas ketidakpastian jam.

#### Bukti dan recovery

Simpan evidence per `run_id`: manifest JSON, CSV latency/resource/prediksi yang relevan, hasil query rekonsiliasi, logs yang telah dibatasi dari secret, screenshot, dan ringkasan pass/fail. Source of truth hasil adalah berkas mentah dan hash yang tercatat; isi status workbook berasal dari bukti ini. Kode/schema/config yang berubah membentuk run baru.

Backup menggunakan mekanisme snapshot database yang konsisten, bukan copy file aktif secara sembarang. Simpan tujuh backup harian sukses terakhir per DB dan satu backup sebelum reset/cleanup; backup yang ditahan untuk evidence tidak dihapus sampai ekspor arsipnya diverifikasi. Proyeksi storage mencakup seluruh backup yang ditahan. Backup pada host melindungi dari kehilangan disk guest; kerusakan disk fisik host tetap di luar jaminan lab. Cleanup versi pertama bersifat manual; daemon retensi dan reference-count AI-job tidak diperlukan.

#### Verifikasi

Tes otomasi memeriksa packaging/config, rekonsiliasi, dan fault yang dapat direproduksi. Acceptance TLS/firewall/reboot/restore serta task operator berjalan di VM aktual. Langkah, task, dan bukti dicatat pada `[standar implementasi](../../architecture/standards.md)`, `[catatan migrasi](../../history/index.md)`, dan manifest run; hasil uji lama tidak dihitung sebagai hasil versi baru.

[IP, port, source ID dan nama konfigurasi yang wajib dipakai](../../interface-contracts/index.md) ditetapkan terpisah agar kedua peran memakai nilai yang sama.
