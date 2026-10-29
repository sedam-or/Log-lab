# Kesepakatan kedua VM

[Kembali ke README](../README.md) · [Erna](../docs/tugas/erna.md) · [Arhasya](../docs/tugas/arhasya.md)

Ini versi untuk dibaca anggota tim. Kamu tidak perlu memahami JSON untuk mengikuti kesepakatan ini. Isi halaman dibuat otomatis dari contract.json, sehingga isinya harus sama dengan aturan yang dipakai alat pemeriksa.

**Versi aturan: 1.0.0.** Perubahan alamat/nama tidak dilakukan sendiri oleh satu anggota.

## Apa yang kita hubungkan

Erna membuat aplikasi login pada VM A. Arhasya membuat penerima dan halaman pemantauan pada VM B. Saat diuji bersama, dua VM berada pada satu laptop/PC Windows 11 dengan VMware. SSH memudahkan penggunaan terminal dari host; data aplikasi dikirim melalui HTTPS.

| Aturan bersama | Nilainya |
| --- | --- |
| Jaringan privat VMware | `172.16.202.0/24` pada `VMnet1` |
| Alamat host | `172.16.202.1`; bukan default gateway internet |
| Port aplikasi / terminal SSH | `8443` / `22` |
| User Debian / user service | `loglab` / `loglab-svc` |
| Folder kode pada masing-masing VM | `/home/loglab/LogLab` |
| Nama sumber catatan | `login-lab-a` |

## Erna mengerjakan aplikasi login

| Yang perlu disamakan | Nilai yang dipakai |
| --- | --- |
| Nama VM di VMware | `LogLab-Source-Erna` |
| Nama mesin Debian | `loglab-source` |
| Alamat IP | `172.16.202.21` |
| Alamat web | `https://172.16.202.21:8443` |
| Service yang akan dibuat | `loglab-source.service` |
| File konfigurasi privat | `/etc/loglab/source.env` |
| File database lokal | `/var/lib/loglab/source.sqlite3` |
| RAM / CPU / disk guest | `1024 MiB` / `1 vCPU` / `20 GiB` |
| Contoh konfigurasi aman | [source.example.env](source.example.env) |

## Arhasya mengerjakan aplikasi pemantauan

| Yang perlu disamakan | Nilai yang dipakai |
| --- | --- |
| Nama VM di VMware | `LogLab-Monitor-Arhasya` |
| Nama mesin Debian | `loglab-monitor` |
| Alamat IP | `172.16.202.22` |
| Alamat web | `https://172.16.202.22:8443` |
| Service yang akan dibuat | `loglab-monitor.service` |
| File konfigurasi privat | `/etc/loglab/monitor.env` |
| File database lokal | `/var/lib/loglab/monitor.sqlite3` |
| RAM / CPU / disk guest | `2048 MiB` / `2 vCPU` / `20 GiB` |
| Contoh konfigurasi aman | [monitor.example.env](monitor.example.env) |

## Cara kedua aplikasi berbicara

Saat coding awal, gunakan data contoh dan receiver simulasi. Tabel berikut adalah jalur HTTPS yang harus dibuat untuk aplikasi akhir. Method GET berarti membaca halaman; POST berarti mengirim data.

| Kebutuhan | Dikerjakan pada | Method dan jalur |
| --- | --- | --- |
| Membuka halaman login | Erna | `GET /login` |
| Mengirim form login | Erna | `POST /login` |
| Mengirim login dari alat uji JSON | Erna | `POST /api/v1/login` |
| Mengirim satu catatan login | Arhasya | `POST /api/v1/events` |
| Mengirim kondisi antrean Source | Arhasya | `POST /api/v1/source-status` |
| Membuka halaman pemantauan operator | Arhasya | `GET /` |
| Memeriksa proses hidup | Kedua VM | `GET /health` |

Login form dan JSON memakai username/password akun fiktif. Pengiriman event/status memakai token pasangan. Dashboard memerlukan sesi operator. Monitor menjawab event yang sudah disimpan dengan stored, atau duplicate bila identitas dan isi yang sama sudah tersimpan. Source hanya menganggap selesai setelah source_id, event_id dan digest pada jawaban cocok.

Pada demonstrasi, host boleh membuka web/SSH kedua VM. Source boleh mengirim HTTPS ke Monitor, tetapi tidak diberi akses SSH ke Monitor. Database tidak membuka port jaringan. NAT dimatikan saat acceptance; jaringan host-only dua laptop terpisah tidak otomatis saling terhubung.

## Akun uji, model dan file pendukung

| Yang dipakai | Kesepakatan |
| --- | --- |
| Username login uji di Source | `demo-user-01`, `demo-user-02` |
| Username dashboard | `operator` |
| Daftar akun privat Source | `/etc/loglab/test-accounts.json` |
| Model klasifikasi | `LogisticRegression`, seed `42`; dilatih offline |
| Format event / fitur / rules | `1` / `login-window-v1` / `rules-v1` |
| Waktu catatan | `UTC` |
| Model dan checksum di Monitor | `/var/lib/loglab/model.json` dan `/var/lib/loglab/model.json.sha256` |
| Backup lokal pada masing-masing VM | `/var/backups/loglab/daily.sqlite3` |
| CA publik / sertifikat / private key | `/etc/loglab/ca.crt` / `/etc/loglab/tls.crt` / `/etc/loglab/tls.key` |

Path yang sama pada dua VM menunjuk disk masing-masing, bukan folder bersama. Model akhir diserahkan integrator setelah fitur Arhasya diterima. Password akun uji dan operator disiapkan privat saat deployment.

### Siapa boleh membaca file privat

Kode mode di tabel ini dipakai saat menulis skrip setup. Owner adalah pemilik file; group adalah kelompok akun yang diizinkan. Mode 0600 berarti hanya owner dapat membaca/menulis. 0640 menambah izin baca bagi group; 0750 untuk folder memberi owner akses penuh dan group akses baca/masuk. 0700 hanya dapat diakses owner.

| Lokasi | Owner:group | Mode |
| --- | --- | --- |
| Folder konfigurasi privat | `root:loglab-svc` | `0750` |
| File env privat | `root:root` | `0600` |
| Private key TLS | `root:loglab-svc` | `0640` |
| Folder data | `loglab-svc:loglab-svc` | `0700` |

Env dibaca systemd sebagai root lalu diteruskan ke proses service. Service berjalan sebagai loglab-svc; ia tidak perlu diberi izin membaca file env root secara langsung.

## OS yang diunduh

Pakai **debian-13.7.0-amd64-netinst.iso**. Ini installer Debian, bukan file VM yang sudah berisi aplikasi.

[Unduh ISO resmi](https://cdimage.debian.org/debian-cd/13.7.0/amd64/iso-cd/debian-13.7.0-amd64-netinst.iso) · [Daftar SHA-256 resmi](https://cdimage.debian.org/debian-cd/13.7.0/amd64/iso-cd/SHA256SUMS)

SHA-256 yang dicatat dari server resmi pada 2026-10-29:

`a7ef94ac2fb9a7fec454552abd629b7cc9d5155c886165a45649f5ce6167e355`

Bandingkan hash file unduhanmu sebelum dipasang. Pada PowerShell: `Get-FileHash debian-13.7.0-amd64-netinst.iso -Algorithm SHA256`. Di Linux: `sha256sum debian-13.7.0-amd64-netinst.iso`. Alat repo juga tersedia: `python3 scripts/check_iso.py /path/ke/debian-13.7.0-amd64-netinst.iso`.

Daftar paket OS dari mirror dapat berubah sesudah installer dibuat. Hash ISO mengunci berkas pemasangan; ia tidak menjamin seluruh OS setelah apt update identik byte demi byte.

## Nilai yang tidak dibagikan di Git

Password dibuat privat, tidak memakai password umum dari panduan. Token pengiriman dibuat sekali untuk satu pasangan lab dan nilainya harus sama pada A/B. Key pseudonim hanya dibutuhkan Source. Private key sertifikat setiap guest berbeda; CA publik harus dipercaya bersama. Contoh env berisi penanda yang harus diganti sebelum menjalankan service, sehingga contoh itu belum bisa dipakai sebagai konfigurasi hidup.

## Saat kamu menulis konfigurasi

Nama LOGLAB di bawah adalah nama yang dibaca kode. Ikuti ejaannya tepat. Bagian ini dapat dilewati jika kamu sedang membaca pembagian tugas, lalu dibuka saat mengerjakan config/setup.

| Nama variabel | Maksudnya |
| --- | --- |
| `LOGLAB_CONTRACT_VERSION` | Versi kontrak konfigurasi |
| `LOGLAB_PORT` | Port HTTPS, dibaca sebagai integer |
| `LOGLAB_SOURCE_ID` | Identitas sumber yang harus sama pada A dan B |
| `LOGLAB_CA_BUNDLE` | CA publik untuk memverifikasi TLS |
| `LOGLAB_TLS_CERT` | Sertifikat milik guest ini |
| `LOGLAB_TLS_KEY` | Private key milik guest ini; isi tidak dibagikan |
| `LOGLAB_ROLE` | Peran proses, bukan nama anggota |
| `LOGLAB_BIND_HOST` | IP privat tempat Uvicorn mendengarkan |
| `LOGLAB_DB_PATH` | Database lokal per peran |
| `LOGLAB_MONITOR_URL` | Origin Monitor tanpa path dan trailing slash |
| `LOGLAB_SENDER_LOCK` | File lock untuk satu sender |
| `LOGLAB_MODEL_PATH` | Paket model numerik; sidecar checksum menambah .sha256 |
| `LOGLAB_OPERATOR_USERNAME` | Akun operator lab, password disiapkan privat |
| `LOGLAB_SOURCE_TOKEN` | Token acak 32 byte hex lowercase, nilai sama di A dan B |
| `LOGLAB_PSEUDONYM_KEY` | Key HMAC 32 byte hex lowercase, hanya diperlukan Source |
| `LOGLAB_OPERATOR_PASSWORD_HASH` | Hash scrypt operator; password mentah tidak masuk env |

## Cara memeriksa

Dari folder repo jalankan `make check-contract`. Alat memastikan JSON, halaman ini, tabel teknis dan contoh env tetap cocok. Jalankan `make test` setelah environment coding dipasang. Untuk memeriksa env privat, ikuti [petunjuk teknis](../docs/interface-contracts/index.md#periksa-sebelum-meminta-review).

Aplikasi Source/Monitor ditulis pada tugas anggota. Lulus pemeriksaan aturan belum berarti aplikasi atau dua VM sudah berfungsi.

[Kembali ke README](../README.md) · [Detail teknis](../docs/interface-contracts/index.md) · [JSON untuk alat](contract.json)
